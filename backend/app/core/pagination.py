"""
Pagination helpers for building paginated query results.
"""
import math
from dataclasses import dataclass


@dataclass
class PaginationParams:
    """Validated pagination parameters."""

    page: int
    page_size: int

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


def calculate_total_pages(total: int, page_size: int) -> int:
    """Calculate the total number of pages given total items and page size."""
    if page_size <= 0:
        return 0
    return math.ceil(total / page_size)