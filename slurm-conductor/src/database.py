#!/usr/bin/python
import subprocess
try:
    import psycopg2
except ImportError:
    subprocess.call(["apt", "install", "python3-pip", "-y"])
    subprocess.call(["apt-get", "install", "libpq-dev", "-y"])
    subprocess.call(["apt-get", "install", "python-dev", "-y"])
    subprocess.call(["pip3", "install", "psycopg2"])
    subprocess.check_call([
        'apt-get', '--assume-yes', '--option=Dpkg::Options::=--force-confold', 'install',
        'python3-yaml', 'python3-psycopg2',
    ])
    import psycopg2

class Database:
    def __init__(self, user, password, host, port, database):
        self.set_address(user, password, host, port, database)

    def set_address(self, user, password, host, port, database):
        self._user = user
        self._password = password
        self._host = host
        self._port = port
        self._database = database

    def create_slurmctld_table(self):
        """ create tables in the PostgreSQL database"""
        command = """
            CREATE TABLE slurmctld (
                node_id SERIAL PRIMARY KEY,
                hostname VARCHAR(255),
                port VARCHAR(255),
                backup VARCHAR(255))
            """
        try:
            conn = psycopg2.connect(
                database = self.database,
                user = self.user,
                password = self.password,
                host = self.host,
                port = self.port
            )
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
    
    def insert__slurmctld_node(self,  host, backup):
        '''Insert config of a node into relational db.'''
        psql = """INSERT INTO  slurmctld (host, active)
                  VALUES ( %s, %s);"""
        node_id = None
        try:
            conn = psycopg2.connect(
                database = self.database,
                user = self.user,
                password = self.password,
                host = self.host,
                port = self.port
            )
            cur = conn.cursor()
            cur.execute(psql, (host, backup,))
            node_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
        return node_id

    def create_slurmdbd_table(self):
        """ create tables in the PostgreSQL database"""
        command = """
            CREATE TABLE slurmdbd (
                node_id SERIAL PRIMARY KEY,
                hostname VARCHAR(255),
                port VARCHAR(255),
                backup VARCHAR(255))
            """
        try:
            conn = psycopg2.connect(
                database = self.database,
                user = self.user,
                password = self.password,
                host = self.host,
                port = self.port
            )
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

    def insert__slurmdbd_node(self, host, backup):
        '''Insert config of a node into relational db.'''
        psql = """INSERT INTO  slurmdbd (host, active)
                  VALUES ( %s, %s);"""
        node_id = None
        try:
            conn = psycopg2.connect(
                database = self.database,
                user = self.user,
                password = self.password,
                host = self.host,
                port = self.port
            )
            cur = conn.cursor()
            cur.execute(psql, (host, backup,))
            node_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
        return node_id
    
    def create_slurmd_table(self):
        """ create tables in the PostgreSQL database"""
        command = """
            CREATE TABLE slurmd (
                inventory VARCHAR(255),
                partition VARCHAR(255),
                state VARCHAR(255),
                default_partition VARCHAR(255))
            """
        try:
            conn = psycopg2.connect(
                database = self.database,
                user = self.user,
                password = self.password,
                host = self.host,
                port = self.port
            )
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

    def insert__slurmd_node(self,  inventory, partition, state, default):
        '''Insert config of a node into relational db.'''
        psql = """INSERT INTO  slurmd (inventory, partition, state, default_partition)
                  VALUES ( %s, %s, %s, %s, %s);"""
        node_id = None
        try:
            conn = psycopg2.connect(
                database = self.database,
                user = self.user,
                password = self.password,
                host = self.host,
                port = self.port
            )
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
    
