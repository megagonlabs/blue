from typing import Dict, Optional
from blue.data.source import DataSource


class DatabaseConnectionManager:
    def __init__(self):
        self.active_sources: Dict[str, DataSource] = {}

    def get_source(self, source_name: str) -> Optional[DataSource]:
        return self.active_sources.get(source_name)

    def add_source(self, source_name: str, source_obj: DataSource):
        self.active_sources[source_name] = source_obj

    def remove_source(self, source_name: str):
        if source_name in self.active_sources:
            del self.active_sources[source_name]
