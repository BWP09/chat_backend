import api

client = api.Client("http://localhost:8081")
# client.set_token("nTjT-ps-p7e0k-XJd6bK8H6sbae9-JZK2SCsuXg9SGI")

# success, r = client.auth_create(
#     username = "test",
#     password = "test",
#     display_name = "Test",
#     bio = "this is a test account"
# )

# print(success, r)

# client.get_token(
#     username = "bwp09",
#     password = "password123!",
# )

# success, r = client.revoke_token()
# print(success, r)

# status, json = client.create_guild("tel aviv 2027", "hash", "bibi save us")

# print(status, json)

# status, json = client.get_guild(7382529905558294528)

# print(status, json)

# status, json = client.get_guilds()

# print(status, json)

# status, json = client.get_guild_channels(7382529905558294528)

# print(status, json)

# status, json = client.create_guild_channel(7475279037984673792, "brandon", "bwgut")

# print(status, json)

# status, json = client.get_guild_channels(7382529905558294528)

# print(status, json)

# status, json = client.get_message(7434035811869265920, 7475064746207612928)

# print(status, json)

import os
import result

token = ""

while True:
    inp = input("> ")

    cmd, rest = inp.split(" ", 1)

    match cmd:
        case "exit":
            break

        case "token":
            split = rest.split(" ", 1)

            if len(split) != 1:
                subcmd, rest = split
            
            else:
                subcmd = split[0]

            match subcmd:
                case "get":
                    username, password = rest.split(" ", 1)

                    r = client.get_token(username, password)
                    
                    if (ok := r.ok()) is not None:
                        with open(os.path.join(os.getcwd(), ".token"), "w") as f:
                            f.write(ok)
                        
                        print("token saved to .token")
            
                    else:
                        print(r.err())

                case "load":
                    with open(os.path.join(os.getcwd(), ".token"), "r") as f:
                        token = f.read()

                    print("token loaded from .token")

                    client.set_token(token)
                
                case "print":
                    print(token)
        
        case "participant":
            split = rest.split(" ", 1)

            if len(split) != 1:
                subcmd, rest = split
            
            else:
                subcmd = split[0]

            match subcmd:
                case "add":
                    channel, user = rest.split(" ", 1)

                    r = client.add_participant(int(channel), int(user))

                    print(r)
        
        case "user":
            split = rest.split(" ", 1)

            if len(split) != 1:
                subcmd, rest = split
            
            else:
                subcmd = split[0]

            match subcmd:
                case "get":
                    method, data = rest.split(" ", 1)

                    if method == "id":
                        ...
                    
                    elif method == "username":
                        r = client.query_user_by_username(data)

                        print(r)