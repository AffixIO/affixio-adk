import asyncio
import pytest

from affixio_adk import AffixIOAuthorizer, AffixIOBlocked, AffixIODecision


def test_allow_executes_tool():
    async def run():
        guard = AffixIOAuthorizer("test", agent_id="agent")
        guard.decide = lambda *a, **k: _decision("allow")

        @guard.tool
        def add(a, b):
            return a + b

        assert await add(2, 3) == 5

    asyncio.run(run())


@pytest.mark.parametrize("decision", ["deny", "review", "unexpected"])
def test_only_allow_executes(decision):
    async def run():
        guard = AffixIOAuthorizer("test", agent_id="agent")
        guard.decide = lambda *a, **k: _decision(decision)

        @guard.tool
        def dangerous():
            raise AssertionError("must not execute")

        with pytest.raises(AffixIOBlocked):
            await dangerous()

    asyncio.run(run())


def test_sync_tool_is_awaitable_and_runs_once():
    async def run():
        guard = AffixIOAuthorizer("test", agent_id="agent")
        calls = []
        guard.decide = lambda *a, **k: _decision("allow")

        @guard.tool
        def record(value):
            calls.append(value)
            return value

        assert await record("one") == "one"
        assert calls == ["one"]

    asyncio.run(run())


def _decision(value):
    async def result(*args, **kwargs):
        return AffixIODecision(value, {})
    return result()
