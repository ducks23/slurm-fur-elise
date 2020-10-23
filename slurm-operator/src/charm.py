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
        self._slurmdbd = Slurmdbd(self, "slurmdbd")
        self._slurmctld = Slurmctld(self, "slurmctld")

        event_handler_bindings = {
            self.on.install: self._on_install,
            self.mysql.on.database_available: self._on_db_availabe,
            self._slurmd.on.slurmd_available: self._on_slurmd_available,
            self._slurmdbd.on.slurmdbd_available: self._on_slurmdbd_available,
            self._slurmctld.on.slurmctld_available: 
            self._on_slurmctld_available,
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
        db.create_slurmd_table()
        db.create_slurmdbd_table()
        db.create_slurmctld_table()

    def _on_slurmd_available(self, event):
        slurmd_db = Database(
            self._stored.user,
            self._stored.password,
            self._stored.host,
            self._stored.port,
            self._stored.database
        )
        slurmd_db.insert_node(
            event.slurmd_info.inventory,
            event.slurmd_info.partition,
            event.slurmd_info.state,
        )

    def _on_slurmdbd_available(self, event):
        slurmdbd_db = Database(
            self._stored.user,
            self._stored.password,
            self._stored.host,
            self._stored.port,
            self._stored.database
        )
        slurmdbd_db.insert_slurmdbd_node(
            event.slurmdbd_info.host,
        )

    def _on_slurmctld_available(self, event):
        slurmctld_db = Database(
            self._stored.user,
            self._stored.password,
            self._stored.host,
            self._stored.port,
            self._stored.database
        )
        slurmcltd_db.insert_slurmctld_node(
            event.slurmctld_info.host,
        )

    def _assebmle_send_config(self, event):
        slurm_db = Database(
            self._stored.user,
            self._stored.password,
            self._stored.host,
            self._stored.port,
            self._stored.database
        )
        config = slurm_db.get_config()
        self._slurmctld.send(
            config,
        )
        self._slurmd.send(
            config,
        )


if __name__ == "__main__":
    main(SlurmOperator)
