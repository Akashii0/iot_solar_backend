import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
from typing import Dict
import json

router = APIRouter(tags=["Relay Control"])


# Store active WebSocket connections per device_id
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.pending_requests: Dict[str, asyncio.Future] = {}

    async def connect(self, device_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[device_id] = websocket
        print("Active connections:", list(self.active_connections.keys()))
        print(f"Device {device_id} connected")

    def disconnect(self, device_id: str):
        if device_id in self.active_connections:
            del self.active_connections[device_id]
            print(f"Device {device_id} disconnected")

    async def send_command(self, device_id: str, command: dict):
        if device_id not in self.active_connections:
            raise HTTPException(
                status_code=404, detail=f"Device {device_id} not connected"
            )
        try:
            await self.active_connections[device_id].send_json(command)
        except Exception:
            self.disconnect(device_id)
            raise HTTPException(status_code=500, detail="Failed to send command")

    async def send_command_and_await_response(
        self, device_id: str, command: dict, timeout: float = 5.0
    ) -> dict:
        if device_id not in self.active_connections:
            raise HTTPException(404, f"Device {device_id} not connected")

        # Create a Future for this request
        future = asyncio.get_event_loop().create_future()
        self.pending_requests[device_id] = future

        try:
            # Send the command
            await self.active_connections[device_id].send_json(command)
            # Wait for the response (with timeout)
            response = await asyncio.wait_for(future, timeout=timeout)
            return response
        except asyncio.TimeoutError:
            raise HTTPException(504, f"Device {device_id} did not respond in time")
        finally:
            # Clean up pending request
            self.pending_requests.pop(device_id, None)

    def fulfill_pending_request(self, device_id: str, message: str):
        """Called when a message arrives from the device. If matching a pending request, resolve it."""
        if (
            device_id in self.pending_requests
            and not self.pending_requests[device_id].done()
        ):
            try:
                data = json.loads(message)
                self.pending_requests[device_id].set_result(data)
            except json.JSONDecodeError as e:
                # Not JSON – ignore
                print(e)
                pass


manager = ConnectionManager()


# --- WebSocket endpoint for ESP32 ---


@router.get("/debug/connections")
async def list_connections():
    return {
        "active": list(manager.active_connections.keys()),
        "req": list(manager.pending_requests.keys()),
    }


@router.websocket("/ws/{device_id}")
async def websocket_relay(websocket: WebSocket, device_id: str):
    await manager.connect(device_id, websocket)
    try:
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30)
                print(f"Received from {device_id}: {data}")
                # Let the manager know a message arrived – may resolve a pending request
                manager.fulfill_pending_request(device_id, data)
            except asyncio.TimeoutError:
                # keep connection alive even if ESP sends nothing
                await websocket.send_text("ping")
    except WebSocketDisconnect:
        manager.disconnect(device_id)


# --- HTTP endpoints to control relays ---
class RelayState(BaseModel):
    state: str  # "ON" or "OFF"


@router.post("/{device_id}/power")
async def control_power(device_id: str, command: RelayState):
    """
    Turn the main power relay ON or OFF.
    """
    if command.state not in ["ON", "OFF"]:
        raise HTTPException(status_code=400, detail="State must be 'ON' or 'OFF'")
    await manager.send_command(device_id, {"relayPowerState": command.state})
    return {"status": "ok", "device": device_id, "command": f"power {command.state}"}


@router.post("/{device_id}/appliance")
async def control_appliance(device_id: str, command: RelayState):
    """Turn the appliance relay ON or OFF."""
    if command.state not in ["ON", "OFF"]:
        raise HTTPException(status_code=400, detail="State must be 'ON' or 'OFF'")
    await manager.send_command(device_id, {"relayApplianceState": command.state})
    return {
        "status": "ok",
        "device": device_id,
        "command": f"appliance {command.state}",
    }


@router.get("/{device_id}/status")
async def get_connection_status(device_id: str):
    """Check if device is connected via WebSocket."""
    connected = device_id in manager.active_connections
    return {"device_id": device_id, "connected": connected}


@router.get("/{device_id}/states")
async def get_relay_states(device_id: str):
    """
    Send a 'get_states' command to the ESP and wait for its response.
    Expected ESP response: {"relayPowerState": "ON/OFF", "relayApplianceState": "ON/OFF"}
    """
    response = await manager.send_command_and_await_response(
        device_id, {"command": "get_states"}, timeout=5.0
    )
    power = response.get("relayPowerState", "UNKNOWN")
    appliance = response.get("relayApplianceState", "UNKNOWN")
    return {"device_id": device_id, "power": power, "appliance": appliance}
