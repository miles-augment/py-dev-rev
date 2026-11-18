"""Read-only schema services for the DevRev SDK."""

from devrev.models.schemas import (
    AggregatedSchema,
    AggregatedSchemaGetRequest,
    AggregatedSchemaGetResponse,
)
from devrev.services.base import AsyncBaseService, BaseService


class SchemasService(BaseService):
    """Read DevRev object schemas."""

    def aggregated_get(self, request: AggregatedSchemaGetRequest) -> AggregatedSchema:
        """Get the effective schema for an object type or schema fragments."""
        response = self._post("/schemas.aggregated.get", request, AggregatedSchemaGetResponse)
        return response.schema_


class AsyncSchemasService(AsyncBaseService):
    """Read DevRev object schemas asynchronously."""

    async def aggregated_get(self, request: AggregatedSchemaGetRequest) -> AggregatedSchema:
        """Get the effective schema for an object type or schema fragments."""
        response = await self._post("/schemas.aggregated.get", request, AggregatedSchemaGetResponse)
        return response.schema_
