import base64
import json
import urllib.request
import urllib.error
from typing import Tuple, Optional

from models import User
from config import MERCADO_PAGO_ACCESS_TOKEN

API_BASE = "https://api.mercadopago.com"


class PaymentService:
    def __init__(self) -> None:
        self.token = MERCADO_PAGO_ACCESS_TOKEN

    def _headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }

    def create_pix_payment(self, amount: int, user: User) -> Tuple[str, str, Optional[bytes]]:
        if amount <= 0:
            return "", "Informe um valor positivo para comprar saldo.", None
        if not self.token:
            return "", "Configuração ausente: defina MERCADO_PAGO_ACCESS_TOKEN.", None
        payload = {
            "transaction_amount": float(amount),
            "description": f"Compra de saldo Battle Royale — @{user.user_name or user.user_id}",
            "payment_method_id": "pix",
            "payer": {
                # email opcional, pode ser qualquer placeholder
                "email": f"{user.user_id}@example.com",
                "first_name": user.nome or user.user_name or str(user.user_id),
            },
        }
        req = urllib.request.Request(
            f"{API_BASE}/v1/payments",
            data=json.dumps(payload).encode("utf-8"),
            headers=self._headers(),
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            try:
                err = e.read().decode("utf-8")
            except Exception:
                err = str(e)
            return "", f"Erro ao criar pagamento PIX: {err}", None
        except Exception as e:
            return "", f"Erro ao criar pagamento PIX: {e}", None

        payment_id = str(data.get("id", ""))
        tx_data = (
            data.get("point_of_interaction", {})
            .get("transaction_data", {})
        )
        qr = tx_data.get("qr_code")
        qr_b64 = tx_data.get("qr_code_base64")
        ticket_url = tx_data.get("ticket_url")

        info_lines = [
            f"Pagamento PIX criado (ID: {payment_id})",
            f"Valor: {amount}",
        ]
        if qr:
            info_lines.append(f"Chave/QR PIX: {qr}")
        if ticket_url:
            info_lines.append(f"Comprovante: {ticket_url}")
        info_lines.append("Use /verificar_pagamento <payment_id> para creditar após aprovação.")
        img_bytes = None
        if qr_b64:
            try:
                img_bytes = base64.b64decode(qr_b64)
            except Exception:
                img_bytes = None
        return payment_id, "\n".join(info_lines), img_bytes

    def check_payment_status(self, payment_id: str) -> Tuple[str, bool, int]:
        """
        Retorna (status, aprovado_e_nao_debitado_local, amount)
        """
        if not payment_id:
            return "invalid", False, 0
        if not self.token:
            return "config_missing", False, 0
        req = urllib.request.Request(
            f"{API_BASE}/v1/payments/{payment_id}",
            headers=self._headers(),
            method="GET",
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            try:
                err = e.read().decode("utf-8")
            except Exception:
                err = str(e)
            return f"error: {err}", False, 0
        except Exception as e:
            return f"error: {e}", False, 0

        status = data.get("status", "unknown")
        amount = int(float(data.get("transaction_amount", 0)))
        approved = status == "approved"
        # Aqui não mantemos controle de "já creditado". O handler decide creditar uma vez.
        return status, approved, amount