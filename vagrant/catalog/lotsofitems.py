from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, Item

engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# The following code each make a category then fill it with 3 items each
category1 = Category(name="Soccer")

session.add(category1)
session.commit()

item1 = Item(name="Soccer Ball",
             description="Ball for display in the center of the field.",
             category=category1)

session.add(item1)
session.commit()

item2 = Item(name="Shinguards",
             description="Guards your shins without shinning your guards.",
             category=category1)

session.add(item2)
session.commit()

item3 = Item(name="Soccer Cleats",
             description="Soccer cleats. Kid-safe!",
             category=category1)

session.add(item3)
session.commit()


category2 = Category(name="Basketball")

session.add(category2)
session.commit()


item1 = Item(name="Basketball",
             description="Put the game in the basket!",
             category=category2)

session.add(item1)
session.commit()

item2 = Item(name="Jersey",
             description="Proudly identify your favorite team.",
             category=category2)

session.add(item2)
session.commit()

item3 = Item(name="Hoop and Stand",
             description="You can put basketballs into it to earn points.",
             category=category2)

session.add(item3)
session.commit()


category1 = Category(name="Baseball")

session.add(category1)
session.commit()


item1 = Item(name="Baseball",
             description="A ball for use with baseball.",
             category=category1)

session.add(item1)
session.commit()

item2 = Item(name="Baseball bases",
             description="B set of bases to run over and win the game!",
             category=category1)

session.add(item2)
session.commit()

item3 = Item(name="Baseball bat",
             description="Large wooden stick for hitting baseballs.",
             category=category1)

session.add(item3)
session.commit()


print "added new items and categories!"
