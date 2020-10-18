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

    def sanpshot(self):
        return self.slurmd_info.snapshot()

    def restor(self, snapshot):
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
        host = event.relation.data[event.unit].get("host", None)

    def _on_relation_broken(self, event):
        pass

class SlurmdInfo:

    def __init__(self, host=None,port=None):
        self.set_address(host, port)

    def set_address(self, host, port):
        self._host = host
        self._port = port

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port

    @classmethod
    def restore(cls, snapshot):
        return cls(
            host=snapshot['slurmd_info.host'],
            port=snapshot['slurmd_info.port'],
        )

    def snapshot(self):
        return {
            'slurmd_info.host': self.host,
            'slurmd_info.port': self.port,
        }
