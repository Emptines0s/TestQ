from sqlalchemy import Column, ForeignKey, PrimaryKeyConstraint, Integer, String, DateTime,\
    Table, Boolean, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func


Base = declarative_base()


class UserTest(Base):
    __tablename__ = 'user_test'

    id = Column(Integer)
    user_id = Column(ForeignKey('user.user_id'))
    test_id = Column(ForeignKey('test.test_id'))
    result = Column(String)
    datetime = Column(DateTime, server_default=func.now())
    test = relationship('Test', back_populates='users')

    __table_args__ = (
        PrimaryKeyConstraint('id', name='user_test_pk'),
    )


class User(Base):
    __tablename__ = 'user'

    user_id = Column(Integer)
    user_login = Column(String)
    user_password = Column(String)
    user_level = Column(String)
    tests = relationship('UserTest', backref='user', cascade="all, delete-orphan")

    __table_args__ = (
        PrimaryKeyConstraint('user_id', name='user_pk'),
    )


test_question = Table('test_question', Base.metadata,
                      Column('test_id', ForeignKey('test.test_id')),
                      Column('question_id', ForeignKey('question.question_id'))
                      )


class Test(Base):
    __tablename__ = 'test'

    test_id = Column(Integer)
    test_name = Column(String)
    test_description = Column(String)
    test_question_count = Column(Integer)
    questions = relationship('Question',
                             secondary=test_question,
                             backref='tests')
    users = relationship('UserTest', back_populates='test', cascade="all, delete-orphan")

    __table_args__ = (
        PrimaryKeyConstraint('test_id', name='test_pk'),
    )


class Question(Base):
    __tablename__ = 'question'

    question_id = Column(Integer)
    question_name = Column(String)
    question_description = Column(String)
    answers = relationship('Answer', cascade="all, delete-orphan")

    __table_args__ = (
        PrimaryKeyConstraint('question_id', name='question_pk'),
    )


class Answer(Base):
    __tablename__ = 'answer'

    answer_id = Column(Integer)
    answer_content = Column(String)
    is_correct = Column(Boolean)
    question_id = Column(Integer)

    __table_args__ = (
        PrimaryKeyConstraint('answer_id', name='answer_pk'),
        ForeignKeyConstraint(['question_id'], ['question.question_id'])
    )