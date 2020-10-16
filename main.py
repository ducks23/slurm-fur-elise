#!/usr/bin/python

import psycopg2

def insert_node(conn, hostname, inventory, parition, state, default):
    '''Insert config of a node into relational db.'''
    psql = """INSERT INTO  config (hostname, inventory, parition, state, default)
              VALUES ( %s, %s, %s, %s, %s);"""
    node_id = None
    try:
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(psql, (hostname, inventory, parition, state, default,))
        # get the generated id back
        node_id = cur.fetchone()[0]
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

    return node_id

def create_tables(conn):
    """ create tables in the PostgreSQL database"""
    commands = """
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
        # create table one by one
        cur.execute(commands)
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
        user = "slurm",
        password = "slurm",
        host = "127.0.0.1",
        port = "5432"
    )
    create_tables(conn)
    print("success :)")

if __name__ == "__main__":
    main()
