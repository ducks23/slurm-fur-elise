#!/usr/bin/python3
"""Slurmd."""
import json
import logging

from ops.framework import (
    EventBase,
    EventSource,
    Object,
    ObjectEvents,
    StoredState,
)


logger = logging.getLogger()


class SlurmdAvailableEvent(EventBase):
    """Emmited when slurmd is available."""
    def __init__(self, handle, slurmd_info):
        super().__init__(handle)
        self._slurmd_info = slurmd_info

    @property
    def slurmd_info(self):
        return self._slurmd_info

    def snapshot(self):
        return self.slurmd_info.snapshot()

    def restore(self, snapshot):
        self._slurmd_info = SlurmdInfo.restore(snapshot)


class SlurmdRequiresEvents(ObjectEvents):
    """SlurmClusterProviderRelationEvents."""

    slurmd_available = EventSource(SlurmdAvailableEvent)


class Slurmd(Object):
    """Slurmd."""

    on = SlurmdRequiresEvents()
    _state = StoredState()

    def __init__(self, charm, relation_name):
        """Set self._relation_name and self.charm."""
        super().__init__(charm, relation_name)
        self._charm = charm
        self._relation_name = relation_name

        self.framework.observe(
            self._charm.on[self._relation_name].relation_created,
            self._on_relation_created
        )
        self.framework.observe(
            self._charm.on[self._relation_name].relation_changed,
            self._on_relation_changed
        )

    def _on_relation_created(self, event):
        pass

    def _on_relation_joined(self, event):
        pass

    def _on_relation_changed(self, event):
        if not event.relation.data.get(event.unit):
            event.defer()
            return
        rel_data = event.relation[event.unit]
        host = rel_data.get('host', None)
        partition = rel_data.get('partition', None)
        state = rel_data.get('state', None)
        node_name = rel_data.get('node-name', None)
        node_addr = rel_data.get('node-addr', None)
        real_memory = rel_data.get('real-memory', None)
        cpus = rel_data.get('cpus', None)
        threads_per_core = rel_data.get('threads-per-core', None)
        threads_per_socket = rel_data.get('threads-per-socket', None)
        sockets_per_board = rel_data.get('sockets-per-board', None)
        
        if not (
                host and
                partition and 
                state and 
                node_name and 
                node_addr and
                real_memory and
                cpus and
                threads_per_core and
                threads_per_socket and
                sockets_per_board
            )
            event.defer()
            return

        slurmd = SlurmdInfo(
                host,
                partition,
                state,
                node_name,
                node_addr,
                real_memory,
                cpus,
                threads_per_core,
                threads_per_socket,
                sockets_per_board
            )
        self.on.slurmd_available.emit(slurmd)

    def _on_relation_broken(self, event):
        pass

class SlurmdInfo:

    def __init__(
            self,
            host=None,
            inventory=None,
            partition=None,
            state=None
        ):
        self.set_address(
            host,
            inventory,
            partition,
            state
        )

    def set_address(
            self,
            host,
            inventory,
            partition,
            state
        ):
        self._host = host
        self._inventory = inventory
        self._partition = partition
        self._state = state
    
    @property
    def host(self):
        return self._host

    @property
    def partition(self):
        return self._partition

    @property
    def inventory(self):
        return self._inventory
    
    @property
    def state(self):
        return self._state

    @classmethod
    def restore(cls, snapshot):
        return cls(
            host=snapshot['slurmd_info.host'],
            inventory=snapshot['slurmd_info.inventory'],
            partition=snapshot['slurmd_info.partition'],
            state=snapshot['slurmd_info.state'],
        )

    def snapshot(self):
        return {
            'slurmd_info.host': self.host,
            'slurmd_info.inventory': self.inventory,
            'slurmd_info.partition': self.partition,
            'slurmd_info.state': self.state,
        }
