"""Runtime configuration for ClubKeeper."""

from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel


class Config(BaseModel):
    api_key: str
    base_url: str
    model_id: str
    data_dir: Path
    max_mails_per_run: int = 20

    @classmethod
    def load(cls) -> "Config":
        api_key = os.environ.get("ZAI_API_KEY", "")
        data_dir = Path(os.environ.get("CLUBKEEPER_DATA", "demo/data")).resolve()
        return cls(
            api_key=api_key,
            base_url=os.environ.get("ZAI_BASE_URL", "https://api.z.ai/api/coding/paas/v4"),
            model_id=os.environ.get("ZAI_MODEL", "glm-5-turbo"),
            data_dir=data_dir,
        )

    @property
    def inbox_dir(self) -> Path:
        return self.data_dir / "inbox"

    @property
    def outbox_dir(self) -> Path:
        return self.data_dir / "outbox"

    @property
    def decisions_dir(self) -> Path:
        return self.data_dir / "decisions"

    @property
    def processed_dir(self) -> Path:
        return self.data_dir / "processed"

    @property
    def register_path(self) -> Path:
        return self.data_dir / "register.csv"

    @property
    def log_path(self) -> Path:
        return self.data_dir / "activity.log"
