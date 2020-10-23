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
    def __init__(self, handle, db_info):
        super().__init__(handle)
        self._slurmd_info = db_info

    @property
    def slurmd_info(self):
        return self._slurmd_info

    def snapshot(self):
        return self.slurmd_info.snapshot()

    def restore(self, snapshot):
        self._slurmd_info = SlurmdInfo.restor(snapshot)


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
        
        inventory = event.relation.data[event.unit].get('inventory')
        if not inventory:
            event.defer()
            return
        partition = event.relation.data[event.unit].get('partition')
        partition = event.relation.data[event.unit].get('state')
        slurmd = SlurmdInfo(inventory, partition, state)
        self.on.slurmd_available.emit(slurmd)

    def _on_relation_broken(self, event):
        pass

class SlurmdInfo:

    def __init__(self, inventory=None, partition=None, state=None):
        self.set_address(partition, port, state)

    def set_address(self, inventory, partition, state):
        self._inventory = inventory
        self._partition = partition
        self._state = state

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
            inventory=snapshot['slurmd_info.inventory'],
            partition=snapshot['slurmd_info.partition'],
            state=snapshot['slurmd_info.state'],
        )

    def snapshot(self):
        return {
            'slurmd_info.inventory': self.inventory,
            'slurmd_info.partition': self.partition,
            'slurmd_info.state': self.state,
        }
