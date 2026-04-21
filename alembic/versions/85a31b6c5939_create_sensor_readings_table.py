"""create sensor_readings table

Revision ID: 85a31b6c5939
Revises: a1d5a4cc52e2
Create Date: 2026-03-18 13:06:14.823380

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "85a31b6c5939"
down_revision: Union[str, None] = "a1d5a4cc52e2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---------- sensor_readings table ----------
    op.create_table(
        "sensor_readings",
        sa.Column(
            "id", sa.BigInteger, primary_key=True, autoincrement=True, nullable=False
        ),
        sa.Column(
            "device_id",
            sa.Integer,
            sa.ForeignKey("devices.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "appliance_name",
            sa.String(50),
            nullable=True,
        ),
        sa.Column("current", sa.Numeric(5, 2)),  # amperes, up to 999.99
        sa.Column("voltage", sa.Numeric(5, 2)),  # volts, up to 999.99
        sa.Column("temperature", sa.Numeric(5, 2)),  # volts, up to 999.99
        sa.Column("humidity", sa.Numeric(5, 2)),  # volts, up to 999.99
        sa.Column("light_lux", sa.Numeric(7, 2)),  # volts, up to 99999.99
        sa.Column(
            "recorded_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
            index=True,  # often filtered by time
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        # No updated_at here – readings are immutable once inserted
    )

    # Composite index for device + time range queries (very common)
    op.create_index(
        "ix_sensor_readings_device_recorded",
        "sensor_readings",
        ["device_id", "recorded_at"],
    )


def downgrade() -> None:
    op.drop_table("sensor_readings")
