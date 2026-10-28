# AffixIO ADK guard

Fail-closed authorization for Python functions exposed as Google Agent Development Kit tools.

```python
from affixio_adk import AffixIOAuthorizer

auth = AffixIOAuthorizer("aio_...", agent_id="my-agent")

@auth.tool
def update_ticket(ticket_id: str, status: str):
    return update_system(ticket_id, status)
```

Only an explicit `allow` decision executes the function. `deny`, `review`, malformed decisions, and authorization failures do not execute it. The wrapper is compatible with ADK's Python function-tool pattern and does not require private prompts, credentials or operator identity in the decision payload.

Install with `pip install affixio-adk[google]`. The Google ADK dependency is optional because the guard is deliberately a normal callable wrapper, making it easy to test before wiring it into an ADK Agent.
