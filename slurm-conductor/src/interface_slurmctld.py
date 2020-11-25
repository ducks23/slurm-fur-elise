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


class SlurmctldAvailableEvent(EventBase):
    """Emmited when slurmctld is available."""
    def __init__(self, handle, slurmctld_info):
        super().__init__(handle)
        self._slurmctld_info = slurmctld_info

    @property
    def slurmctld_info(self):
        return self._slurmctld_info

    def snapshot(self):
        return self.slurmctld_info.snapshot()

    def restore(self, snapshot):
        self._slurmctld_info = SlurmctldInfo.restore(snapshot)


class SlurmctldRequiresEvents(ObjectEvents):
    """SlurmClusterProviderRelationEvents."""

    slurmctld_available = EventSource(SlurmctldAvailableEvent)


class Slurmctld(Object):
    """Slurmctld."""

    on = SlurmctldRequiresEvents()

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
        
        host = event.relation.data[event.unit].get('host')
        if not host:
            event.defer()
            return
        slurmctld = SlurmctldInfo(host)
        self.on.slurmctld_available.emit(slurmctld)

    def _on_relation_broken(self, event):
        pass

class SlurmctldInfo:

    def __init__(self, host=None):
        self.set_address(host)

    def set_address(self, host):
        self._host = host
    
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
            host=snapshot['slurmctld_info.host'],
        )

    def snapshot(self):
        return {
            'slurmctld_info.host': self.host,
        }
