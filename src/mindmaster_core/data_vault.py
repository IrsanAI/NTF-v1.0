"""MindMaster Data Vault skeleton (Phase 0/1).

Design goals:
- AES-256-GCM for bulk record encryption (fast path)
- Hybrid PQC-ready key envelope (classical + post-quantum KEX/signature)
- Crypto-agility policy to switch profiles without rewriting stored records
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Literal

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

CryptoProfile = Literal["legacy", "hybrid", "pqc_strict"]


@dataclass
class VaultPolicy:
    profile: CryptoProfile
    algorithm_version: str = "v1"


class DataVault:
    def __init__(self, base_dir: str = "/data/encrypted", policy: VaultPolicy | None = None) -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        profile = os.getenv("MM_CRYPTO_PROFILE", "hybrid")
        self.policy = policy or VaultPolicy(profile=profile)  # type: ignore[arg-type]

    def _new_dek(self) -> bytes:
        # 32 bytes = AES-256
        return os.urandom(32)

    def _encrypt_with_dek(self, plaintext: bytes, aad: bytes) -> Dict[str, bytes]:
        dek = self._new_dek()
        nonce = os.urandom(12)
        aes = AESGCM(dek)
        ciphertext = aes.encrypt(nonce, plaintext, aad)
        wrapped_dek = self._wrap_dek(dek)
        return {
            "nonce": nonce,
            "ciphertext": ciphertext,
            "wrapped_dek": wrapped_dek,
        }

    def _wrap_dek(self, dek: bytes) -> bytes:
        """Wrap DEK according to crypto profile.

        legacy: classic KMS/KEK path
        hybrid: X25519 + ML-KEM-derived KEK (recommended MVP default)
        pqc_strict: PQC-forward path for selected tenants
        """
        # Placeholder for real KEK derivation / HSM integration.
        # In real implementation this method will:
        # 1) derive shared secret using configured KEX policy
        # 2) HKDF into KEK
        # 3) wrap DEK with AES key-wrap or AES-GCM envelope
        kek = os.urandom(32)
        nonce = os.urandom(12)
        aes = AESGCM(kek)
        return nonce + aes.encrypt(nonce, dek, b"mindmaster-dek-wrap-v1")

    def store_record(self, record_id: str, payload: dict, aad_meta: dict | None = None) -> Path:
        aad = json.dumps(aad_meta or {}, sort_keys=True).encode("utf-8")
        plaintext = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        encrypted = self._encrypt_with_dek(plaintext, aad)

        out = {
            "policy": self.policy.__dict__,
            "aad": (aad_meta or {}),
            "nonce_b64": encrypted["nonce"].hex(),
            "ciphertext_b64": encrypted["ciphertext"].hex(),
            "wrapped_dek_b64": encrypted["wrapped_dek"].hex(),
            "notes": {
                "pqc_hybrid": "Use oqs-python/liboqs for ML-KEM + ML-DSA integration in production.",
                "performance": "Keep AES-256-GCM for bulk data; apply PQC to key/signature path.",
            },
        }

        out_path = self.base_dir / f"{record_id}.json"
        out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
        return out_path


def demo() -> None:
    vault = DataVault(base_dir=os.getenv("MM_VAULT_DIR", "./.mindmaster_vault"))
    path = vault.store_record(
        record_id="sample-chat-001",
        payload={"source": "grok", "content": "NTF compressed state update"},
        aad_meta={"tenant": "local-user", "kind": "chat_message"},
    )
    print(f"stored encrypted record: {path}")


if __name__ == "__main__":
    demo()
