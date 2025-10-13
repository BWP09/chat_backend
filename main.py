import flask as fl, sqlmodel as sql, sqlalchemy.exc as sql_e, datetime, functools, typing
import snowflake # type: ignore
import typedef, crypt, api, db

def http_error(code: int, context: typing.Optional[str] = None) -> tuple[fl.Response, int]:
    translations = {
        400: "bad request, malformed data",
        401: "unauthorized",
        404: "resource not found",
        405: "method not allowed",
        500: "server error",
    }

    return fl.jsonify({
        "error": translations.get(code, "unknown"),
        "context": context
    }), code

def http_info(context: typing.Optional[str] = None) -> tuple[fl.Response, int]:
    return fl.jsonify({
        "info": "ok",
        "context": context
    }), 200

def token_required[**P, F](f: typing.Callable[P, F]) -> typing.Callable[P, F | fl.Response | tuple[fl.Response, int]]:
    @functools.wraps(f)
    def decorated(*args: P.args, **kwargs: P.kwargs) -> F | fl.Response | tuple[fl.Response, int]:
        with sql.Session(engine) as session:
            auth = fl.request.headers.get("Authorization", "")

            if not auth.startswith("Bearer "):
                return http_error(401, "invalid token")

            token_raw = auth.removeprefix("Bearer ").strip()
            token_hash = crypt.sha256(token_raw)

            auth_token = session.exec(
                sql.select(db.AuthToken).where(db.AuthToken.token_hash == token_hash)
            ).first()

            if auth_token is None:
                return http_error(401, "invalid or expired token")

            if auth_token.deletes_at.timestamp() < datetime.datetime.now(datetime.timezone.utc).timestamp():
                session.delete(auth_token)
                session.commit()

                return http_error(401, "invalid or expired token")

            if auth_token.revoked:
                return http_error(401, "invalid or expired token")
            
            if auth_token.expires_at.timestamp() < datetime.datetime.now(datetime.timezone.utc).timestamp():
                auth_token.revoked = True

                session.add(auth_token)
                session.commit()
                
                return http_error(401, "invalid or expired token")
            
            return f(*args, **kwargs)
    
    return decorated

def get_auth_user(session: sql.Session) -> db.User:
    token_raw = fl.request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    token_hash = crypt.sha256(token_raw)

    auth_token = session.exec(
        sql.select(db.AuthToken).where(db.AuthToken.token_hash == token_hash)
    ).first()

    if auth_token is None:
        raise ValueError("auth token was None")
    
    return auth_token.user

app = fl.Flask(__name__)
sf = snowflake.SnowflakeGenerator(1)

engine = sql.create_engine("sqlite:///database.db", echo=True)
sql.SQLModel.metadata.create_all(engine)

base_url = "/api/v1"

@app.errorhandler(404)
def handle_404(_: Exception | int):
    return http_error(404)

@app.errorhandler(405)
def handle_405(_: Exception | int):
    return http_error(405)

@app.route(f"{base_url}/auth/create", methods = ["POST"])
def route_auth_create():
    with sql.Session(engine) as session:
        json: typedef.jsondict | None = fl.request.json

        if json is None:
            return http_error(400)
        
        username = json.get("username")
        password = json.get("password")
        display_name = json.get("display_name")
        bio = json.get("bio")

        if type(username) != str:
            return http_error(400, "`username` must be a string")
        
        user = session.exec(
            sql.select(db.User).where(db.User.username == username)
        ).first()

        if user is not None:
            return http_error(400, "username is taken")
        
        if type(password) != str:
            return http_error(400, "`password` must be a string")
        
        if type(display_name) != str:
            return http_error(400, "`display_name` must be a string")
        
        if type(bio) != str and bio is not None:
            return http_error(400)

        id = next(sf)

        if id is None:
            return http_error(500, "snowflake generation failed")
        
        api_user = api.User(
            id = id,
            username = username,
            display_name = display_name,
            status = api.Status(typedef.StatusType.OFFLINE),
            bio = bio,
        )

        session.add(
            db.User(
                id = id,
                username = username,
                display_name = display_name,
                bio = bio,
                password_hash = crypt.hash_password(password),
                status = db.Status(
                    user_id = id,
                )
            )
        )

        try:
            session.commit()

        except sql_e.IntegrityError:
            return http_error(500, "INSERT failed integrity check")

        return fl.jsonify(api_user.jsonable())

@app.route(f"{base_url}/auth/login", methods = ["POST"])
def route_auth_login():
    with sql.Session(engine) as session:
        json: typedef.jsondict | None = fl.request.json

        if json is None:
            return http_error(400)
        
        username = json.get("username")
        password = json.get("password")

        if type(username) != str:
            return http_error(400, "`username` must be a string")
        
        if type(password) != str:
            return http_error(400, "`password` must be a string")

        user = session.exec(
            sql.select(db.User).where(db.User.username == username)
        ).first()

        if user is None or not crypt.verify_password(password, user.password_hash):
            return http_error(401, "invalid credentials")
        
        token = crypt.generate_token()
        token_hash = crypt.sha256(token)

        authtoken = db.AuthToken(
            token_hash = token_hash,
            user_id = user.id,
            expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days = 30),
            deletes_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days = 60),
        )

        session.add(authtoken)
        session.commit()

        return {"token": token}

@app.route(f"{base_url}/auth/logout", methods = ["POST"])
@token_required
def route_auth_logout():
    with sql.Session(engine) as session:
        auth_user = get_auth_user(session)
        
        auth_token = session.exec(
            sql.select(db.AuthToken).where(db.AuthToken.user_id == auth_user.id)
        ).first()

        if auth_token is None:
            return http_error(401, "couldn't load auth token")
        
        auth_token.revoked = True
        
        session.add(auth_token)
        session.commit()

        return http_info("token successfully invalidated")

@app.route(f"{base_url}/guilds", methods = ["POST"])
@token_required
def route_all_guilds():
    with sql.Session(engine) as session:
        match fl.request.method:
            case "POST": # Create guild
                auth_user = get_auth_user(session)

                json: typedef.jsondict | None = fl.request.json

                if json is None:
                    return http_error(400)

                id = next(sf)

                if id is None:
                    return http_error(500, "snowflake generation failed")
                  
                name = json.get("name")
                icon_hash = json.get("icon_hash")
                description = json.get("description")

                if type(name) != str:
                    return http_error(400)
                
                if type(icon_hash) != str:
                    return http_error(400)

                if type(description) != str and description is not None:
                    return http_error(400)

                api_guild = api.Guild(
                    id = id,
                    name = name,
                    owner = api.User.from_db(auth_user),
                    icon_hash = icon_hash,
                    description = description,
                )

                session.add(
                    db.Guild(
                        id = id,
                        name = name,
                        owner = auth_user,
                        owner_id = auth_user.id,
                        description = description,
                        icon_hash = icon_hash,
                        members = [db.Member(
                            user_id = auth_user.id,
                            guild_id = id,
                            timed_out = False,
                            joined_at = datetime.datetime.now()
                        )]
                    )
                )

                try:
                    session.commit()

                except sql_e.IntegrityError:
                    return http_error(500, "INSERT failed integrity check")

                return fl.jsonify(api_guild.jsonable())
            
            case _:
                return http_error(405)

@app.route(f"{base_url}/guilds/<int:guild_id>", methods = ["GET", "PATCH", "DELETE"])
@token_required
def route_specific_guild(guild_id: int):
    with sql.Session(engine) as session:
        match fl.request.method:
            case "GET": # Get guild info
                guild = session.exec(
                    sql.select(db.Guild).where(db.Guild.id == guild_id)
                ).first()
                
                if guild is None:
                    return http_error(404, "guild not found")
                
                return fl.jsonify(api.Guild.from_db(guild).jsonable())

            case "PATCH": # Modify guild info
                return f"PATCH: {guild_id}"

            case "DELETE": # Delete guild
                guild = session.exec(
                    sql.select(db.Guild).where(db.Guild.id == guild_id)
                ).first()

                if guild is None:
                    return http_error(404, "guild not found")
                
                user = get_auth_user(session)
                
                if user.id != guild.owner_id:
                    return http_error(403, "only guild owner has delete permission")

                session.delete(guild)
                session.commit()

                return http_info("guild deleted")
            
            case _:
                return http_error(405)
        
@app.route(f"{base_url}/guilds/<int:guild_id>/channels", methods = ["GET", "POST"])
@token_required
def route_all_channels(guild_id: int):
    with sql.Session(engine) as session:
        match fl.request.method:
            case "GET": # Get guild channels
                guild = session.exec(
                    sql.select(db.Guild).where(db.Guild.id == guild_id)
                ).first()
                
                if guild is None:
                    return http_error(404, "guild not found")
                
                return fl.jsonify([api.Channel.from_db(channel).jsonable() for channel in guild.channels])

            case "POST": # Create guild channel
                guild = session.exec(
                    sql.select(db.Guild).where(db.Guild.id == guild_id)
                ).first()
                
                if guild is None:
                    return http_error(404, "guild not found")
                
                json: typedef.jsondict | None = fl.request.json

                if json is None:
                    return http_error(400)

                id = next(sf)

                if id is None:
                    return http_error(500, "snowflake generation failed")
                  
                name = json.get("name")
                description = json.get("description")

                if type(name) != str:
                    return http_error(400)

                if type(description) != str and description is not None:
                    return http_error(400)

                participants = [api.User.from_db(member.user) for member in guild.members]

                api_channel = api.Channel(
                    id = id,
                    type = typedef.ChannelType.GUILD,
                    name = name,
                    participants = participants,
                    guild_id = guild_id,
                )

                session.add(
                    db.Channel(
                        id = id,
                        type = typedef.ChannelType.GUILD,
                        name = name,
                        participants = [db.ChannelParticipant(
                            user_id = participant.id,
                            channel_id = participant.id
                        ) for participant in participants],
                        guild_id = guild_id,
                    )
                )

                try:
                    session.commit()

                except sql_e.IntegrityError:
                    return http_error(500, "INSERT failed integrity check")

                return fl.jsonify(api_channel.jsonable())

            case _:
                return http_error(405)

@app.route(f"{base_url}/channels/<int:channel_id>", methods = ["GET", "PATCH", "DELETE"])
def route_specific_channel(channel_id: int):
    with sql.Session(engine) as session:
        match fl.request.method:
            case "GET": # Get channel info
                channel = session.exec(
                    sql.select(db.Channel).where(db.Channel.id == channel_id)
                ).first()
                
                if channel is None:
                    return http_error(404, "channel not found")
                
                return fl.jsonify(api.Channel.from_db(channel).jsonable())

            case "PATCH": # Modify channel info
                return f"PATCH: {channel_id}"

            case "DELETE": # Delete channel
                return f"DELETE: {channel_id}"
            
            case _:
                return http_error(405)

@app.route(f"{base_url}/channels/<int:channel_id>/messages", methods = ["GET", "POST"])
def route_all_messages(channel_id: int):
    with sql.Session(engine) as session:
        match fl.request.method:
            case "GET": # Get messages
                return "200"

            case "POST": # Send message
                auth_user = get_auth_user(session)

                channel = session.exec(
                    sql.select(db.Channel).where(db.Channel.id == channel_id)
                ).first()
                
                if channel is None:
                    return http_error(404, "channel not found")
                
                json: typedef.jsondict | None = fl.request.json

                if json is None:
                    return http_error(400)

                id = next(sf)

                if id is None:
                    return http_error(500, "snowflake generation failed")
                  
                content = json.get("content")
                message_reference_id = json.get("message_reference_id")

                if type(content) != str:
                    return http_error(400)

                if type(message_reference_id) != int and message_reference_id is not None:
                    return http_error(400)

                message_type = typedef.MessageType.TEXT if message_reference_id is None else typedef.MessageType.REPLY

                api_message = api.Message(
                    id = id,
                    type = message_type,
                    channel_id = channel_id,
                    author = api.User(
                        id = auth_user.id,
                        username = auth_user.username,
                        display_name = auth_user.display_name,
                        status = api.Status(
                            type = auth_user.status.type,
                            text = auth_user.status.text,
                        ),
                        bio = auth_user.bio,
                    ),
                    content = content,
                    message_reference_id = message_reference_id,
                )

                session.add(
                    db.Message(
                        id = id,
                        type = message_type,
                        channel_id = channel_id,
                        author_id = auth_user.id,
                        content = content,
                        message_reference_id = message_reference_id,
                    )
                )

                try:
                    session.commit()

                except sql_e.IntegrityError:
                    return http_error(500, "INSERT failed integrity check")
                
                return fl.jsonify(api_message.jsonable())

            case _:
                return http_error(405)

@app.route(f"{base_url}/channels/<int:channel_id>/messages/<int:message_id>", methods = ["GET", "PATCH"])
def route_specific_message(channel_id: int, message_id: int):
    match fl.request.method:
        case "GET": # Get message
            return "200"

        case "PATCH": # Edit message
            return "200"

        case "DELETE": # Delete channel
            return "200"

        case _:
            return fl.jsonify({
                "error": "method not allowed"
            }), 405

@app.route(f"{base_url}/guilds/<int:guild_id>/members", methods = ["GET"])
def route_all_members(guild_id: int):
    match fl.request.method:
        case "GET": # Get guild members
            return f"GET: {guild_id}"

        case _:
            return http_error(405)

@app.route(f"{base_url}/guilds/<int:guild_id>/members/<int:user_id>", methods = ["GET", "PUT", "PATCH", "DELETE"])
def route_specific_member(guild_id: int, user_id: int):
    match fl.request.method:
        case "GET": # Get guild member
            return f"GET: {user_id}"
        
        case "PUT": # Add guild member
            return f"PUT: {user_id}"

        case "PATCH": # Modify guild member
            return f"PATCH: {user_id}"

        case "DELETE": # Remove guild member
            return f"DELETE: {user_id}"

        case _:
            return http_error(405)
        
@app.route(f"{base_url}/guilds/<int:guild_id>/roles", methods = ["GET", "POST"])
def route_all_roles(guild_id: int):
    match fl.request.method:
        case "GET": # Get guild roles
            return f"GET: {guild_id}"
        
        case "POST": # Create guild role
            return f"POST: {guild_id}"

        case _:
            return http_error(405)

@app.route(f"{base_url}/guilds/<int:guild_id>/roles/<int:role_id>", methods = ["GET", "PATCH", "DELETE"])
def route_specific_role(guild_id: int, role_id: int):
    match fl.request.method:
        case "GET": # Get guild role
            return f"GET: {role_id}"
        
        case "PATCH": # Modify guild role
            return f"PATCH: {role_id}"

        case "DELETE": # Delete guild role
            return f"DELETE: {role_id}"

        case _:
            return http_error(405)
        
@app.route(f"{base_url}/guilds/<int:guild_id>/bans", methods = ["GET"])
def route_all_bans(guild_id: int):
    match fl.request.method:
        case "GET": # Get guild bans
            return f"GET: {guild_id}"

        case _:
            return http_error(405)

@app.route(f"{base_url}/guilds/<int:guild_id>/bans/<int:user_id>", methods = ["GET", "PUT", "DELETE"])
def route_specific_ban(guild_id: int, user_id: int):
    match fl.request.method:
        case "GET": # Get guild ban
            return f"GET: {user_id}"
        
        case "PUT": # Create guild ban
            return f"PUT: {user_id}"

        case "DELETE": # Delete guild ban
            return f"DELETE: {user_id}"

        case _:
            return http_error(405)

@app.route(f"{base_url}/users/<int:user_id>", methods = ["GET", "PUT"])
def route_specific_user(user_id: int):
    with sql.Session(engine) as session:
        match fl.request.method:
            case "GET": # Get user's info
                if user_id == 0:
                    auth_user = get_auth_user(session)
                    user_id = auth_user.id

                user = session.exec(
                    sql.select(db.User).where(db.User.id == user_id)
                ).first()
                
                if user is None:
                    return http_error(404, "user not found")
                
                return fl.jsonify(api.User.from_db(user).jsonable())
            
            case "PUT": # Edit self's info
                return f"PUT: {user_id}"

            case _:
                return http_error(405)

@app.route(f"{base_url}/users/<int:user_id>/guilds", methods = ["GET", "PUT"])
def route_user_guilds(user_id: int):
    with sql.Session(engine) as session:
        match fl.request.method:
            case "GET": # Get user's joined guilds
                if user_id == 0:
                    auth_user = get_auth_user(session)
                    user_id = auth_user.id

                user = session.exec(
                    sql.select(db.User).where(db.User.id == user_id)
                ).first()
                
                if user is None:
                    return http_error(404, "user not found")
                
                return fl.jsonify([api.Guild.from_db(member.guild).jsonable() for member in user.memberships])
            
            case "PUT": # Edit self's info
                return f"PUT: {user_id}"

            case _:
                return http_error(405)

if __name__ == "__main__":
    app.run(port = 8081, debug = True)