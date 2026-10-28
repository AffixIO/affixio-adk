from __future__ import annotations

import inspect
from dataclasses import dataclass
from functools import wraps
from typing import Any, Awaitable, Callable, TypeVar

import httpx

T = TypeVar("T")


@dataclass(frozen=True)
class AffixIODecision:
    decision: str
    evidence: dict[str, Any]

    @property
    def allowed(self) -> bool:
        return self.decision.lower() == "allow"


class AffixIOBlocked(RuntimeError):
    def __init__(self, decision: AffixIODecision):
        super().__init__(f"AffixIO blocked tool execution: {decision.decision}")
        self.decision = decision


class AffixIOAuthorizer:
    """Guard ordinary Python callables, which Google ADK can expose as tools."""

    def __init__(self, api_key: str, *, agent_id: str, base_url: str = "https://api.affix-io.com", timeout: float = 8.0, fail_closed: bool = True):
        self.api_key, self.agent_id = api_key, agent_id
        self.base_url, self.timeout, self.fail_closed = base_url.rstrip("/"), timeout, fail_closed

    async def decide(self, tool_name: str, tool_input: Any) -> AffixIODecision:
        payload = {"agent_id": self.agent_id, "action_type": "adk_tool_call", "tool_name": tool_name, "tool_input": tool_input}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/v1/sdk2/actions/decide", json=payload, headers={"X-API-Key": self.api_key})
                response.raise_for_status()
                body = response.json()
                return AffixIODecision(str(body.get("decision", "deny")), body)
        except Exception:
            if self.fail_closed:
                raise
            return AffixIODecision("deny", {"reason": "authorization_unavailable"})

    def tool(self, fn: Callable[..., T]) -> Callable[..., T] | Callable[..., Awaitable[T]]:
        name = fn.__name__

        @wraps(fn)
        async def guarded(*args: Any, **kwargs: Any) -> Any:
            decision = await self.decide(name, {"args": list(args), "kwargs": kwargs})
            if not decision.allowed:
                raise AffixIOBlocked(decision)
            result = fn(*args, **kwargs)
            return await result if inspect.isawaitable(result) else result

        return guarded
