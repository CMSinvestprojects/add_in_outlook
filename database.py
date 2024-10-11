from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()

username = os.getenv('user')
password = os.getenv('password')
host = os.getenv('host')
db_name = os.getenv('db_name')
db_type = 'mysql'

print(f"criando banco para {username}, banco {db_name}, tipo {db_type}, {host}")

sqlite_path = os.path.join(Path.home(), 'Documents\escreve_banco_bi')
try:
    if db_type == 'mysql':
        engine = create_engine('mysql+pymysql://{}:{}@{}/{}'.format(username, password, host, db_name))

        fundos_engine = create_engine('mysql+pymysql://{}:{}@{}/{}'.format(username, password, host, 'fundos_investimento'))
    elif db_type == 'sqlite':
        engine = create_engine(r'sqlite:///{}\database.db'.format(sqlite_path))


    else:
        raise Exception('banco não suportado {}'.format(db_type))

except KeyError:
    engine = create_engine(r'sqlite:///{}\database.db'.format(Path.cwd()))


