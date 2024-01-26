from sqlalchemy import create_engine, Column, Integer, String, Sequence, Date, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import text, insert, update, delete
import json
from re import search, IGNORECASE
from datetime import date

TABLENAME = 'people'
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

connection = engine.connect()
metadata = MetaData()

metadata.reflect(bind=engine)

# person1 = Person(first_name='John', last_name='Doe', city='New York', country='USA', birth_date='1990-01-15')
# person2 = Person(first_name='Jane', last_name='Smith', city='London', country='UK', birth_date='1985-03-22')
# session.add_all([person1, person2])
# session.commit()
def row_to_dict(row):
    return row._asdict()

def serialize_date(obj):
    if isinstance(obj, date):
        return obj.isoformat()
    raise TypeError("Type not serializable")


def save_data(filename, rows):
    data = [row_to_dict(row) for row in rows]
    with open(filename, 'w') as wfile:
        json.dump(data, wfile, indent=2, default=serialize_date)
        print("saved")

def show_all(result):
    rows = result.fetchall()
    while True:
        choice = input("Save results? y/n: ")
        if choice.lower() == 'y':
            save_data('data.json', rows)
            break
        elif choice.lower() == 'n':
            if rows:
                print("Result: ")
                for row in rows:
                    print(row)
                break
            else:
                print("No result")
                break
        else:
            print("incorrect action")

def insert_row(table_name):
    
    if table_name in metadata.tables:
        table = metadata.tables[table_name]
        columns = table.columns.keys()
        values = {}
        for column in columns:
            value = input(f"Enter value for column {column}: ")
            values[column] = value
        query = insert(table).values(values)
        try:
            connection.execute(query)
            connection.commit()
        except Exception as e:
            connection.rollback()
            print(f"Error {str(e)}")
    else:
        print("table is not found")

def update_row(table_name):
    if table_name in metadata.tables:
        table = metadata.tables[table_name]
        columns = table.columns.keys()
        print("Available columns for update:")
        for column in columns:
            print(f"{column}")
        condition_column = input("Write column for condition statement: ")
        if condition_column in columns:
            condition_value = input(f"Write 'where' value for column {condition_column}: ")
            values = {}
            for column in columns:
                value = input(f"Enter value for column {column}: ")
                values[column] = value
            
            query = update(table).where(getattr(table.c, condition_column) == condition_value).values(values)

            try:
                connection.execute(query)
                connection.commit()
                print("Successfull update")
            except Exception as e:
                connection.rollback()
                print(f"Error {str(e)}")
        else:
            print("Error: Column does not exists")

def delete_row(table_name):
    if table_name in metadata.tables:
        table = metadata.tables[table_name]
        columns = table.columns.keys()
        print("Available columns for delete:")
        for column in columns:
            print(f"{column}")
        condition_column = input("Write column for condition statement: ")
        if condition_column in columns:
            condition_value = input(f"Write 'where' value for column {condition_column}: ")
            query = delete(table).where(getattr(table.c, condition_column) == condition_value)
            try:
                connection.execute(query)
                connection.commit()
                print("Successfull delete")
            except Exception as e:
                connection.rollback()
                print(f"Error {str(e)}")
        else:
            print("Error: Column does not exists")


while True:
    

    choice = str(input("""
    1. Show all people
    2. Show people by city
    3.Show people by country
    4.Show people by country or city
    5.Insert
    6.Update
    7.Delete
    0.Exit
    ---->  """))

    try:
        if choice == '0':
            break
        elif choice == '1':
            result = session.execute(text(f"select * from {TABLENAME}"))
            show_all(result)
        elif choice == '2':
            city = input("Enter city: ")
            result = session.execute(text(f"select * from {TABLENAME} where city = '{city}'"))
            show_all(result)
        elif choice == '3':
            country = input("Enter country: ")
            result = session.execute(text(f"select * from {TABLENAME} where country = '{country}'"))
            show_all(result)
        elif choice == '4':
            city = input("Enter city: ")
            country = input("Enter country: ")
            result = session.execute(text(f"select * from {TABLENAME} where country = '{country}' OR city = '{city}'"))
            show_all(result)
        elif choice == '5':
            insert_row(TABLENAME)
        elif choice == '6':
            update_row(TABLENAME)
        elif choice == '7':
            delete_row(TABLENAME)


    except Exception as e:
        print(f"Query error: {e}")

session.close()