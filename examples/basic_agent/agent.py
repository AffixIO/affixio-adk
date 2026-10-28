"""Minimal Google ADK agent with an AffixIO-protected function tool."""

import os

from google.adk.agents import LlmAgent

from affixio_adk import AffixIOAuthorizer

authorizer = AffixIOAuthorizer(
    os.environ["AFFIXIO_API_KEY"],
    agent_id=os.getenv("AFFIXIO_AGENT_ID", "google-adk-example"),
)


@authorizer.tool
def lookup_order(order_id: str) -> dict[str, str]:
    """Look up an order after AffixIO authorizes the tool call."""
    return {"order_id": order_id, "status": "ready"}


root_agent = LlmAgent(
    name="affixio_guarded_agent",
    model=os.getenv("GOOGLE_MODEL", "gemini-2.5-flash"),
    instruction="Use lookup_order only when the user asks about an order.",
    tools=[lookup_order],
)
