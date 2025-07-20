from dataclasses import dataclass


@dataclass
class SearchResult:
    id: int
    user_query: str
    note_content: str