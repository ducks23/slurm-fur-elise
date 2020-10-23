#!/usr/bin/python3
"""Slurmctld."""
import logging
import socket

from ops.framework import (
    EventBase,
    EventSource,
    Object,
    ObjectEvents,
)


logger = logging.getLogger()


class Slurmctld(Object):
    """Slurmctld Interface."""

    def __init__(self, charm, relation_name):
        """Initialize and observe."""
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

        self.framework.observe(
            self._charm.on[self._relation_name].relation_departed,
            self._on_relation_departed
        )

    def _on_relation_created(self, event):
        """Set hostname and port on the unit data."""
        host = socket.gethostbyname()
        event.relation.data[self.model.unit]['host'] = host
