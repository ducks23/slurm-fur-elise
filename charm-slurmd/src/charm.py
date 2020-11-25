#!/usr/bin/python3
"""SlurmdCharm."""
import logging

from interface_slurmd import Slurmd
from ops.charm import CharmBase
from ops.framework import StoredState
from ops.main import main
from ops.model import (
    ActiveStatus,
    BlockedStatus,
)
from slurm_ops_manager import SlurmManager
from utils import random_string


logger = logging.getLogger()


class SlurmdCharm(CharmBase):
    """Slurmd lifecycle events."""

    _stored = StoredState()

    def __init__(self, *args):
        """Init _stored attributes and interfaces, observe events."""
        super().__init__(*args)

        self._stored.set_default(
            config_available=False,
            munge_available=False,
        )

        self._slurm_manager = SlurmManager(self, "slurmd")

        self._slurmd = Slurmd(self, "slurmd")

        event_handler_bindings = {
            self.on.install: self._on_install,
        }
        for event, handler in event_handler_bindings.items():
            self.framework.observe(event, handler)

    def _on_install(self, event):
        #self._slurm_manager.install()
        self.unit.status = ActiveStatus("Slurm Installed")


if __name__ == "__main__":
    main(SlurmdCharm)
