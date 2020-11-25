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


class SlurmdbdAvailableEvent(EventBase):
    """Emmited when slurmdbd is available."""
    def __init__(self, handle, slurmdbd_info):
        super().__init__(handle)
        self._slurmdbd_info = slurmdbd_info

    @property
    def slurmdbd_info(self):
        return self._slurmdbd_info

    def snapshot(self):
        return self.slurmdbd_info.snapshot()

    def restore(self, snapshot):
        self._slurmdbd_info = SlurmdbdInfo.restore(snapshot)


class SlurmdbdRequiresEvents(ObjectEvents):
    """SlurmClusterProviderRelationEvents."""

    slurmdbd_available = EventSource(SlurmdbdAvailableEvent)


class Slurmdbd(Object):
    """Slurmdbd."""

    on = SlurmdbdRequiresEvents()

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
        slurmdbd = SlurmdbdInfo(host, inventory, partition, state)
        self.on.slurmdbd_available.emit(slurmdbd)

    def _on_relation_broken(self, event):
        pass

class SlurmdbdInfo:

    def __init__(self, host=None):
        self.set_address(host)

    def set_address(self, host):
        self._host = host
    
    @property
    def host(self):
        return self._host


    @classmethod
    def restore(cls, snapshot):
        return cls(
            host=snapshot['slurmdbd_info.host'],
        )

    def snapshot(self):
        return {
            'slurmdbd_info.host': self.host,
        }
