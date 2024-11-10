import sqlalchemy as sqa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session\

#Creating a base
Base = declarative_base()

#Create a base template for the database entries
class Account(Base):

    __tablename__ = "Accounts"

    name = sqa.Column("Name", sqa.String, primary_key=True)
    balance = sqa.Column("Balance", sqa.INTEGER)

    #Information we're going to save into the Database
    def __init__(self, name, balance):
        self.name = name
        self.balance = balance

    #How it will be displayed
    def __repr__(self):
        return f"({self.name, self.balance}) "
    
class Access(Base):

    __tablename__ = "Access"

    name = sqa.Column("Name", sqa.String, primary_key=True)
    guildID = sqa.Column("Guild ID", sqa.INTEGER)

    #Information we're going to save into the Database
    def __init__(self, name, guildID):
        self.name = name
        self.guildID = guildID

    #How it will be displayed
    def __repr__(self):
        return f"({self.name, self.guildID}) "

#Creating a database with SQLite named database1.db
engine = sqa.create_engine("sqlite:///AlbionBot.db", echo=True)
Base.metadata.create_all(bind=engine)

#Creating the info/data we want to store
#account = Account("email@gmail.com", "Password123")

mSession = Session(engine)
session = mSession

#Check if the account exists
def CheckAccount(name : str):
    #Query the database for matching credentials
    query = session.query(Account).filter(sqa.and_(Account.name == name)).first()
    if query:
        return query.balance
    else:
        return "Account does not exist!"
    
def CreateAccount(Name : str, Balance : int):
    newAccount = Account(Name, Balance)
    with Session(engine) as session:
        #Actually commiting and saving the info to the database
        session.begin()
        session.add(newAccount)
        session.commit()
        session.close()

def CheckForAccount(name : str):
    query = session.query(Account).filter(Account.name == name).first()
    if query:
        return True
    else:
        return False

    
def AddBalance(Name : str, Balance: int):
    if CheckForAccount(Name):
        query = session.query(Account).filter(Account.name == Name).first()
        oldBal = query.balance
        query.balance += Balance
        session.commit()
        return query.balance, oldBal
    else:
        CreateAccount(Name, Balance)
        return 

def RemoveBalance(Name : str, Balance: int):
    query = session.query(Account).filter(Account.name == Name).first()
    oldBal = query.balance
    query.balance -= Balance
    session.commit()
    return query.balance, oldBal

def addGuild(name : str, guildID : int):
    newAccess = Access(name, guildID)
    with Session(engine) as session:
        #Actually commiting and saving the info to the database
        session.begin()
        session.add(newAccess)
        session.commit()
        session.close()

def CheckForAccess(guildID : int):
    query = session.query(Access).filter(Access.guildID == guildID).first()
    if query:
        return True
    else:
        return False


#Insert data into the database
#def InsertData(account):
    #with Session(engine) as session:
        #Actually commiting and saving the info to the database
        #session.begin()
        #session.add(account)
        #session.commit()
        #session.close()
    return "Balance added"