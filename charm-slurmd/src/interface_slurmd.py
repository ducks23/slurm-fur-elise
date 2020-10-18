#!/usr/bin/python3
"""Slurmd."""
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

class SlurmConfigAvailableEvent(EventBase):
    """Emitted when slurm config is available."""


class SlurmdProvidesEvents(ObjectEvents):
    """SlurmctldProvidesEvents."""

    slurm_config_available = EventSource(SlurmConfigAvailableEvent)


class Slurmd(Object):
    """Slurmd."""

    on = SlurmdProvidesEvents()

    def __init__(self, charm, relation_name):
        """Set initial data and observe interface events."""
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
        """Set partition name to slurm-configurator."""
        event.relation.data[self.model.app]['hostname'] = socket.gethostbyname()

    def _on_relation_changed(self, event):
        """Check for the munge_key in the relation data."""
        event_app_data = event.relation.data.get(event.app)
        if not event_app_data:
            event.defer()
            return
        slurm_config = event_app_data.get('slurm_config')
        
        if not slurm_config:
            event.defer()
            return

        self._charm._stored.config_available = True
        self.on.slurm_config_available.emit()
