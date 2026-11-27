import unittest

from fastapi.security import OAuth2PasswordRequestForm
from ..main import app
from ..database import SessionLocal
from ..routers.user import delete_user
from ..routers import user
from .. import oauth2, schemas


u = schemas.User(
    role="student",
    login="aa@mail.ru",
    first_name="pa",
    last_name="la",
    middle_name="fa",
    password_hash="lala",
    status="active",
)


class test_oauth2(unittest.TestCase):
    def get_db(self):
        return SessionLocal()

    #
    # def test_get_user(self):
    #     user = oauth2.get_user("string", self.get_db())
    #     print("get_test: ", user)
    #
    # def test_create_user(self):
    #     us = schemas.CreateUser(
    #         role="student",
    #         login="abob@mail.ru",
    #         first_name="The punisher",
    #         last_name="The ONLY ONE",
    #         middle_name="deho_o",
    #         password="bmw_exchange_accident_aurora_sorokin",
    #     )
    #     res = user.create_user(us, self.get_db())
    #     print("create_test: ", res)

    # def test_delete_user(self):
    #     login = "abob@mail.ru"
    #     res = user.delete_user(login, self.get_db())
    #     print("delete_test: ", res)


class test_oauth2_async(unittest.IsolatedAsyncioTestCase):
    def get_db(self):
        return SessionLocal()

    # async def test_login(self):
    #     form = OAuth2PasswordRequestForm(
    #         username="abob@mail.ru", password="bmw_exchange_accident_aurora_sorokin"
    #     )
    #     token = await user.login(form, self.get_db())
    #     print("token: ", token)

    async def test_get_user_from_token(self):
        form = OAuth2PasswordRequestForm(
            username="abob@mail.ru", password="bmw_exchange_accident_aurora_sorokin"
        )
        token = await user.login(form, self.get_db())
        usaa = await oauth2.get_current_user(token.access_token, self.get_db())
        print(usaa.model_dump())
