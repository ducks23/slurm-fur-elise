#!/usr/bin/python3
"""SlurmOperator."""
import logging

from interface_mysql import MySQLClient
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
            slurm_info=dict()
        )
        self._mysql = MySQLClient(self, "db")
        event_handler_bindings = {
            self.on.install: self._on_install,
            self._mysql.on.database_available: self._on_db_availabe,
            }
        for event, handler in event_handler_bindings.items():
            self.framework.observe(event, handler)


    def _on_install(self, event):
        # need to install dependencies for psycopg2
        pass
    
    def _on_db_availabe(self, event):
        db = = {
            'db_username': event.db_info.user,
            'db_password': event.db_info.password,
            'db_hostname': event.db_info.host,
            'db_port': event.db_info.port,
            'db_name': event.db_info.database,
        }

    def _on_start(self, event):
        pass

if __name__ == "__main__":
    main(SlurmOperator)
