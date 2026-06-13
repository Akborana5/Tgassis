from __future__ import annotations

from dataclasses import dataclass

from rapidfuzz import fuzz

from .models import MediaItem, SearchResponse, SearchResult


@dataclass(slots=True)
class SearchService:
    def score(self, query: str, item: MediaItem) -> float:
        q = query.strip().lower()
        if not q:
            return 0.0
        title = item.title.lower()
        token_score = 100.0 if q in title else float(fuzz.partial_ratio(q, title))
        lang_score = max((float(fuzz.partial_ratio(q, lang.lower())) for lang in item.languages), default=0.0)
        quality_score = max((float(fuzz.partial_ratio(q, quality.lower())) for quality in item.qualities), default=0.0)
        return (token_score * 0.7) + (lang_score * 0.2) + (quality_score * 0.1)

    def search(self, query: str, items: list[MediaItem], page: int = 1, page_size: int = 20) -> SearchResponse:
        scored = [
            SearchResult(
                id=item.id,
                title=item.title,
                year=item.year,
                poster=item.poster,
                languages=item.languages,
                qualities=item.qualities,
                score=round(self.score(query, item), 2),
            )
            for item in items
        ]
        filtered = [result for result in scored if result.score >= 40 or query.lower() in result.title.lower()]
        ranked = sorted(filtered, key=lambda r: r.score, reverse=True)

        start = max(0, (page - 1) * page_size)
        end = start + page_size
        return SearchResponse(
            query=query,
            page=page,
            page_size=page_size,
            total=len(ranked),
            items=ranked[start:end],
        )


search_service = SearchService()
