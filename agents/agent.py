import os
from adk.adk import ADK
from adk.config import ToolConfig
from adk.tools import VertexAiSearchTool

engine_id = os.environ.get("ENGINE_ID")
if not engine_id:
    raise ValueError("ENGINE_ID environment variable must be set.")

tool_config = ToolConfig(
    [VertexAiSearchTool(engine_id=engine_id)]
)

if __name__ == "__main__":
    ADK(tool_config=tool_config).run()