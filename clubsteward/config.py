"""Runtime configuration for ClubSteward."""

from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel, Field


class Brand(BaseModel):
    """White-label branding per club (colors, name, tagline)."""

    name: str = "ClubSteward"
    tagline: str = ""
    locale: str = "en"
    colors: dict[str, str] = Field(default_factory=dict)
    logo: str | None = None


class Config(BaseModel):
    api_key: str
    base_url: str
    model_id: str
    data_dir: Path
    max_mails_per_run: int = 20

    @classmethod
    def load(cls, club: str | None = None) -> "Config":
        api_key = os.environ.get("ZAI_API_KEY", "")
        # club modes: 'demo' (default English demo) or a club id under clubs/<id>
        root = Path(__file__).resolve().parent.parent
        if club and club != "demo":
            data_dir = root / "clubs" / club
        else:
            data_dir = Path(os.environ.get("CLUBSTEWARD_DATA", "demo/data")).resolve()
        return cls(
            api_key=api_key,
            base_url=os.environ.get("ZAI_BASE_URL", "https://api.z.ai/api/coding/paas/v4"),
            model_id=os.environ.get("ZAI_MODEL", "glm-5-turbo"),
            data_dir=data_dir,
        )

    @property
    def club_id(self) -> str:
        name = self.data_dir.name
        if name == "data":
            return "demo"
        return name

    @property
    def brand(self) -> Brand:
        p = self.data_dir / "brand.yaml"
        if p.exists():
            try:
                import yaml
                return Brand(**(yaml.safe_load(p.read_text(encoding="utf-8")) or {}))
            except Exception:
                pass
        return Brand()

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
