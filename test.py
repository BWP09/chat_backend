import requests as rq

base_url = "http://localhost:5000/api/v1"

def add_guild(token: str):
    data = {
        "name": "zachs playhouse",
        "icon_hash": "1234567890",
        "description": "zachs dungeon",
    }

    r = rq.post(f"{base_url}/guilds", headers = {"Authorization": f"Bearer {token}"}, json = data)
    print(r.status_code)
    print(r.content.decode())
    print()

def get_guild():
    r = rq.get(f"{base_url}/guilds/7342585204759859200")
    print(r.status_code)
    print(r.content.decode())
    print()

def delete_guild():
    r = rq.delete(f"{base_url}/guilds/0")
    print(r.status_code)
    print(r.content.decode())
    print()

def auth_create(username: str, password: str):
    r = rq.post(
        f"{base_url}/auth/create", 
        json = {
            "username": username,
            "password": password,
            "display_name": username.upper(),
            "bio": f"hello im {username}"
        }
    )
    print(r.status_code)
    print(r.content.decode())
    print()

def auth_login(username: str, password: str):
    r = rq.post(
        f"{base_url}/auth/login", 
        json = {"username": username, "password": password}
    )
    print(r.status_code)
    print(r.content.decode())
    print()

# auth_create("testusername", "testpassword")
# auth_login("testusername", "testpassword")
# # add_guild()
# # get_guild()