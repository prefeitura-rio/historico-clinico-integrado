# -*- coding: utf-8 -*-
from argparse import ArgumentParser

from loguru import logger
from tortoise import Tortoise, run_async

from app.db import TORTOISE_ORM
from api.app.models.mrg import User
from app.utils import password_hash


async def run(username: str, password: str, is_admin: bool):
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

    await User.create(
        username=username,
        email=f"{username}@example.com",
        password=password_hash(password),
        is_active=True,
        is_superuser=is_admin,
    )
    await Tortoise.close_connections()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--username", type=str, required=True)
    parser.add_argument("--password", type=str, required=True)
    parser.add_argument("--admin", type=bool, default=False)
    args = parser.parse_args()
    run_async(run(args.username, args.password, args.admin))
    logger.info(f"User {args.username} created. Admin: {args.admin}")
