from typing import List, Dict, Any, Optional
from pydantic import BaseModel, HttpUrl, Field


class TagResult(BaseModel):
    """Model for the result of counting href tags in a URL"""
    url_id: int = Field(..., description="ID of the processed URL")
    url: str = Field(..., description="URL that was processed")
    count: int = Field(..., description="Number of href tags found")


class TagsResponse(BaseModel):
    """Model for the response containing all count results"""
    data: List[TagResult] = Field(..., description="List of results by URL")
    total_time: float = Field(..., description="Total processing time in seconds")
    urls_processed: int = Field(..., description="Number of URLs processed")


class HealthResponse(BaseModel):
    """Model for the health endpoint response"""
    data: str = Field("Ok!", description="Application status")


class IndexResponse(BaseModel):
    """Model for the main endpoint response"""
    data: str = Field("/v1/tags | /docs | /healthcheck", description="Navigation information")


class ErrorResponse(BaseModel):
    """Model for error responses"""
    data: str = Field(..., description="Error message")
