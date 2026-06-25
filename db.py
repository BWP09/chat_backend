import sqlmodel as sql, typing, datetime, sqlalchemy
import typedef

class Status(sql.SQLModel, table=True):
    user_id: int = sql.Field(foreign_key="user.id", primary_key=True, sa_type=sqlalchemy.BigInteger)
    type: typedef.StatusType = typedef.StatusType.OFFLINE
    text: typing.Optional[str] = None

    # user: "User" = sql.Relationship(back_populates="status")

class User(sql.SQLModel, table=True):
    id: int = sql.Field(primary_key=True, sa_type=sqlalchemy.BigInteger)
    username: str = sql.Field(unique = True)
    display_name: str
    bio: typing.Optional[str] = None
    password_hash: str

    status: Status = sql.Relationship()
    owned_guilds: list["Guild"] = sql.Relationship(back_populates="owner")
    memberships: list["Member"] = sql.Relationship(back_populates="user")
    channels: list["ChannelParticipant"] = sql.Relationship(back_populates="user")
    tokens: list["AuthToken"] = sql.Relationship(back_populates="user")

class Guild(sql.SQLModel, table=True):
    id: int = sql.Field(primary_key=True, sa_type=sqlalchemy.BigInteger)
    name: str
    description: typing.Optional[str] = None
    owner_id: int = sql.Field(foreign_key="user.id")
    icon_hash: typing.Optional[str] = None

    owner: User = sql.Relationship(back_populates="owned_guilds")
    channels: list["Channel"] = sql.Relationship(back_populates="guild")
    members: list["Member"] = sql.Relationship(back_populates="guild")
    invites: list["Invite"] = sql.Relationship(back_populates="guild")

class Member(sql.SQLModel, table=True):
    user_id: int = sql.Field(foreign_key="user.id", primary_key=True, sa_type=sqlalchemy.BigInteger)
    guild_id: int = sql.Field(foreign_key="guild.id", primary_key=True, sa_type=sqlalchemy.BigInteger)
    invite_id: int = sql.Field(foreign_key="invite.id", sa_type=sqlalchemy.BigInteger)

    timed_out: bool = False
    nickname: typing.Optional[str] = None
    joined_at: datetime.datetime = sql.Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))

    user: User = sql.Relationship(back_populates="memberships")
    guild: Guild = sql.Relationship(back_populates="members")
    invite: "Invite" = sql.Relationship(back_populates="users")

class Channel(sql.SQLModel, table=True):
    id: int = sql.Field(primary_key=True, sa_type=sqlalchemy.BigInteger)
    guild_id: int = sql.Field(foreign_key="guild.id", sa_type=sqlalchemy.BigInteger)
    type: typedef.ChannelType
    name: str

    guild: Guild = sql.Relationship(back_populates="channels")
    participants: list["ChannelParticipant"] = sql.Relationship(back_populates="channel")
    # participants: list["User"] = sql.Relationship(back_populates="channels")

class ChannelParticipant(sql.SQLModel, table=True):
    user_id: int = sql.Field(foreign_key="user.id", primary_key=True, sa_type=sqlalchemy.BigInteger)
    channel_id: int = sql.Field(foreign_key="channel.id", primary_key=True, sa_type=sqlalchemy.BigInteger)

    user: User = sql.Relationship()
    channel: Channel = sql.Relationship(back_populates="participants")

class AuthToken(sql.SQLModel, table=True):
    token_hash: str = sql.Field(primary_key=True)
    user_id: int = sql.Field(foreign_key="user.id", sa_type=sqlalchemy.BigInteger)

    created_at: datetime.datetime = sql.Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    expires_at: datetime.datetime
    deletes_at: datetime.datetime
    revoked: bool = False

    user: User = sql.Relationship(back_populates="tokens")

class Mention(sql.SQLModel, table=True):
    type: typedef.MentionType
    message_id: int = sql.Field(primary_key=True, foreign_key="message.id", sa_type=sqlalchemy.BigInteger)
    user_id: int = sql.Field(foreign_key="user.id", sa_type=sqlalchemy.BigInteger)
    channel_id: int = sql.Field(foreign_key="channel.id", sa_type=sqlalchemy.BigInteger)

    message: "Message" = sql.Relationship(back_populates="mentions")
    user: User = sql.Relationship()
    channel: Channel = sql.Relationship()

class Message(sql.SQLModel, table=True):
    id: int = sql.Field(primary_key=True, sa_type=sqlalchemy.BigInteger)
    type: typedef.MessageType
    channel_id: int = sql.Field(foreign_key="channel.id", sa_type=sqlalchemy.BigInteger)
    author_id: int = sql.Field(foreign_key="user.id", sa_type=sqlalchemy.BigInteger)
    content: str
    edit_timestamp: typing.Optional[datetime.datetime] = None
    pinned: bool = False
    message_reference_id: typing.Optional[int] = sql.Field(foreign_key="message.id", sa_type=sqlalchemy.BigInteger)

    author: User = sql.Relationship()
    mentions: list[Mention] = sql.Relationship(back_populates="message")

class Invite(sql.SQLModel, table=True):
    id: int = sql.Field(primary_key=True, sa_type=sqlalchemy.BigInteger)
    guild_id: int = sql.Field(foreign_key="guild.id", sa_type=sqlalchemy.BigInteger)
    author_id: int = sql.Field(foreign_key="user.id", sa_type=sqlalchemy.BigInteger)

    guild: Guild = sql.Relationship(back_populates="invites")
    author: User = sql.Relationship()
    users: list[Member] = sql.Relationship(back_populates="invite")

class Friendship(sql.SQLModel, table=True):
    from_id: int = sql.Field(primary_key=True, foreign_key="user.id", sa_type=sqlalchemy.BigInteger)
    to_id: int = sql.Field(primary_key=True, foreign_key="user.id", sa_type=sqlalchemy.BigInteger)
    mutual: bool

    from_user: User = sql.Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Friendship.from_id]", "primaryjoin": "Friendship.from_id == User.id"}
    )
    to_user: User = sql.Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Friendship.to_id]", "primaryjoin": "Friendship.to_id == User.id"}
    )