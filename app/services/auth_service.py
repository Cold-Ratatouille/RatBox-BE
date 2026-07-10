from app.core.security import hash_password
from app.data.repositories.user_repository import create_user, find_user_by_username
from app.domain.models import User


class UsernameTakenError(Exception):
    pass


def signup(username: str, password: str, name: str) -> User:
    if find_user_by_username(username):
        raise UsernameTakenError(f"이미 사용 중인 아이디입니다: {username}")

    row = create_user(username=username, password_hash=hash_password(password), name=name)
    return User(id=row["id"], username=row["username"], name=row["name"])
