from typing import Tuple, Dict, Any


def get_page_params(page: int, size: int) -> Tuple[int, int]:
    """
    Calculates SQL offset and limit from 1-indexed page and page size.

    :param page: The 1-based page number.
    :param size: Number of items per page.
    :return: A tuple of (offset, limit).
    """
    limit = max(1, size)
    offset = (max(1, page) - 1) * limit
    return offset, limit


def get_paginated_metadata(total: int, page: int, size: int) -> Dict[str, Any]:
    """
    Generates standard pagination metadata descriptors.

    :param total: Total number of records matching the query.
    :param page: The current active page number (1-based).
    :param size: The page limit size.
    :return: A dictionary containing pagination metadata.
    """
    limit = max(1, size)
    current_page = max(1, page)
    total_pages = (total + limit - 1) // limit if total > 0 else 0
    return {
        "total": total,
        "page": current_page,
        "size": limit,
        "total_pages": total_pages,
        "has_next": current_page < total_pages,
        "has_prev": current_page > 1,
    }
