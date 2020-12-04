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

    _stored = StoredState()

    def __init__(self, *args):
        """Initialize charm."""
        super().__init__(*args)

        self._stored.set_default(
            db=dict(),
            partitions=set(),
        )

        self._slurmd = Slurmd(self, "slurmd")

        event_handler_bindings = {
            self.on.install: self._on_install,
            self.on.start: self._on_start,
            self.on.config_chaged: self._on_start,
            self._slurmd.on.slurmd_available: self._on_slurmd_available,
            }

        for event, handler in event_handler_bindings.items():
            self.framework.observe(event, handler)


    def _on_install(self, event):
        subprocess.run(["sleep", "10"])
    
    def _on_start(self, event):
        self.framework.breakpoint()

    def _on_slurmd_available(self, event):
        partition_name = event.slurmd_info.partition
        host = event.slurmd_info.host
        inventory = event.slurmd_info.inventory
        state = event.slurmd_info.state

        node = {
            'node_name': node_name,
            'node_addr': node_addr,
            'state':state,
            'real_memory': real_memory,
            'cpus': cpus,
            'threads_per_core': threads_per_core,
            'cores_per_socket': cores_per_socket,
            'sockets_per_board': sockets_per_board,
            'host': host,
            'inventory': inventory,
            'state': state
        }
        partition = { 
            'nodes': [node],
            'default': default,
            'state': state
        }
        """ checks to see if current partition is already in the set
        of partitions
        if not it adds partition to set and adds the new node to stored dict

        else gets the current set of nodes and appends the new node
        to the list of nodes already in the partition
        """

        if not self._stored.partitions.__contains__(partition_name):
            self._stored.partitions.__add__(partition_name)
            self._stored.db.__setitem__(partition_name, partition)
        else:
            current_nodes = self._stored.db.__getitem__(partition_name)
            new_nodes = current_nodes['nodes'].append(nodes)
            partition['nodes'] = new_nodes
            self._stored.db.__setitem__(partition_name, partition)



if __name__ == "__main__":
    main(SlurmOperator)
