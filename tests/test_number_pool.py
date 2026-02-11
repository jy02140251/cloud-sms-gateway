"""Tests for Number Pool Manager."""
import pytest
import asyncio
from sms_gateway.number_pool import NumberPool, NumberStatus

@pytest.mark.asyncio
async def test_assign_number():
    pool = NumberPool(daily_limit=20)
    pool.add_number("+14377846365", "telnyx")
    number = await pool.assign_number("+12025551234")
    assert number == "+14377846365"

@pytest.mark.asyncio
async def test_one_to_one_assignment():
    pool = NumberPool(daily_limit=20)
    pool.add_number("+14377846365", "telnyx")
    pool.add_number("+14377847068", "telnyx")
    
    assignments = await pool.assign_batch(["+12025551234", "+12025555678"])
    assert len(assignments) == 2
    assert assignments["+12025551234"] != assignments["+12025555678"]

@pytest.mark.asyncio
async def test_daily_limit():
    pool = NumberPool(daily_limit=2)
    pool.add_number("+14377846365", "telnyx")
    
    await pool.assign_number("+12025551111")
    await pool.assign_number("+12025552222")
    result = await pool.assign_number("+12025553333")
    assert result is None  # Should fail - daily limit reached

@pytest.mark.asyncio
async def test_reset_daily():
    pool = NumberPool(daily_limit=1)
    pool.add_number("+14377846365", "telnyx")
    
    await pool.assign_number("+12025551111")
    await pool.release_number("+14377846365", cooldown=False)
    
    pool.reset_daily_counts()
    result = await pool.assign_number("+12025552222")
    assert result == "+14377846365"  # Should work after reset