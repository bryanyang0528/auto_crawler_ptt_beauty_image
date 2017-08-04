import os
from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date, Text
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()
DB_connect = os.environ['SQLALCHEMY_DATABASE_URI']


class Images(Base):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True)
    url = Column(String, ForeignKey('articles.url'))
    imgurl = Column(String)

class Articles(Base):
    __tablename__ = 'articles'

    board = Column(String)
    post_date = Column(Date)
    author = Column(String)
    title = Column(String)
    url = Column(String, primary_key=True)
    rate = Column(Integer)
    post_content = Column(Text)
    createdate = Column(DateTime(timezone=True), server_default=func.now())
    images = relationship('Images')
    comments = relationship('Comments')

class Comments(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    commenter = Column(String)
    url = Column(String, ForeignKey('articles.url'))
    content = Column(String)
    rate = Column(Integer)
    comment_date = Column(Date)

if __name__ == '__main__':
    engine = create_engine(DB_connect)
    session = sessionmaker()
    session.configure(bind=engine)
    Base.metadata.create_all(engine)

