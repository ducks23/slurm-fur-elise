#!/usr/bin/python3
"""SlurmOperator."""
import logging
import subprocess
import pscopg2

from database import Database
from interface_mysql import MySQLClient
from interface_slurmd import Slurmd
from ops.charm import CharmBase
from ops.framework import StoredState
from ops.main import main
from ops.model import (
    ActiveStatus,
    BlockedStatus,
    ModelError,
    WaitingStatus,
)


logger = logging.getLogger()

class Database:
    def __init__(self, user, password, host, port, database):
        self.set_address(user, password, host, port, database)

    def set_address(self, user, password, host, port, database):
        self._user = user
        self._password = password
        self._host = host
        self._port = port
        self._database = database

    def create_table(self):
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
    
    def insert_node(self, hostname, inventory, partition, state, default):
        '''Insert config of a node into relational db.'''
        psql = """INSERT INTO  config (hostname, inventory, partition, state, default_partition)
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


class SlurmOperator(CharmBase):
    """SlurmOperator."""

    _stored = StoredState()

    def __init__(self, *args):
        """Initialize charm."""
        super().__init__(*args)

        self._stored.set_default(
            slurm_info=dict(),
            psql_creds=None,
            user=None,
            password=None,
            host=None,
            port=None,
            database=None,
        )

        self._mysql = MySQLClient(self, "db")
        self._slurmd = Slurmd(self, "slurmd")

        event_handler_bindings = {
            self.on.install: self._on_install,
            self.mysql.on.database_available: self._on_db_availabe,
            self._slurmd.on.slurmd_available: self._on_slurmd_available,
            }

        for event, handler in event_handler_bindings.items():
            self.framework.observe(event, handler)


    def _on_install(self, event):
        subprocess.call(["apt-get", "install", "libpq-dev"])
        subprocess.call(["apt-get", "install", "python-dev"])
        subprocess.call(["pip3", "install", "psycopg2"])

    def _on_db_availabe(self, event):
        self._stored.user = event.db_info.user
        self._stored.password = event.db_info.password
        self._stored.host = event.db_info.host
        self._stored.port = event.db_info.port
        self._stored.database = event.db_info.database
        db = Database(
            self._stored.user,
            self._stored.password,
            self._stored.host,
            self._stored.port,
            self._stored.database
        )
        db.create_table()

    def _on_slurmd_available(self, event):
        host = event.slurmd_info.host
        db = Database(
            self._stored.user,
            self._stored.password,
            self._stored.host,
            self._stored.port,
            self._stored.database
        )
        db.insert_node(
            event.slurmd_info.hostname,
            event.slurmd_info.inventory,
            event.slurmd_info.partition,
            event.slurmd_info.state,
            event.slurmd_info.default,
        )


if __name__ == "__main__":
    main(SlurmOperator)
