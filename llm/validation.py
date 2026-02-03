from pydantic import BaseModel, Field, field_validator
from typing import List, Literal, Optional, Union
from enum import Enum

# Enums for validation
class QueryType(str, Enum):
    SEARCH_BOOKS = "search_books"
    FIND_AUTHORS = "find_authors"
    GET_REVIEWS = "get_reviews"
    SEARCH_PUBLISHERS = "search_publishers"
    FIND_GENRES = "find_genres"

class OperatorType(str, Enum):
    EQUALS = "="
    CONTAINS = "contains"
    GREATER_THAN = ">"
    LESS_THAN = "<"
    GREATER_THAN_EQUAL = ">="
    LESS_THAN_EQUAL = "<="
    NOT_EQUALS = "!="

class FilterType(str, Enum):
    ##GENRE = "genre"
    THEME = "theme"
    AUTHOR = "author"
    PUBLISHER = "publisher"
    PUBLICATION_YEAR = "publication_year"
    PAGE_COUNT = "page_count"
    RATING = "rating"
    SETTING = "setting"
    LANGUAGE = "language"
    ISBN = "isbn"

class SortByType(str, Enum):
    TITLE = "title"
    PUBLICATION_YEAR = "publication_year"
    PAGE_COUNT = "page_count"
    RATING = "rating"
    AUTHOR_NAME = "author_name"
    NONE = "none"

class SortOrderType(str, Enum):
    ASC = "asc"
    DESC = "desc"

# Main filter model
class QueryFilter(BaseModel):
    type: FilterType = Field(..., description="Type of filter to apply")
    value: Union[str, int, float] = Field(..., description="Value to filter by")
    operator: OperatorType = Field(OperatorType.EQUALS, description="Comparison operator")
    
    @field_validator('value')
    @classmethod
    def validate_value_based_on_type(cls, v, info):
        filter_type = info.data.get('type')
        
        if filter_type in ['publication_year', 'page_count', 'rating']:
            if not isinstance(v, (int, float)):
                try:
                    return int(v)
                except ValueError:
                    raise ValueError(f"{filter_type} must be a number")
        
        elif filter_type in ['genre', 'theme', 'author', 'publisher', 'setting', 'language']:
            if not isinstance(v, str):
                raise ValueError(f"{filter_type} must be a string")
        
        return v

# Main query intent model
class QueryIntent(BaseModel):
    query_type: QueryType = Field(QueryType.SEARCH_BOOKS, description="Type of query to execute")
    filters: List[QueryFilter] = Field(default_factory=list, description="List of filters to apply")
    sort_by: Optional[SortByType] = Field(SortByType.NONE, description="Field to sort results by")
    sort_order: SortOrderType = Field(SortOrderType.DESC, description="Sort order (ascending/descending)")
    limit: int = Field(20, ge=1, le=100, description="Maximum number of results to return")
    
    @field_validator('filters')
    @classmethod
    def validate_filters(cls, v):
        if not v:
            raise ValueError("At least one filter is required for meaningful queries")
        return v
    
    @field_validator('sort_by')
    @classmethod
    def validate_sort_by(cls, v, info):
        # If sort_by is provided, ensure it's compatible with query_type
        query_type = info.data.get('query_type')
        
        if v != SortByType.NONE:
            if query_type == QueryType.FIND_AUTHORS and v not in [SortByType.AUTHOR_NAME, SortByType.NONE]:
                raise ValueError(f"Cannot sort authors by {v}")
        
        return v