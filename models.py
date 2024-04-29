import uuid
from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String,index=True)
    first_name = Column(String,index=True)
    email= Column(String,index=True)
    contact= Column(String,index=True)
    
    
class Account(Base):
    __tablename__ = 'account'

    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(String, unique=True, index=True)
    account_type=Column(String, index=True, default="savings")
    balance = Column(Float, default=0.0)
    user_id=Column(Integer, ForeignKey('users.id'))

    def __init__(self, **kwargs):
        super(Account, self).__init__(**kwargs)
        self.account_number = str(uuid.uuid4())
    
class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, index=True)
    transaction_type=Column(String, index=True)
    transaction_amount=Column(Float)
    transaction_date=Column(DateTime, nullable=False, server_default=func.now())
    from_account = Column(Integer, ForeignKey('account.id'))
    to_account = Column(Integer, ForeignKey('account.id'))
    sender_account = relationship("Account", foreign_keys=[from_account])
    receiver_account = relationship("Account", foreign_keys=[to_account])