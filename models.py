from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(120))
    content: Mapped[str] = mapped_column(Text)
    priority: Mapped[int] = mapped_column(default=1)
    description: Mapped[str | None] = mapped_column(String(250), nullable=True)
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
