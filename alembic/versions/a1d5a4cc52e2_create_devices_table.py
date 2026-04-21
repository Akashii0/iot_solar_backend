"""create devices table

Revision ID: a1d5a4cc52e2
Revises: 161b7f7b42f4
Create Date: 2026-03-18 13:01:49.128493

"""

from datetime import datetime
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a1d5a4cc52e2"
down_revision: Union[str, None] = "4acfe5d185fe"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---------- devices table (ESP32 microcontrollers) ----------
    op.create_table(
        "devices",
        sa.Column("id", sa.Integer, primary_key=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False, server_default="ESP32"),
        sa.Column("mac_address", sa.String(20), unique=True, nullable=False),
        sa.Column("firmware_version", sa.String(20)),
        sa.Column(
            "location", sa.String(200), server_default="Living Room"
        ),  # e.g., "Living Room"
        sa.Column("last_seen", sa.DateTime(timezone=True)),  # last reading received
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            onupdate=datetime.now,  # ORM-level; for DB trigger see note below
        ),
    )

    # Index for quick lookups by MAC address (already unique, so index is implicit)
    op.create_index(
        op.f("ix_devices_mac_address"), "devices", ["mac_address"], unique=False
    )


def downgrade() -> None:
    op.drop_table("devices")
