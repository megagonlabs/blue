import json
from datetime import datetime
from blue.utils.log_utils import CustomLogger
from .logstore import LogStore


class SearchableCustomLogger(CustomLogger):
    """
    Extends CustomLogger with structured event collection via pluggable LogStore.
    Automatically routes context → RedisLogStore namespaces.
    """

    def __init__(self, config=None, logstore: LogStore = None):
        super().__init__(config=config)
        self.logstore = logstore
        self.context = {}  # persistent execution context fields

    def set_logstore(self, logstore: LogStore):
        """Dynamically attach or replace the backend LogStore."""
        self.logstore = logstore

    # -----------------------------------------------------
    # CONTEXT MANAGEMENT
    # -----------------------------------------------------
    def set_context(self, **kwargs):
        """Set persistent context (session, agent, operator, planner...)."""
        self.context.update(kwargs)

    def update_context(self, **kwargs):
        """Alias for set_context(), improves readability."""
        self.context.update(kwargs)

    def clear_context(self):
        """Reset context (typically at session boundaries)."""
        self.context = {}

    # -----------------------------------------------------
    # STRUCTURED RECORD EMISSION
    # -----------------------------------------------------
    def record(self, **fields):
        """
        Record a structured event.
        Args may include:
            action, inputs, outputs, duration, metadata, etc.
        """

        if not self._initialized:
            self._initialize()

        # Build log event without injecting context here
        payload = {
            "timestamp": datetime.utcnow().isoformat(),
            **fields
        }

        # Persist to backend store (with context passed separately)
        if self.logstore:
            try:
                self.logstore.write(record=payload, context=self.context)
            except Exception as e:
                super().error(f"Structured log backend failed: {e}")

        # Emit to standard logger for visibility
        super().info(json.dumps(payload))

        return payload


