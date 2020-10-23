#!/usr/bin/python3
"""Slurmctld."""
import json
import logging
import socket

from ops.framework import (
    EventBase,
    EventSource,
    Object,
    ObjectEvents,
)


logger = logging.getLogger()


class ConfigAvailableEvent(EventBase):
    """Emitted when slurm-config is available."""


class SlurmctldEvents(ObjectEvents):
    """Slurmctld relation events."""

    config_available = EventSource(ConfigAvailableEvent)


class Slurmctld(Object):
    """Slurmctld."""

    on = SlurmctldRelationEvents()

    def __init__(self, charm, relation_name):
        """Set initial data and observe interface events."""
        super().__init__(charm, relation_name)
        self._charm = charm
        self._relation_name = relation_name

        self.framework.observe(
            self._charm.on[self._relation_name].relation_changed,
            self._on_relation_changed
        )
        self.framework.observe(
            self._charm.on[self._relation_name].relation_departed,
            self._on_relation_departed
        )
        self.framework.observe(
            self._charm.on[self._relation_name].relation_broken,
            self._on_relation_broken
        )

    def _on_relation_created(self, event):
        """Obtain and store the munge_key, emit slurm_config_available."""
        host = socket.gethostbyname()
        event.relation.data[self.model.unit]['host'] = host
    
    def _on_relation_changed(self, event):
        """Obtain and store the munge_key, emit slurm_config_available."""
        event_app_data = event.relation.data.get(event.app)
        if not event_app_data:
            event.defer()
            return

        slurm_config = event_app_data.get('slurm_config')
        if not slurm_config:
            event.defer()
            return
        self.on.config_available.emit()
