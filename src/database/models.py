import enum
from sqlalchemy import Column, Integer, String, Boolean, func, Table, Date, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DateTime, Date
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(150), nullable=False)
    phone = Column(String(20), nullable=False)
    birthday = Column(Date, nullable=False)
    additional_note = Column(String(150), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    user = relationship("User", backref="contacts", lazy="joined")
    created_at = Column('created_at', DateTime,
                        default=func.now())
    updated_at = Column('updated', DateTime,
                        default=func.now())


class Role(enum.Enum):
    admin: str = "admin"
    moderator: str = "moderator"
    user: str = "user"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    password = Column(String(250), nullable=False)
    email = Column(String(150), nullable=False)
    avatar = Column(String(150), default=func.now())
    refresh_token = Column(String(255), nullable=True)
    created_at = Column('created_at', DateTime, default=func.now())
    role = Column('role', Enum(Role), default=Role.user, nullable=True)
    is_confirmed = Column(Boolean, default=False, nullable=True)
