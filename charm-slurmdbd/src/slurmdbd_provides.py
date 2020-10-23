#! /usr/bin/env python3
"""SlurmdbdProvidesRelation."""
import logging
import socket
from ops.framework import (
    EventBase,
    EventSource,
    Object,
    ObjectEvents,
    StoredState,
)


logger = logging.getLogger()


class SlurmctldAvailableEvent(EventBase):
    """Emitted when slurmctld is available."""


class SlurmctldUnAvailableEvent(EventBase):
    """Emitted when slurmctld is unavailable."""


class MungeKeyAvailableEvent(EventBase):
    """Emitted when the munge key becomes available."""


class SlurmdbdProvidesRelationEvents(ObjectEvents):
    """SlurmdbdProvidesRelationEvents."""

    munge_key_available = EventSource(MungeKeyAvailableEvent)
    slurmctld_available = EventSource(SlurmctldAvailableEvent)
    slurmctld_unavailable = EventSource(SlurmctldUnAvailableEvent)


class Slurmdbd(Object):
    """SlurmdbdProvidesRelation."""

    on = SlurmdbdProvidesRelationEvents()

    _state = StoredState()

    def __init__(self, charm, relation_name):
        """Set the provides initial data."""
        super().__init__(charm, relation_name)

        self.charm = charm
        self._relation_name = relation_name


        self.framework.observe(
            charm.on[self._relation_name].relation_created,
            self._on_relation_created
        )

        self.framework.observe(
            charm.on[self._relation_name].relation_changed,
            self._on_relation_changed
        )

        self.framework.observe(
            charm.on[self._relation_name].relation_broken,
            self._on_relation_broken
        )

    def _on_relation_created(self, event):
        if not self.charm._stored.slurmdbd_available:
            event.defer()
            return
        host = socket.gethostname().split(".")[0]
        munge = self.charm.slurm_manager.get_munge_key()
        event.relation.data[self.model.unit]['hostname'] = host
        event.relation.data[self.model.unit]['munge-key'] = munge
