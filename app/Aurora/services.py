from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional
import json

# from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.Aurora.schemas import base
from app.Aurora.utils.instructions import AGENT_INSTRUCTIONS
from app.Device import selectors as device_selectors
from app.Sensor import services as sensor_services
from app.Sensor import formatters as sensor_formatters
from app.core.settings import get_settings
from pydantic_ai.models.openrouter import OpenRouterModel
from pydantic_ai.providers.openrouter import OpenRouterProvider

settings = get_settings()

# DEFAULT_MODEL = "openrouter:nvidia/nemotron-3-nano-30b-a3b:free"

model = OpenRouterModel(
    "nvidia/nemotron-3-nano-30b-a3b:free",
    provider=OpenRouterProvider(api_key=settings.OPENROUTER_API_KEY),
)


@dataclass
class AppDeps:
    db: AsyncSession
    device_id: Optional[int]


class AgentResponse(BaseModel):
    message: str = Field(description="The output message from the LLM")
    used_tool: bool = Field(default=False, description="If a tool was called or not")


class Aurora:
    def __init__(
        self,
        model: Any = model,
        instructions: str = AGENT_INSTRUCTIONS,
        deps_type: Any = AppDeps,
    ):
        self.model = model
        self.instructions = instructions
        self.deps = deps_type

        # Create the agent
        self.agent = Agent(
            self.model,
            deps_type=self.deps,
            instructions=self.instructions,
            # output_type=AgentResponse,
        )

        # Register tools (Battery-specific for now lol.)
        self._register_tools()

    def _register_tools(self):
        """
        Register tools to the agent.
        """

        @self.agent.tool
        async def get_latest_reading(ctx: RunContext[AppDeps]) -> dict:
            """
            Get the latest sensor reading (voltage, current, power, timestamp).
            """
            latest = await sensor_services.fetch_latest_data(
                device_id=ctx.deps.device_id, db=ctx.deps.db
            )
            if not latest:
                return {"error": "No sensor data available"}
            return await sensor_formatters.format_sensor_reading(latest)

        @self.agent.tool
        async def check_load_feasibility(
            ctx: RunContext[AppDeps], load_power_watts: float
        ):
            """
            Check if a given load (in watts) can be safely powered by the battery.
            Returns feasibility status, reason, and estimated runtime if applicable.
            """

            # Get the latest reading
            latest = await sensor_services.fetch_latest_data(
                device_id=ctx.deps.device_id, db=ctx.deps.db
            )

            if not latest:
                return {"error": "Cannot assess feasibility without sensor data."}

            voltage = latest.get("voltage")
            if voltage is None:
                return {"error": "Incomplete sensor data: missing voltage"}

            # TODO Example feasibility logic
            # ! In a real implementation, i will would have to use sensor data
            SOC = 0.78  # placeholder – should come from the SOC model
            nominal_capacity_ah = 100
            nominal_voltage = 12
            max_discharge_current = 50  # A

            load_current = load_power_watts / voltage if voltage else 0

            if load_current > max_discharge_current:
                return {
                    "feasible": False,
                    "reason": f"Load current {load_current:.1f}A exceeds maximum discharge current {max_discharge_current}A",
                }

            eta_dod = 0.5
            eta_inv = 0.9
            usable_wh = SOC * nominal_capacity_ah * nominal_voltage * eta_dod * eta_inv
            if usable_wh <= 0:
                return {"feasible": False, "reason": "Battery is depleted"}

            runtime_hours = usable_wh / load_power_watts if load_power_watts > 0 else 0
            return {
                "feasible": True,
                "reason": "Load is within battery limits",
                "estimated_runtime_hours": round(runtime_hours, 2),
            }

        @self.agent.tool
        async def predict_runtime(ctx: RunContext[AppDeps], load_power_watts: float):
            """
            Predict how long the battery can run a given load (in watts).
            """
            result = await check_load_feasibility(ctx, load_power_watts)
            if "error" in result:
                return f"Error: {result['error']}"
            if not result.get("feasible"):
                return f"Not feasible: {result.get('reason', 'unknown reason')}"
            hours = result.get("estimated_runtime_hours", 0)
            return f"The battery can run a {load_power_watts}W load for approximately {hours} hours."

        @self.agent.tool
        async def get_system_info(ctx: RunContext[AppDeps]):
            """
            Return system or device information (battery type, capacity, etc.).
            """
            device = await device_selectors.get_device_by_id(
                id=ctx.deps.device_id, db=ctx.deps.db
            )

            return {
                "battery_type": "Lead-Acid 12V",
                "device_id": device.id,
                "device_name": device.name,
                "device_mac_address": device.mac_address,
                "device_last_location": device.location,
                "nominal_capacity_ah": 100,
                "nominal_voltage": 12,
                "max_load_capacity_watts": 3500,
                "health_status": "Optimal",
            }

        @self.agent.tool_plain
        async def get_current_time() -> str:
            """
            Return the current date and time.
            """
            now = datetime.now()
            return now.strftime("%I:%M %p, %d %B %Y").lstrip("0")

    async def chat(self, prompt: str, db: AsyncSession, device_id: int):
        """
        Run the agent on a user prompt and return the final output message.
        """
        deps = AppDeps(db=db, device_id=device_id)
        result = await self.agent.run(prompt, deps=deps)

        # Extract tools used from the last response that contains tool calls

        tools_used = []
        for msg in reversed(result._state.message_history):
            if hasattr(msg, "parts"):
                for part in msg.parts:
                    if part.part_kind == "tool-call":
                        tools_used.append(part.tool_name)
            if tools_used:
                break

        # Get usage details
        usage = result._state.usage
        usage_details = base.UsageDetails(
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            total_tokens=usage.input_tokens + usage.output_tokens,
            requests=usage.requests if hasattr(usage, "requests") else 1,
            tool_calls=len(tools_used),
            reasoning_tokens=getattr(usage, "reasoning_tokens", None),
        )

        # Get provider info from the last response (typically index -1)
        provider_name = "unknown"
        provider_url = None
        provider_response_id = None
        finish_reason = None
        downstream_provider = None

        # Find the last response message that has provider details
        for msg in reversed(result._state.message_history):
            if hasattr(msg, "provider_name") and msg.provider_name:
                provider_name = msg.provider_name
                provider_url = getattr(msg, "provider_url", None)
                provider_response_id = getattr(msg, "provider_response_id", None)
                finish_reason = getattr(msg, "finish_reason", None)
                if hasattr(msg, "provider_details") and msg.provider_details:
                    downstream_provider = msg.provider_details.get(
                        "downstream_provider"
                    )
                break

        provider_details = base.ProviderDetails(
            name=provider_name,
            url=provider_url,
            response_id=provider_response_id,
            finish_reason=finish_reason,
            downstream_provider=downstream_provider,
        )

        return base.AuroraChat(
            message=result.output,
            tools_used=tools_used,
            usage=usage_details,
            run_id=result._state.run_id,
            retries=result._state.retries,
            provider=provider_details,
        )

    @staticmethod
    def _encode_sse(event: str, data: dict) -> str:
        return f"event: {event}\ndata: {json.dumps(data)}\n\n"

    async def chat_stream(self, prompt: str, db: AsyncSession, device_id: int):
        """
        Run the agent on a user prompt and return the final streamed output message.
        """
        deps = AppDeps(db=db, device_id=device_id)

        async def stream():
            previous = ""

            async with self.agent.run_stream(prompt, deps=deps) as result:
                async for content in result.stream_text():
                    delta = content[len(previous):]
                    previous = content

                    yield self._encode_sse(
                        "chunk",
                        {
                            "delta": delta,
                            "content": content,
                        },
                    )

                final_output = await result.get_output()
                yield self._encode_sse("done", {"content": final_output})

        return stream()


async def chat_with_aurora(prompt: str, db: AsyncSession, device_id: int):
    """
    Chat with Aurora AI – a wrapper that creates a default Aurora instance.

    Args:
        prompt (str): The prompt message
        db (AsyncSession): The database session
        device_id (int): The device ID to monitor.

    Returns:
        str: The AI response.
    """

    aurora = Aurora()  # uses default model and instructions
    return await aurora.chat(prompt, db, device_id)


async def chat_with_aurora_stream(prompt: str, db: AsyncSession, device_id: int):
    """
    Chat with Aurora AI – a wrapper that creates a default Aurora instance with streaming response.

    Args:
        prompt (str): The prompt message
        db (AsyncSession): The database session
        device_id (int): The device ID to monitor.

    Returns:
        str: The streamed AI response.
    """

    aurora = Aurora()  # uses default model and instructions
    return await aurora.chat_stream(prompt, db, device_id)
