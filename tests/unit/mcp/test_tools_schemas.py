"""Tests for the registered DevRev schema lookup MCP tool."""

import json
from datetime import timedelta

import httpx
import respx
from mcp.shared.memory import create_connected_server_and_client_session

from devrev_mcp.server import mcp


async def test_lookup_schema_and_custom_field_over_mcp(mock_env_vars):
    field = {"name": "tnt__jira_issue_keys", "field_type": "array", "base_type": "text"}
    schema = {"custom_fields": [field], "leaf_type": "ticket", "stock_fields": []}
    tool_name = "devrev_schemas_aggregated_get"
    with respx.mock as router:
        route = router.post("https://api.test.devrev.ai/schemas.aggregated.get").mock(
            return_value=httpx.Response(200, json={"schema": schema})
        )
        async with create_connected_server_and_client_session(mcp, timedelta(seconds=5)) as session:
            result = await session.call_tool(tool_name, {"leaf_type": "ticket"})
            assert not result.isError
            assert result.structuredContent == {"schema": schema}

            result = await session.call_tool(
                tool_name, {"leaf_type": "ticket", "field_name": field["name"]}
            )
            assert not result.isError
            assert result.structuredContent == {"field": field}

            result = await session.call_tool(
                tool_name, {"leaf_type": "ticket", "field_name": "tnt__jira_issue"}
            )
            assert result.isError
            assert "not found in the returned schema" in result.content[0].text

    assert [json.loads(call.request.content) for call in route.calls] == [
        {"leaf_type": "ticket"},
        {"leaf_type": "ticket"},
        {"leaf_type": "ticket"},
    ]
