#!/usr/bin/python
import string
import random
import psycopg2

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def get_config(conn):
    '''Insert config of a node into relational db.'''
    node_id = None
    try:
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute("SELECT * from config")
        print("The number of parts: ", cur.rowcount)
        row = cur.fetchone()

        while row is not None:
            print(row)
            row = cur.fetchone()
        row = cur.fetchone()

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def insert_node(conn, hostname, inventory, partition, state, default):
    '''Insert config of a node into relational db.'''
    psql = """INSERT INTO  config (hostname, inventory, partition, state, default_partition)
              VALUES ( %s, %s, %s, %s, %s);"""
    node_id = None
    try:
        cur = conn.cursor()
        cur.execute(psql, (hostname, inventory, partition, state, default,))
        node_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return node_id

def create_tables(conn):
    """ create tables in the PostgreSQL database"""
    command = """
        CREATE TABLE config (
            node_id SERIAL PRIMARY KEY,
            hostname VARCHAR(255),
            inventory VARCHAR(255),
            partition VARCHAR(255),
            state VARCHAR(255),
            default_partition VARCHAR(255))
        """
    try:
        cur = conn.cursor()
        #create table
        cur.execute(command)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def main():
    conn = psycopg2.connect(
        database="slurm_config",
        user = "postgres",
        password = "slurm",
        host = "127.0.0.1",
        port = "5432"
    )
    #table already created now time to insert data
    #create_tables(conn)
    name = id_generator()
    insert_node(conn, name, "intel", "part1", "up", "yes_default")
    #select_config(conn)
if __name__ == "__main__":
    main()
