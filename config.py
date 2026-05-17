import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    BASE_URL = os.getenv("BASE_URL", "https://secby.ru")

    ADMIN = {
        "login": os.getenv("ADMIN_LOGIN", "admin"),
        "password": os.getenv("ADMIN_PASSWORD")
    }

    MODERATOR = {
        "login": os.getenv("MODERATOR_LOGIN", "moderator"),
        "password": os.getenv("MODERATOR_PASSWORD")
    }

    TEST_USER = {
        "login": os.getenv("TEST_USER_LOGIN", "user_testapi"),
        "password": os.getenv("TEST_USER_PASSWORD"),
        "email": os.getenv("TEST_USER_EMAIL", "testapi@example.com")
    }