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
        Supports ephemeral context for workers via _ephemeral_context.
        Args may include:
            action, inputs, outputs, duration, metadata, etc.
        """

        if not self._initialized:
            self._initialize()

        # Extract ephemeral worker-level context
        ephemeral = fields.pop("_ephemeral_context", {})

        # Merge persistent + ephemeral context
        full_context = {**self.context, **ephemeral}

        # Build log event without injecting context here
        payload = {
            "timestamp": datetime.utcnow().isoformat(),
            **fields
        }

        # Final stored record
        final_record = {
            **payload,
            "context": full_context
        }

        # Write to logstore
        if self.logstore:
            try:
                self.logstore.write(record=final_record, context=full_context)
            except Exception as e:
                super().error(f"Structured log backend failed: {e}")

        # Emit readable log
        super().info(json.dumps(final_record))

        return final_record