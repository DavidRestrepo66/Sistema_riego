from utils.db import (
    usuarios_collection
)


class UserRepository:

    @staticmethod
    def create_user(data):

        return usuarios_collection.insert_one(
            data
        )

    @staticmethod
    def find_by_email(email):

        return usuarios_collection.find_one({
            "email": email
        })