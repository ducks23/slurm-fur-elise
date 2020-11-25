#!/usr/bin/python3
"""SlurmOperator."""
import logging
import subprocess

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

    db = StoredState()

    def __init__(self, *args):
        """Initialize charm."""
        super().__init__(*args)

        self.db.set_default(
            slurmd_nodes=dict(),
        )

        self._slurmd = Slurmd(self, "slurmd")

        event_handler_bindings = {
            self.on.install: self._on_install,
            self._slurmd.on.slurmd_available: self._on_slurmd_available,
            }

        for event, handler in event_handler_bindings.items():
            self.framework.observe(event, handler)


    def _on_install(self, event):
        pass

    def _on_slurmd_available(self, event):
        partition = event.slurmd_info.partition
        host = event.slurmd_info.host
        inventory = event.slurmd_info.inventory
        state =  event.slurmd_info.state

        logger.debug(host)
        self.framework.breakpoint()
        self.db.slurmd_nodes[partition][host] = {
            'host': host,
            'inventory': inventory,
            'state': state,
        }
        self.framework.breakpoint()
        

if __name__ == "__main__":
    main(SlurmOperator)
