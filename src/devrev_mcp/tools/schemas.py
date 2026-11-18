"""Read-only MCP tools for DevRev object schemas."""

from typing import Any

from mcp.server.fastmcp import Context

from devrev.exceptions import DevRevError
from devrev.models.schemas import AggregatedSchemaGetRequest, CustomSchemaSpecForRead
from devrev_mcp.server import mcp
from devrev_mcp.utils.errors import format_devrev_error
from devrev_mcp.utils.formatting import serialize_model


@mcp.tool()
async def devrev_schemas_aggregated_get(
    ctx: Context[Any, Any, Any],
    leaf_type: str | None = None,
    field_name: str | None = None,
    custom_schema_fragments: list[str] | None = None,
    custom_schema_spec: CustomSchemaSpecForRead | None = None,
    is_custom_leaf_type: bool | None = None,
    stock_schema_fragment: str | None = None,
) -> dict[str, Any]:
    """Read the effective DevRev schema and discover custom field types before writing.

    Args:
        leaf_type: DevRev object type, e.g. "ticket" or "issue".
        field_name: Return just this custom field definition by exact API name,
            e.g. "tnt__release_notes". Omit to return the full schema.
        custom_schema_fragments: Custom schema fragment IDs to include.
        custom_schema_spec: App names and/or a subtype to include.
        is_custom_leaf_type: Whether leaf_type identifies a custom object type.
        stock_schema_fragment: Stock schema fragment ID to include.
    """
    app = ctx.request_context.lifespan_context
    request = AggregatedSchemaGetRequest(
        leaf_type=leaf_type,
        custom_schema_fragments=custom_schema_fragments,
        custom_schema_spec=custom_schema_spec,
        is_custom_leaf_type=is_custom_leaf_type,
        stock_schema_fragment=stock_schema_fragment,
    )
    try:
        schema = await app.get_client().schemas.aggregated_get(request)
    except DevRevError as e:
        raise RuntimeError(format_devrev_error(e)) from e

    if field_name is None:
        return {"schema": serialize_model(schema)}
    for field in schema.custom_fields:
        if field.name == field_name:
            return {"field": serialize_model(field)}
    raise RuntimeError(f"Custom field {field_name!r} not found in the returned schema.")
