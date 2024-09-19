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
    admin_name = getenv_or_action("API_ADMIN_NAME", action="ignore")
    admin_cpf = getenv_or_action("API_ADMIN_CPF", action="ignore")
    admin_data_source = getenv_or_action("API_ADMIN_DATA_SOURCE", action="ignore")

    await create_any_user(
        username=admin_username,
        password=admin_password,
        is_admin=True,
        name=admin_name,
        cpf=admin_cpf,
        data_source=admin_data_source,
        role="desenvolvedor",
    )

async def create_any_user(
    username: str,
    password: str,
    is_admin: bool,
    name: str = "João da Silva",
    cpf: str = "01234567890",
    data_source: str = "3567508",
    role: str = "convidado",
):
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
            role_id=role,
            data_source_id=data_source,
            name=name,
            cpf=cpf,
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
    parser.add_argument("--name", type=str)
    parser.add_argument("--cpf", type=str)
    parser.add_argument("--data-source", type=str)
    parser.add_argument("--role", type=str)
    parser.add_argument("--is-admin", type=bool, default=False)

    args = parser.parse_args()

    if args.create_admin and (args.username or args.password or args.is_admin):
        raise ValueError("You cannot create an admin user and a regular user at the same time")

    if args.create_admin:
        run_async(create_admin_user())
    else:
        run_async(create_any_user(
            username=args.username,
            password=args.password,
            is_admin=args.is_admin,
            name=args.name,
            cpf=args.cpf,
            data_source=args.data_source,
            role=args.role,
        ))

    logger.info("User is available!")
