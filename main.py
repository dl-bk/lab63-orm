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

def check_query(query):
    if not search(r'\bpeople\b', query, IGNORECASE):
        raise Exception(f"Incorrect table name. Name must be 'people'")
    
    if search(r'\bupdate\b', query, IGNORECASE) or search(r'\bdelete\b', query, IGNORECASE):
        if not search(r'\bwhere\b', query, IGNORECASE):
            raise Exception("Update or Delete query must contain 'Where' statement")

#створення таблиці
Base.metadata.create_all(engine)

#створення сесії та додавання запису
Session = sessionmaker(bind=engine)
session = Session()

# person1 = Person(first_name='John', last_name='Doe', city='New York', country='USA', birth_date='1990-01-15')
# person2 = Person(first_name='Jane', last_name='Smith', city='London', country='UK', birth_date='1985-03-22')
# session.add_all([person1, person2])
# session.commit()



while True:
    user_query = input("Enter query or 'exit' to exit: ")
    if user_query.lower() == 'exit':
        break

    try:
        check_query(user_query)
        result = session.execute(text(user_query))
        rows = result.fetchall()
        if rows:
            print("Result: ")
            for row in rows:
                print(row)
        else:
            print("No result")
    except Exception as e:
        print(f"Query error: {e}")

session.close()