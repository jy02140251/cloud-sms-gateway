"""REST API endpoints for the SMS Cloud Gateway service."""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import Optional, List
import re
import uuid
from datetime import datetime

from .gateway import SMSGateway
from .number_pool import NumberPool

app = FastAPI(
    title="SMS Cloud Gateway API",
    description="High-performance SMS sending and management service",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

gateway = SMSGateway()


class SendSMSRequest(BaseModel):
    phone_number: str = Field(..., description="Target phone number with country code")
    message: str = Field(..., min_length=1, max_length=1600)
    provider: Optional[str] = Field(None, description="Preferred SMS provider")
    priority: int = Field(default=0, ge=0, le=9)

    @validator("phone_number")
    def validate_phone(cls, v):
        pattern = r"^\+?[1-9]\d{6,14}$"
        if not re.match(pattern, v):
            raise ValueError("Invalid phone number format")
        return v


class BulkSMSRequest(BaseModel):
    phone_numbers: List[str] = Field(..., min_items=1, max_items=1000)
    message: str = Field(..., min_length=1, max_length=1600)
    provider: Optional[str] = None


class SMSResponse(BaseModel):
    request_id: str
    status: str
    timestamp: str
    message: Optional[str] = None


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.post("/api/v1/sms/send", response_model=SMSResponse)
async def send_sms(request: SendSMSRequest, background_tasks: BackgroundTasks):
    request_id = str(uuid.uuid4())
    background_tasks.add_task(
        gateway.send_async, request.phone_number, request.message, request.provider
    )
    return SMSResponse(
        request_id=request_id,
        status="queued",
        timestamp=datetime.utcnow().isoformat(),
        message="SMS queued for delivery",
    )


@app.post("/api/v1/sms/bulk", response_model=SMSResponse)
async def send_bulk_sms(request: BulkSMSRequest, background_tasks: BackgroundTasks):
    request_id = str(uuid.uuid4())
    background_tasks.add_task(
        gateway.send_bulk_async, request.phone_numbers, request.message, request.provider
    )
    return SMSResponse(
        request_id=request_id,
        status="bulk_queued",
        timestamp=datetime.utcnow().isoformat(),
        message=f"{len(request.phone_numbers)} messages queued",
    )


@app.get("/api/v1/sms/status/{request_id}")
async def get_sms_status(request_id: str):
    status = gateway.get_status(request_id)
    if not status:
        raise HTTPException(status_code=404, detail="Request not found")
    return status


@app.get("/api/v1/providers")
async def list_providers():
    return {"providers": gateway.list_providers()}