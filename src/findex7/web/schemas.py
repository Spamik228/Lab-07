from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    doc_id: str
    title: str
    score: float
    snippet: str


class SearchResponse(BaseModel):
    query: str
    total: int
    took_ms: float
    results: List[SearchResult]


class StatsResponse(BaseModel):
    index_size_bytes: int
    doc_count: int
    vocabulary_size: int
    uptime_seconds: float


class HealthResponse(BaseModel):
    status: Literal["ok"]