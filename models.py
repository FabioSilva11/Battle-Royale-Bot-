from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class User:
    group_id: Optional[int]
    user_id: int
    nome: Optional[str]
    sobrenome: Optional[str]
    user_name: Optional[str]
    saldo: int = 100
    roubos: int = 5
    escudo: int = 1
    last_roubo_reset: Optional[str] = None
    recebimentos_data: Optional[str] = None
    recebimentos_hoje: int = 0

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "User":
        return User(
            group_id=data.get("group_id"),
            user_id=int(data.get("user_id")),
            nome=data.get("nome"),
            sobrenome=data.get("sobrenome"),
            user_name=data.get("user_name"),
            saldo=int(data.get("saldo", 0)),
            roubos=int(data.get("roubos", 0)),
            escudo=min(3, max(0, int(data.get("escudo", 0)))),
            last_roubo_reset=data.get("last_roubo_reset"),
            recebimentos_data=data.get("recebimentos_data"),
            recebimentos_hoje=int(data.get("recebimentos_hoje", 0)),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "group_id": self.group_id,
            "user_id": self.user_id,
            "nome": self.nome,
            "sobrenome": self.sobrenome,
            "user_name": self.user_name,
            "saldo": max(0, int(self.saldo)),
            "roubos": max(0, int(self.roubos)),
            "escudo": min(3, max(0, int(self.escudo))),
            "last_roubo_reset": self.last_roubo_reset,
            "recebimentos_data": self.recebimentos_data,
            "recebimentos_hoje": max(0, int(self.recebimentos_hoje)),
        }