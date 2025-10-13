import enum

class StatusType(enum.Enum):
    OFFLINE        = 0
    ONLINE         = 1
    AWAY           = 2
    DO_NOT_DISTURB = 3

class ChannelType(enum.Enum):
    GUILD = 0
    DM    = 1

class MentionType(enum.Enum):
    EVERYONE = 0
    HERE     = 1
    USER     = 2
    CHANNEL  = 3
    ROLE     = 4

class MessageType(enum.Enum):
    TEXT       = 0
    REPLY      = 1
    USER_JOIN  = 2
    USER_LEAVE = 3

type jsonable = dict[str, jsonable] | list[jsonable] | str | int | float | bool | None
type jsondict = dict[str, jsonable]