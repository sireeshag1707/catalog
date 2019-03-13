from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
from Data_Setup import *

engine = create_engine('sqlite:///Gadget.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

# Delete CarsCompanyName if exisitng.
session.query(GadgetCompanyName).delete()
# Delete CarName if exisitng.
session.query(GadgetName).delete()
# Delete User if exisitng.
session.query(User).delete()

# Create sample users data
User1 = User(name="Sireesha Goutham", email="sireeshag1999@gmail.com",
             picture='http://www.enchanting-costarica.com/wp-content/'
             'uploads/2018/02/jcarvaja17-min.jpg')
session.add(User1)
session.commit()
print ("Successfully Add First User")
# Create sample car companys
Cmp1 = GadgetCompanyName(name="Titan",
                         user_id=1)
session.add(Cmp1)
session.commit()

Cmp2 = GadgetCompanyName(name="Samsung",
                         user_id=1)
session.add(Cmp2)
session.commit

Cmp3 = GadgetCompanyName(name="Lenovo",
                         user_id=1)
session.add(Cmp3)
session.commit()

Cmp4 = GadgetCompanyName(name="vivo Y21L",
                         user_id=1)
session.add(Cmp4)
session.commit()

Cmp5 = GadgetCompanyName(name="LED TV",
                         user_id=1)
session.add(Cmp5)
session.commit()

Cmp6 = GadgetCompanyName(name="MOTO E3",
                         user_id=1)
session.add(Cmp6)
session.commit()

# Populare a cars with models for testing
# Using different users for cars names year also
N1 = GadgetName(name="titan watch",
                color="black",
                price="7650",
                Gadgettype="Watch",
                date=datetime.datetime.now(),
                Gadgetcompanynameid=1,
                user_id=1)
session.add(N1)
session.commit()

N2 = GadgetName(name="Ear Phones",
                color="blue",
                price="4,25,000",
                Gadgettype="earphones",
                date=datetime.datetime.now(),
                Gadgetcompanynameid=2,
                user_id=1)
session.add(N2)
session.commit()

N3 = GadgetName(name="Lenovo 16L",
                color="ash",
                price="10,73,650",
                Gadgettype="laptop",
                date=datetime.datetime.now(),
                Gadgetcompanynameid=3,
                user_id=1)
session.add(N3)
session.commit()

N4 = GadgetName(name="Vivo 15Pro",
                color="purple",
                price="90,55,950",
                Gadgettype="phone",
                date=datetime.datetime.now(),
                Gadgetcompanynameid=4,
                user_id=1)
session.add(N4)
session.commit()

N5 = GadgetName(name="LED 3D",
                color="blue",
                price="10,25,650",
                Gadgettype="TV",
                date=datetime.datetime.now(),
                Gadgetcompanynameid=5,
                user_id=1)
session.add(N5)
session.commit()

N6 = GadgetName(name="Moto E5",
                color="white",
                price="11,73,000",
                Gadgettype="phone",
                date=datetime.datetime.now(),
                Gadgetcompanynameid=6,
                user_id=1)
session.add(N6)
session.commit()

print("Your cars database has been inserted!")
