"""Tests for DevRev public schema lookup through the SDK clients."""

import json

import httpx
import pytest
import respx

from devrev import AsyncDevRevClient, DevRevClient
from devrev.models import AggregatedSchemaGetRequest, CustomSchemaSpecForRead


@pytest.mark.parametrize("use_async", [False, True])
async def test_get_aggregated_schema(mock_env_vars, use_async):
    field = {
        "name": "tnt__jira_issue_keys",
        "field_type": "array",
        "base_type": "text",
        "ui": {"display_name": "Jira issues"},
    }
    schema_payload = {"custom_fields": [field], "stock_fields": [{"name": "title"}]}
    request = AggregatedSchemaGetRequest(
        leaf_type="ticket",
        custom_schema_spec=CustomSchemaSpecForRead(apps=["tracker"], subtype="bug"),
        is_custom_leaf_type=False,
    )

    with respx.mock as router:
        route = router.post("https://api.test.devrev.ai/schemas.aggregated.get").mock(
            return_value=httpx.Response(200, json={"schema": schema_payload})
        )
        if use_async:
            async with AsyncDevRevClient() as client:
                schema = await client.schemas.aggregated_get(request)
        else:
            with DevRevClient() as client:
                schema = client.schemas.aggregated_get(request)

    assert route.call_count == 1
    assert json.loads(route.calls.last.request.content) == {
        "leaf_type": "ticket",
        "custom_schema_spec": {"apps": ["tracker"], "subtype": "bug"},
        "is_custom_leaf_type": False,
    }
    assert schema.custom_fields[0].base_type == "text"
    assert schema.model_dump(exclude_none=True) == schema_payload
