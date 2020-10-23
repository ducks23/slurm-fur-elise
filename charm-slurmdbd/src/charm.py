#!/usr/bin/python3
"""Slurmdbd Charm."""
import socket
from interface_mysql import MySQLClient
from ops.charm import CharmBase
from ops.framework import StoredState
from ops.main import main
from ops.model import (
    ActiveStatus,
    BlockedStatus,
)
import logging

from slurm_ops_manager import SlurmManager

from slurmdbd_provides import Slurmdbd

logger = logging.getLogger()


class SlurmdbdCharm(CharmBase):
    """Slurmdbd Charm Class."""

    _stored = StoredState()

    def __init__(self, *args):
        """Set the defaults for slurmdbd."""
        super().__init__(*args)

        self._stored.set_default(
            slurmdbd_available=False,
        )
        self.slurm_manager = SlurmManager(self, "slurmdbd")
        self.slurmdbd = Slurmdbd(self, "slurmdbd")

        self.db = MySQLClient(self, "db")

        event_handler_bindings = {
            self.on.install: self._on_install,
            self.on.config_changed: self._on_config_changed,
            self.db.on.database_available: self._on_database_available,
        }
        for event, handler in event_handler_bindings.items():
            self.framework.observe(event, handler)

    def _on_install(self, event):
        self.slurm_manager.install()
        self.unit.status = ActiveStatus("Slurm Installed")
        self._stored.slurm_installed = True

    def _on_config_changed(self, event):
        _write_config_and_restart_slurmdbd(self, event)

    def _on_database_available(self, event):
        """Render the database details into the slurmdbd.yaml."""
        db = {
            'db_username': event.db_info.user,
            'db_password': event.db_info.password,
            'db_hostname': event.db_info.host,
            'db_port': event.db_info.port,
            'db_name': event.db_info.database,
        }
        logger.debug("database available")

        self._stored.db_info_acquired = True
        _write_config_and_restart_slurmdbd(self, event)


def _write_config_and_restart_slurmdbd(charm, event, db):
    """Check for prerequisites before writing config/restart of slurmdbd."""
    if not charm._stored.slurm_installed:
        event.defer()
        return

    slurmdbd_host_port_addr = {
        'slurmdbd_hostname': socket.gethostname().split(".")[0],
        'slurmdbd_port': "6819",
    }
    slurmdbd_config = {
        **slurmdbd_host_port_addr,
        **charm.model.config,
        **db,
    }
    charm.slurm_ops_manager.render_config_and_restart(slurmdbd_config)
    charm.unit.status = ActiveStatus("Slurmdbd Available")
    charm._stored.slurmdbd_started = True


if __name__ == "__main__":
    main(SlurmdbdCharm)
