import api

client = api.Client("http://localhost:8081")
client.set_token("bEiTr9Ugp-aBt71-8sagbq_PkBai6MlXlxO4av6stkA")

# success, r = client.auth_create(
#     username = "bwp09",
#     password = "password123!",
#     display_name = "BWP09",
#     bio = "bw"
# )

# print(success, r)

# client.get_token(
#     username = "bwp09",
#     password = "password123!",
# )

# success, r = client.revoke_token()
# print(success, r)

# status, json = client.create_guild("Test Guild", "hash", "this is a guild for testing the API")

# print(status, json)

# status, json = client.get_guild(7382529905558294528)

# print(status, json)

# status, json = client.get_guilds()

# print(status, json)

# status, json = client.get_guild_channels(7382529905558294528)

# print(status, json)

status, json = client.create_guild_channel(7434031026608803840, "general", "general channel")

print(status, json)

# status, json = client.get_guild_channels(7382529905558294528)

# print(status, json)