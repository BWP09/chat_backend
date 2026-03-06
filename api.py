import typing, json, datetime, requests as rq
import typedef, db

class APIBase:
    def jsonable(self) -> typedef.jsonable:
        """Returns a JSON-compatible representation of the object"""
        return None
    
    def json(self, indent: typing.Optional[int] = None) -> str:
        """Returns the JSON representation of the object"""
        return json.dumps(self.jsonable(), indent = indent)

# class Timestamp(APIBase): 
#     def __init__(
#             self,
#             unix_timestamp_ms: int
#         ) -> None:
        
#         self.unix_timestamp_ms = unix_timestamp_ms
#         self.dt = datetime.datetime.fromtimestamp(self.unix_timestamp_ms / 1000)
    
#     def __repr__(self) -> str:
#         return f"{self.__class__.__name__}(unix_timestamp_ms={self.unix_timestamp_ms})"

#     def jsonable(self) -> typedef.jsonable:
#         return self.unix_timestamp_ms

#     @classmethod
#     def now(cls) -> typing.Self:
#         return cls(int(time.time() * 1000))

#     def fmt(self, format: str) -> str:
#         return self.dt.strftime(util.dt_parse(format))

class Status(APIBase):
    def __init__(
            self,
            type: typedef.StatusType,
            text: typing.Optional[str] = None,
        ) -> None:

        self.type = type
        self.text = text

    def jsonable(self) -> typedef.jsonable:
        return {
            "type": self.type.value,
            "text": self.text,
        }

    @classmethod
    def from_db(cls, db_type: db.Status) -> typing.Self:
        return cls(
            type = db_type.type,
            text = db_type.text,
        )

class User(APIBase):
    def __init__(
            self,
            id: int,
            username: str,
            display_name: str,
            status: Status,
            bio: typing.Optional[str] = None,
        ) -> None:
        
        self.id = id
        self.username = username
        self.display_name = display_name
        self.bio = bio
        self.status = status

    def jsonable(self) -> typedef.jsonable:
        return {
            "id": str(self.id),
            "username": self.username,
            "display_name": self.display_name,
            "bio": self.bio,
            "status": self.status.jsonable(),
        }
    
    @classmethod
    def from_db(cls, db_type: db.User) -> typing.Self:
        return cls(
            id = db_type.id,
            username = db_type.username,
            display_name = db_type.display_name,
            status = Status.from_db(db_type.status),
        )
    

class Channel(APIBase):
    def __init__(
            self,
            id: int,
            type: typedef.ChannelType,
            name: str,
            participants: list[User],
            guild_id: typing.Optional[int] = None,
        ) -> None:
        
        self.id = id
        self.type = type
        self.name = name
        self.participants = participants
        self.guild_id = guild_id
    
    def jsonable(self) -> typedef.jsonable:
        return {
            "id": str(self.id),
            "type": self.type.value,
            "name": self.name,
            "participants": [participant.jsonable() for participant in self.participants],
            "guild_id": self.guild_id,
        }

    @classmethod
    def from_db(cls, db_type: db.Channel) -> typing.Self:
        return cls(
            id = db_type.id,
            type = db_type.type,
            name = db_type.name,
            participants = [User.from_db(participant.user) for participant in db_type.participants],
            guild_id = db_type.guild_id,
        )
    
class Role(APIBase):   
    def __init__(
            self,
            id: int,
            name: str,
            color: int,
            mentionable: bool,
        ) -> None:
        
        self.id = id
        self.name = name
        self.color = color
        self.mentionable = mentionable

    def jsonable(self) -> typedef.jsonable:
        return {
            "id": str(self.id),
            "name": self.name,
            "color": self.color,
            "mentionable": self.mentionable,
        }

class Emoji(APIBase):
    def __init__(
            self,
            id: int,
            name: str,
            image_hash: str,
        ) -> None:
        
        self.id = id
        self.name = name
        self.image_hash = image_hash

    def jsonable(self) -> typedef.jsonable:
        return {
            "id": str(self.id),
            "name": self.name,
            "image_hash": self.image_hash,
        }

class Member(APIBase):
    def __init__(
            self,
            user: User,
            joined_at: datetime.datetime,
            timed_out: bool,
            nickname: typing.Optional[str] = None,
            roles: typing.Optional[list[Role]] = None,
        ) -> None:
        
        self.user = user
        self.joined_at = joined_at
        self.timed_out = timed_out
        self.nickname = nickname
        self.roles = roles

    def jsonable(self) -> typedef.jsonable:
        return {
            "user": self.user.jsonable(),
            "joined_at": self.joined_at.timestamp(),
            "timed_out": self.timed_out,
            "nickname": self.nickname,
            "roles": [role.jsonable() for role in self.roles] if self.roles is not None else None,
        }
    
    @classmethod
    def from_db(cls, db_type: db.Member) -> typing.Self:
        return cls(
            user = User.from_db(db_type.user),
            joined_at = db_type.joined_at,
            timed_out = db_type.timed_out,
            nickname = db_type.nickname
        )

class Ban(APIBase):
    def __init__(
            self,
            user: User,
            reason: typing.Optional[str],
        ) -> None:
        
        self.user = user
        self.reason = reason
    
    def jsonable(self) -> typedef.jsonable:
        return {
            "user": self.user.jsonable(),
            "reason": self.reason,
        }

class Guild(APIBase):
    def __init__(
            self,
            id: int,
            name: str,
            owner: User,
            # members: list[Member],
            # channels: list[Channel],
            icon_hash: typing.Optional[str] = None,
            description: typing.Optional[str] = None,
            roles: typing.Optional[list[Role]] = None,
            emojis: typing.Optional[list[Emoji]] = None,
        ) -> None:
        
        self.id = id
        self.name = name
        self.owner = owner
        # self.members = members
        # self.channels = channels
        self.icon_hash = icon_hash
        self.description = description
        self.roles = roles
        self.emojis = emojis

    def jsonable(self) -> typedef.jsonable:
        return {
            "id": str(self.id),
            "name": self.name,
            "owner": self.owner.jsonable(),
            # "members": [member.jsonable() for member in self.members],
            # "channels": [channel.jsonable() for channel in self.channels],
            "icon_hash": self.icon_hash,
            "description": self.description,
            "roles": [role.jsonable() for role in self.roles] if self.roles is not None else None,
            "emojis": [emoji.jsonable() for emoji in self.emojis] if self.emojis is not None else None,
        }
    
    @classmethod
    def from_db(cls, db_type: db.Guild) -> typing.Self:
        return cls(
            id = db_type.id,
            name = db_type.name,
            owner = User.from_db(db_type.owner),
            icon_hash = db_type.icon_hash,
            description = db_type.description,
        )

class Mention(APIBase):
    def __init__(
            self,
            type: typedef.MentionType,
            user: typing.Optional[User] = None,
            channel: typing.Optional[Channel] = None,
        ) -> None:
        
        self.type = type
        self.user = user
        self.channel = channel
    
    def jsonable(self) -> typedef.jsonable:
        return {
            "type": self.type.value,
            "user": self.user.jsonable() if self.user is not None else None,
            "channel": self.channel.jsonable() if self.channel is not None else None,
        }

# class MessageReference(APIBase):
#     def __init__(
#             self,
#             message_id: int,
#             channel_id: int,
#             guild_id: typing.Optional[int],
#         ) -> None:
        
#         self.message_id = message_id
#         self.channel_id = channel_id
#         self.guild_id = guild_id
    
#     def jsonable(self) -> typedef.jsonable:
#         return {
#             "message_id": self.message_id,
#             "channel_id": self.channel_id,
#             "guild_id": self.guild_id,
#         }

class Message(APIBase):
    def __init__(
            self,
            id: int,
            type: typedef.MessageType,
            channel_id: int,
            author: User,
            content: str,
            pinned: bool = False,
            edit_timestamp: typing.Optional[datetime.datetime] = None,
            mentions: typing.Optional[list[Mention]] = None,
            message_reference_id: typing.Optional[int] = None,
        ) -> None:
        
        self.id = id
        self.type = type
        self.channel_id = channel_id
        self.author = author
        self.content = content
        self.edit_timestamp = edit_timestamp
        self.mentions = mentions
        self.pinned = pinned
        self.message_reference_id = message_reference_id
    
    def jsonable(self) -> typedef.jsonable:
        return {
            "id": str(self.id),
            "type": self.type.value,
            "channel_id": self.channel_id,
            "author": self.author.jsonable(),
            "content": self.content,
            "edit_timestamp": self.edit_timestamp.timestamp() if self.edit_timestamp is not None else None,
            "mentions": [mention.jsonable() for mention in self.mentions] if self.mentions is not None else None,
            "pinned": self.pinned,
            "message_reference_id": self.message_reference_id,
        }

class APIException(Exception):
    ...

class Client:
    def __init__(self, server: str, base_url: str = "/api/v1") -> None:
        self.base_url = f"{server}{base_url}"
        self.token: typing.Optional[str] = None
    
    def __auth_header(self):
        if self.token is None:
            raise ValueError("Please set the token!")
        
        return {"Authorization": f"Bearer {self.token}"}

    def get_token(self, username: str, password: str):
        r = rq.post(f"{self.base_url}/auth/login", json = {"username": username, "password": password})

        if r.status_code != 200:
            print(r.json()["error"])
            return

        print(f"This is your token: \"{r.json()["token"]}\"")
        print("Remove this `get_token` method call now that you have obtained your token.")
        print("Replace it with the following:")
        print("<client instance>.set_token(\"<token>\")")

    def set_token(self, token: str):
        self.token = token

    def revoke_token(self) -> tuple[bool, typedef.jsondict]:
        r = rq.post(f"{self.base_url}/auth/logout", headers = self.__auth_header())

        return r.status_code == 200, r.json()
    
    def auth_create(
            self,
            username: str,
            password: str,
            display_name: str,
            bio: typing.Optional[str] = None,
        ) -> tuple[bool, typedef.jsondict]:
        
        data: typedef.jsonable = {
            "username": username,
            "password": password,
            "display_name": display_name,
            "bio": bio,
        }

        r = rq.post(f"{self.base_url}/auth/create", json = data)

        return r.status_code == 200, r.json()
    
    def create_guild(self, name: str, icon_hash: str, description: str) -> tuple[int, typedef.jsondict]:
        data: typedef.jsonable = {
            "name": name,
            "icon_hash": icon_hash,
            "description": description,
        }

        r = rq.post(f"{self.base_url}/guilds", headers = self.__auth_header(), json = data)

        return r.status_code, r.json()
    
    def get_guild(self, id: int) -> tuple[int, typedef.jsonable]:
        r = rq.get(f"{self.base_url}/guilds/{id}", headers = self.__auth_header())
        
        return r.status_code, r.json()
    
    def get_guilds(self) -> tuple[int, typedef.jsonable]:
        r = rq.get(f"{self.base_url}/guilds", headers = self.__auth_header())
        
        print(r.headers)

        return r.status_code, r.json()
    
    def delete_guild(self, id: int) -> tuple[int, typedef.jsonable]:
        r = rq.delete(f"{self.base_url}/guilds/{id}", headers = self.__auth_header())
        
        return r.status_code, r.json()

    def create_guild_channel(self, guild_id: int, name: str, description: str) -> tuple[int, typedef.jsonable]:
        data: typedef.jsonable = {
            "name": name,
            "description": description,
        }

        r = rq.post(f"{self.base_url}/guilds/{guild_id}/channels", headers = self.__auth_header(), json = data)
        
        return r.status_code, r.json()

    def get_guild_channels(self, guild_id: int) -> tuple[int, typedef.jsonable]:
        r = rq.get(f"{self.base_url}/guilds/{guild_id}/channels", headers = self.__auth_header())
        
        return r.status_code, r.json()
    
    def get_channel(self, id: int) -> tuple[int, typedef.jsonable]:
        r = rq.get(f"{self.base_url}/channels/{id}", headers = self.__auth_header())
        
        return r.status_code, r.json()
