import api

client = api.Client("http://localhost:8081")
client.set_token("2ljy0LtPwOZlnj0zgoRCa_yVYv8_gp5kgtKirKw-wlQ")

# success, r = client.auth_create(
#     username = "bwp09",
#     password = "password123!",
#     display_name = "BWP09",
#     bio = "bw"
# )

# print(success, r)

# client.get_token(
#     username = "username",
#     password = "password",
# )

# success, r = client.revoke_token()
# print(success, r)

# status, json = client.create_guild("Test Guild", "hash", "this is a guild for testing the API")

# print(status, json)

# status, json = client.get_guild(7382529905558294528)

# print(status, json)

status, json = client.get_guild_channels(7382529905558294528)

print(status, json)

status, json = client.create_guild_channel(7382529905558294528, "general", "general channel")

print(status, json)

status, json = client.get_guild_channels(7382529905558294528)

print(status, json)