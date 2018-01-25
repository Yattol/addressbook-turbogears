from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Unicode, Integer
from rubrica.model import DeclarativeBase, metadata

class Contatto(DeclarativeBase):
    __tablename__ = 'contatto'

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column('name', Unicode(255), nullable=False)
    phone = Column('phone', Unicode(255), nullable=False)
    owner = Column(Integer, ForeignKey('tg_user.user_id'), nullable=False)

