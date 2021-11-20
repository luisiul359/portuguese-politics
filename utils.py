
import psycopg2
import os


DATABASE_URL = os.environ.get("DATABASE_URL")


def test(input):

    # connect to the PostgreSQL server
    con = psycopg2.connect(DATABASE_URL)
    # create a cursor
    cur = con.cursor()

    create_table_statement = """
    CREATE TABLE IF NOT EXISTS table_test (
        test_attr VARCHAR(255) NOT NULL
    );
    """

    cur.execute(create_table_statement)

    insert_value_statement = """
    INSERT INTO table_test(test_attr)
    VALUES("{}");
    """.format(input)

    cur.execute(insert_value_statement)

    # close the communication with the PostgreSQL
    cur.close()