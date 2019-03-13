import sys
import os
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False)
    picture = Column(String(300))


class GadgetCompanyName(Base):
    __tablename__ = 'Gadgetcompanyname'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref="Gadgetcompanyname")

    @property
    def serialize(self):
        """Return objects data in easily serializeable formats"""
        return {
            'name': self.name,
            'id': self.id
        }


class GadgetName(Base):
    __tablename__ = 'Gadgetname'
    id = Column(Integer, primary_key=True)
    name = Column(String(350), nullable=False)
    color = Column(String(150))
    price = Column(String(10))
    Gadgettype = Column(String(250))
    date = Column(DateTime, nullable=False)
    Gadgetcompanynameid = Column(Integer, ForeignKey('Gadgetcompanyname.id'))
    Gadgetcompanyname = relationship(
        GadgetCompanyName, backref=backref('Gadgetname', 
                                           cascade='all, delete'))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref="Gadgetname")

    @property
    def serialize(self):
        """Return objects data in easily serializeable formats"""
        return {
            'name': self. name,
            'color': self. color,
            'price': self. price,
            'Gadgettype': self. Gadgettype,
            'date': self. date,
            'id': self. id
        }

engin = create_engine('sqlite:///Gadget.db')
Base.metadata.create_all(engin)
