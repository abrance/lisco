from sqlalchemy import Column, Integer, String

from pkg.db.db import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(63), index=True)
    phone = Column(String(31), index=True)
    password = Column(String(63))
    description = Column(String(255))


class Image(Base):
    __tablename__ = "image"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(63), index=True)
    title_type = Column(String(31))
    title = Column(String(63))
    create_user_id = Column(Integer)
    path = Column(String(255))
    description = Column(String(255))


class Instance(Base):
    __tablename__ = "instance"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(63), index=True)
    description = Column(String(255))


class InstanceAttr(Base):
    __tablename__ = "instance_attr"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(63), index=True)
    attr_id = Column(Integer)
    attr_value = Column(String(255))
    instance_id = Column(Integer)


class Quote(Base):
    __tablename__ = "quote"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(63), index=True)
    location = Column(String(255))
    content = Column(String(255))
    create_user_id = Column(Integer)


class QuoteFile(Base):
    __tablename__ = "quote_file"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(63), index=True)
    quote_type = Column(String(31))
    suffix = Column(String(31))
    quote_id = Column(Integer)
    path = Column(String(255))
    urls = Column(String(255))
    description = Column(String(255))
