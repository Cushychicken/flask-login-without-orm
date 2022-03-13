from flask_login import UserMixin
from json import load
from typing import Dict, Optional
from werkzeug.security import generate_password_hash, \
        check_password_hash

class User(UserMixin):
    def __init__(self, id: str, username: str, email: str, password: str):
        self.id = id
        self.username = username
        self.email = email
        self.password = generate_password_hash(password)

    @staticmethod
    def get(user_id: str) -> Optional["User"]:
        return users.get(user_id)

    def __str__(self) -> str:
        return f"<Id: {self.id}, Username: {self.username}, Email: {self.email}>"

    def __repr__(self) -> str:
        return self.__str__()

    def verify_password(self, pwd):
        return check_password_hash(self.password, pwd)

def get_users():
    users = {}
    with open("users.json") as file:
        data = load(file)
        for key in data:
            users[key] = User(
                id=key,
                username=data[key]["username"],
                email=data[key]["email"],
                password=generate_password_hash(data[key]["password"]),
            )
    return users

users = get_users()
