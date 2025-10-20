import json
from typing import Dict, Optional
from pathlib import Path

from models import User
from config import USERS_FILE


class UserStorage:
    def __init__(self, file_path: Optional[str] = None) -> None:
        self.file_path = Path(file_path or USERS_FILE)

    def load(self) -> Dict[str, dict]:
        if not self.file_path.exists():
            return {}
        try:
            return json.loads(self.file_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}

    def save(self, data: Dict[str, dict]) -> None:
        self.file_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def get(self, user_id: int) -> Optional[User]:
        data = self.load()
        raw = data.get(str(user_id))
        if not raw:
            return None
        return User.from_dict(raw)

    def get_by_username(self, username: str) -> Optional[User]:
        if not username:
            return None
        data = self.load()
        for _, raw in data.items():
            if raw.get("user_name") == username:
                return User.from_dict(raw)
        return None

    def upsert(self, user: User) -> None:
        data = self.load()
        data[str(user.user_id)] = user.to_dict()
        self.save(data)

    def add_if_absent(self, user: User) -> bool:
        data = self.load()
        key = str(user.user_id)
        if key in data:
            return False
        data[key] = user.to_dict()
        self.save(data)
        return True

    def all_users(self) -> Dict[str, User]:
        data = self.load()
        return {k: User.from_dict(v) for k, v in data.items()}