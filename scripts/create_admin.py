"""Create an admin account, or promote an existing one, from the command line.

A fresh install has no users, and the sign-up page needs an invitation that
only an admin can issue. This makes that first admin. The account is marked as
email-verified; when no email is configured, two-factor login is also switched
off for it, since the login code could never arrive.

Runs inside the backend container, which mounts this directory at /opt/kit:

    docker compose exec backend python /opt/kit/create_admin.py you@example.org Ada
"""

import argparse
import getpass
import sys

sys.path.insert(0, "/app")

from sqlalchemy import select, update  # noqa: E402

from app.db.tables import UserTable  # noqa: E402
from app.dependencies import get_db  # noqa: E402
from app.schemas.users import UserCreate  # noqa: E402
from app.settings import app_settings  # noqa: E402
from app.types import Scope  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or promote an admin.")
    parser.add_argument("email")
    parser.add_argument("first_name")
    parser.add_argument("--last-name")
    args = parser.parse_args()

    db = next(get_db())
    session = db.users.session

    existing = session.scalar(select(UserTable).where(UserTable.email == args.email))
    if existing is None:
        password = getpass.getpass("Password (min. 8 characters): ")
        if len(password) < 8:
            sys.exit("error: password must be at least 8 characters")
        if getpass.getpass("Repeat password: ") != password:
            sys.exit("error: passwords do not match")
        user_id = db.users.create_user(
            UserCreate(
                email=args.email,
                first_name=args.first_name,
                last_name=args.last_name,
                password=password,
                invite_token=None,
                scope=Scope.ADMIN,
            )
        ).id
        print(f"Created admin {args.email}")
    else:
        user_id = existing.id
        print(f"{args.email} exists, promoting to admin")

    values = {"scope": Scope.ADMIN, "email_verified": True}
    if app_settings.services.email is None:
        values["two_factor_enabled"] = False
        print("No email configured: two-factor login disabled for this account")
    session.execute(update(UserTable).where(UserTable.id == user_id).values(**values))
    session.commit()


if __name__ == "__main__":
    main()
