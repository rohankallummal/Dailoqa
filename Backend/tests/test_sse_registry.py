import asyncio

import pytest

from app.sse.registry import SseRegistry


@pytest.mark.asyncio
async def test_publish_reaches_only_matching_user():
    reg = SseRegistry()
    a = reg.subscribe("sub-1")
    b = reg.subscribe("sub-2")
    await reg.publish("sub-1", {"type": "delta", "text": "hi"})
    got = await asyncio.wait_for(a.get(), timeout=1)
    assert got == {"type": "delta", "text": "hi"}
    assert b.empty()
    reg.unsubscribe("sub-1", a)


@pytest.mark.asyncio
async def test_multiple_subscribers_same_user_both_receive():
    reg = SseRegistry()
    a = reg.subscribe("sub-1")
    b = reg.subscribe("sub-1")
    await reg.publish("sub-1", {"type": "notification"})
    assert (await asyncio.wait_for(a.get(), 1))["type"] == "notification"
    assert (await asyncio.wait_for(b.get(), 1))["type"] == "notification"


@pytest.mark.asyncio
async def test_active_user_subs_tracks_membership():
    reg = SseRegistry()
    assert reg.active_user_subs() == []
    a = reg.subscribe("sub-1")
    assert reg.active_user_subs() == ["sub-1"]
    reg.unsubscribe("sub-1", a)
    assert reg.active_user_subs() == []
