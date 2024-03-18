import psycopg2
import environs
from base_parser import BaseParser

env = environs.Env()
env.read_env('.env')

class ParserOnlinerPostgres(BaseParser):
    def connect_to_db(self):
        try:
            connection = psycopg2.connect(
                database=env('DB_NAME'),
                user=env('DB_USER'),
                password=env("DB_PASSWORD"),
                host=env("DB_HOST"),
                port=env("DB_PORT")
            )
        except:
            connection = False

        return connection
    def create_table_db(self, connection):
        if connection:
            cursor = connection.cursor()
            cursor.execute(
                f"""CREATE TABLE IF NOT EXISTS notebook (
                    id serial PRIMARY KEY,
                    url TEXT,
                    notebook_name TEXT,
                    notebook_description TEXT,
                    notebook_price DECIMAL,
                    notebook_all_price_link TEXT,
                    parse_datetime TIMESTAMPTZ NOT NULL,
                    update_datetime TIMESTAMPTZ
                )
                """
            )
            connection.commit()
        else:
            print('ERROR CONNECTION TO DB!')


parser = ParserOnlinerPostgres().run()