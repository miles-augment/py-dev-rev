"""Models for reading DevRev object schemas."""

from pydantic import ConfigDict, Field

from devrev.models.base import DevRevBaseModel, DevRevResponseModel


class CustomSchemaSpecForRead(DevRevBaseModel):
    """Identify app and subtype fragments to include in a schema lookup."""

    apps: list[str] | None = None
    subtype: str | None = None


class AggregatedSchemaGetRequest(DevRevBaseModel):
    """Request the effective schema for an object type or schema fragments."""

    leaf_type: str | None = None
    custom_schema_fragments: list[str] | None = None
    custom_schema_spec: CustomSchemaSpecForRead | None = None
    is_custom_leaf_type: bool | None = None
    stock_schema_fragment: str | None = None


class CustomFieldDefinition(DevRevResponseModel):
    """A custom field definition, including its type and any server metadata."""

    model_config = ConfigDict(extra="allow")

    name: str
    field_type: str
    base_type: str | None = None


class AggregatedSchema(DevRevResponseModel):
    """The combined object schema, including custom and stock definitions."""

    model_config = ConfigDict(extra="allow")

    custom_fields: list[CustomFieldDefinition]


class AggregatedSchemaGetResponse(DevRevResponseModel):
    """DevRev's aggregated schema response envelope."""

    schema_: AggregatedSchema = Field(alias="schema")
