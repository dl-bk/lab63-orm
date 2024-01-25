from sqlalchemy import create_engine, Column, Integer, String, Sequence, Date
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import text
import json
from re import search, IGNORECASE
# Зчитування конфігураційних даних з файлу
with open('config.json') as f:
    config = json.load(f)

# Отримання логіну та паролю з об'єкта конфігурації
db_user = config['database']['user']
db_password = config['database']['password']

db_url = f'postgresql+psycopg2://{db_user}:{db_password}@localhost:5432/People'
engine = create_engine(db_url)

#оголошення базового класу
Base = declarative_base()
#визначення класу моделі
class Person(Base):
    __tablename__ = 'people'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    city = Column(String(50))
    country = Column(String(50))
    birth_date = Column(Date)



#створення таблиці
Base.metadata.create_all(engine)

#створення сесії та додавання запису
Session = sessionmaker(bind=engine)
session = Session()

# person1 = Person(first_name='John', last_name='Doe', city='New York', country='USA', birth_date='1990-01-15')
# person2 = Person(first_name='Jane', last_name='Smith', city='London', country='UK', birth_date='1985-03-22')
# session.add_all([person1, person2])
# session.commit()

def show_all(result):
    rows = result.fetchall()
    if rows:
        print("Result: ")
        for row in rows:
            print(row)
    else:
        print("No result")
    
while True:
    

    choice = str(input("""
    1. Show all people
    2. Show people by city
    3.Show people by country
    0.Exit
    ---->  """))

    try:
        if choice == '0':
            break
        elif choice == '1':
            result = session.execute(text("select * from people"))
            show_all(result)
        elif choice == '2':
            city = input("Enter city: ")
            result = session.execute(text(f"select * from people where city = '{city}'"))
            show_all(result)
        elif choice == '3':
            country = input("Enter country: ")
            result = session.execute(text(f"select * from people where country = '{country}'"))
            show_all(result)
       

    except Exception as e:
        print(f"Query error: {e}")

session.close()