#!/usr/bin/python3
"""SlurmctldCharm."""
import logging

from interface_slurmctld import Slurmctld
from ops.charm import CharmBase
from ops.framework import StoredState
from ops.main import main
from ops.model import (
    ActiveStatus,
    BlockedStatus,
)
from slurm_ops_manager import SlurmManager


logger = logging.getLogger()


class SlurmctldCharm(CharmBase):
    """Slurmctld lifecycle events."""

    _stored = StoredState()

    def __init__(self, *args):
        """Init _stored attributes and interfaces, observe events."""
        super().__init__(*args)

        self._stored.set_default(
        )
        self._slurm_manager = SlurmManager(self, "slurmctld")

        self._slurmctld = Slurmctld(self, "slurmctld")

        event_handler_bindings = {
            self.on.install: self._on_install,
            # need to figure out how I want to implement munge
            self._slurmctld.on.config_available:
            self._on_check_status_and_write_config,
        }
        for event, handler in event_handler_bindings.items():
            self.framework.observe(event, handler)

    def _on_install(self, event):
        self._slurm_manager.install()
        self._stored.slurm_installed = True
        self.unit.status = ActiveStatus("Slurm Installed")

    def _on_upgrade(self, event):
        self._slurm_manager.upgrade()

    def _on_munge_available(self, event):
        self._slurm_manager.write_munge_key(
            event.munge.munge
        )
        self._stored.munge_available = True

    def _on_check_status_and_write_config(self, event):
        if not self._stored.munge_available:
            event.defer()
            return
        
        self.slurm_manager.write_config_restart(
            event.config_info.config
        )


if __name__ == "__main__":
    main(SlurmctldCharm)
