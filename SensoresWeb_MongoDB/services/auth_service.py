import bcrypt

from repositories.user_repository import (
    UserRepository
)


class AuthService:

    @staticmethod
    def register(nombre, email, password):

        existe = UserRepository.find_by_email(
            email
        )

        if existe:
            return False

        password_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        )

        user_data = {

            "nombre": nombre,

            "email": email,

            "password_hash": password_hash
        }

        UserRepository.create_user(
            user_data
        )

        return True

    @staticmethod
    def login(email, password):

        usuario = UserRepository.find_by_email(
            email
        )

        if not usuario:
            return None

        if bcrypt.checkpw(
            password.encode("utf-8"),
            usuario["password_hash"]
        ):

            return usuario

        return None