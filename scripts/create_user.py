# -*- coding: utf-8 -*-
from argparse import ArgumentParser

from loguru import logger
from tortoise import Tortoise, run_async

from app.config import getenv_or_action
from app.db import TORTOISE_ORM
from app.models import User
from app.utils import password_hash


async def create_admin_user():
    """
    Creates an admin user using the provided environment variables for the username and password.
    """
    admin_username = getenv_or_action("API_ADMIN_USERNAME", action="ignore")
    admin_password = getenv_or_action("API_ADMIN_PASSWORD", action="ignore")

    await create_any_user(admin_username, admin_password, True)

async def create_any_user(username: str, password: str, is_admin: bool):
    """
    Creates a user with the given username, password, and admin status.

    Args:
        username (str): The username of the user.
        password (str): The password of the user.
        is_admin (bool): A flag indicating whether the user is an admin.

    Returns:
        None
    """
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

    user = await User.get_or_none(username=username)

    if user is None:
        await User.create(
            username=username,
            email=f"{username}@example.com",
            password=password_hash(password),
            is_active=True,
            is_superuser=is_admin,
        )
        logger.info("User created")
    else:
        logger.info("User already exist")

    await Tortoise.close_connections()


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("--create-admin", action="store_true")

    parser.add_argument("--username", type=str)
    parser.add_argument("--password", type=str)
    parser.add_argument("--is-admin", type=bool, default=False)

    args = parser.parse_args()

    if args.create_admin and (args.username or args.password or args.is_admin):
        raise ValueError("You cannot create an admin user and a regular user at the same time")

    if args.create_admin:
        run_async(create_admin_user())
    else:
        run_async(create_any_user(args.username, args.password, args.is_admin))

    logger.info("User is available!")
