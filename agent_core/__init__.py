"""通用科研 Agent 核心模块。

使用方式:
    from agent_core import ResearchAgent, OPENAI_TOOLS, TOOL_HANDLERS

    agent = ResearchAgent(
        api_key="...",
        base_url="...",
        model="...",
        tools=OPENAI_TOOLS,
        tool_handlers=TOOL_HANDLERS,
        system_prompt=build_system_prompt(),
    )
    await agent.run_iterations(research_goal="...", max_iterations=3)
"""

from agent_core.engine import ResearchAgent
from agent_core.tools import OPENAI_TOOLS, TOOL_HANDLERS

__all__ = ["ResearchAgent", "OPENAI_TOOLS", "TOOL_HANDLERS"]