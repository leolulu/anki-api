from dataclasses import dataclass


@dataclass
class SearchResult:
    id: int
    query: str
    note_content: str