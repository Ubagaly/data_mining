from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, String, Integer, ForeignKey, DATETIME
from sqlalchemy.orm import relationship

Base = declarative_base()

"""
one-to-one
one-to-many - many-to-one
many-to-many
"""


class MixIdUrl:
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, nullable=False, unique=True)


tag_post = Table(
    'tag_post',
    Base.metadata,
    Column('post_id', Integer, ForeignKey('post.id')),
    Column('tag_id', Integer, ForeignKey('tag.id'))
)


class Post(Base, MixIdUrl):
    __tablename__ = 'post'
    title = Column(String, nullable=False)
    image_url = Column(String, nullable=False)
    data_create = Column(DATETIME, nullable=False)
    author_id = Column(Integer, ForeignKey('author.id'))
    author = relationship('Author')
    tags = relationship('Tag', secondary=tag_post)
    comments_id = Column(Integer, ForeignKey('comments.id'))
    comments = relationship('Comments')


class Author(Base, MixIdUrl):
    __tablename__ = 'author'
    name = Column(String, nullable=False)
    posts = relationship('Post')


class Tag(Base, MixIdUrl):
    __tablename__ = 'tag'
    name = Column(String, nullable=False)
    posts = relationship('Post', secondary=tag_post)

class Comments(Base, MixIdUrl):
    __tablename__ = 'comments'
    #id = Column(Integer, primary_key=True, autoincrement=True)
    author_create = Column(String, nullable=False)
    text_post = Column(String, nullable=False)
    post_id = relationship('Post')
