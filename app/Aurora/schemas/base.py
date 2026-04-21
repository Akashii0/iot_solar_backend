from pydantic import BaseModel, Field


class UsageDetails(BaseModel):
    input_tokens: int
    output_tokens: int
    total_tokens: int
    requests: int
    tool_calls: int
    reasoning_tokens: int | None


class ProviderDetails(BaseModel):
    name: str
    url: str | None
    response_id: str | None
    finish_reason: str | None
    downstream_provider: str | None


class AuroraChat(BaseModel):
    message: str
    tools_used: list = Field(default_factory=list, description="The list of tools used")
    usage: UsageDetails
    run_id: str
    retries: int
    provider: ProviderDetails
