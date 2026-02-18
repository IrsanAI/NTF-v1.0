"""MindMaster Connector Orchestrator (Phase 0/1 skeleton).

Responsibilities:
- ToS-safe pulls from provider export channels
- Quiet-mode scheduling to avoid user/session disruption
- Rate limiting + exponential backoff with jitter
- Idempotent ingestion checkpoints
"""

from __future__ import annotations

import argparse
import os
import random
import time
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class ProviderSyncState:
    provider: str
    sync_cursor: Optional[str] = None
    last_hash: Optional[str] = None


class RateLimiter:
    def __init__(self, per_minute: int) -> None:
        self.per_minute = max(1, per_minute)
        self.window_start = time.time()
        self.used = 0

    def acquire(self) -> None:
        now = time.time()
        elapsed = now - self.window_start
        if elapsed >= 60:
            self.window_start = now
            self.used = 0
        if self.used >= self.per_minute:
            sleep_for = max(0.0, 60 - elapsed)
            time.sleep(sleep_for)
            self.window_start = time.time()
            self.used = 0
        self.used += 1


class ConnectorOrchestrator:
    """Skeleton orchestration service.

    Note: only use official exports/legal endpoints according to provider ToS.
    """

    def __init__(self) -> None:
        self.quiet_mode = os.getenv("MM_QUIET_MODE", "true").lower() == "true"
        self.rate_limit = int(os.getenv("MM_RATE_LIMIT_PER_MIN", "30"))
        self.backoff_base_ms = int(os.getenv("MM_BACKOFF_BASE_MS", "500"))
        self.backoff_max_ms = int(os.getenv("MM_BACKOFF_MAX_MS", "8000"))
        self.allowlist = [x.strip() for x in os.getenv("MM_PROVIDER_ALLOWLIST", "grok").split(",") if x.strip()]
        self.ratelimiter = RateLimiter(self.rate_limit)
        self.state: Dict[str, ProviderSyncState] = {
            p: ProviderSyncState(provider=p) for p in self.allowlist
        }

    def should_pull_now(self) -> bool:
        if not self.quiet_mode:
            return True
        current_hour = time.localtime().tm_hour
        # Quiet mode policy (simple default): run pulls outside typical interaction peaks.
        return current_hour < 8 or current_hour > 20

    def backoff_sleep(self, attempt: int) -> None:
        exp_ms = min(self.backoff_max_ms, self.backoff_base_ms * (2 ** attempt))
        jitter = random.randint(0, 250)
        time.sleep((exp_ms + jitter) / 1000)

    def pull_provider(self, provider: str) -> bool:
        """Simulate one pull from a provider export channel.

        Idempotency strategy:
        - maintain sync_cursor per provider
        - skip already seen content_hash/message_uid pairs
        """
        self.ratelimiter.acquire()
        print(f"[orchestrator] pull provider={provider} tos_mode=official_export_only")
        # TODO: implement adapter call + signed payload verification.
        return True

    def run_once(self) -> int:
        if not self.should_pull_now():
            print("[orchestrator] quiet-mode active: skipping pull window")
            return 0

        failures = 0
        for provider in self.allowlist:
            ok = False
            for attempt in range(3):
                try:
                    ok = self.pull_provider(provider)
                    if ok:
                        break
                except Exception as exc:  # keep loop resilient in worker mode
                    print(f"[orchestrator] provider={provider} attempt={attempt} err={exc}")
                    self.backoff_sleep(attempt)
            if not ok:
                failures += 1
        return failures

    def worker_loop(self) -> None:
        print("[orchestrator] worker loop started")
        while True:
            failures = self.run_once()
            interval = 300 if failures == 0 else 120
            time.sleep(interval)


def main() -> None:
    parser = argparse.ArgumentParser(description="MindMaster connector orchestrator")
    parser.add_argument("--worker-loop", action="store_true", help="run continuous sync loop")
    args = parser.parse_args()

    orchestrator = ConnectorOrchestrator()
    if args.worker_loop:
        orchestrator.worker_loop()
    else:
        failures = orchestrator.run_once()
        raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
