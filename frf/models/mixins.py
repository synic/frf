import sqlalchemy as sa


class TimestampMixin(object):
    created_at = sa.Column(
        sa.DateTime(timezone=True),
        default=sa.func.current_timestamp(),
        index=True)
    updated_at = sa.Column(
        sa.DateTime(timezone=True),
        index=True,
        default=sa.func.current_timestamp(),
        onupdate=sa.func.current_timestamp())


class ArchiveMixin(object):
    deleted_at = sa.Column(
        sa.DateTime(timezone=True), nullable=True, index=True)
