import os
from google.adk.agents import LlmAgent
from google.adk.tools import VertexAiSearchTool

project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
data_store_id="REPLACE_WITH_YOUR_DATASTORE_ID"
data_store_path=f"projects/{project_id}/locations/global/collections/default_collection/dataStores/{data_store_id}"

vertex_ai_search_tool = VertexAiSearchTool(data_store_id=data_store_path)

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="rag_agent",
    description="Google Cloud の利用規約に関する質問にだけ答えるためのエージェントです。Vertex AI Search を活用し、膨大な利用規約ドキュメントの中から関連性の高い情報を迅速に検索し、ユーザーに分かりやすい言葉で回答を生成します。",
    instruction="""
あなたは Google Cloud の利用規約に精通したアシスタントです。
ユーザーから質問を受けたら、必ず Vertex AI Search ツールを実行して、公式の利用規約ドキュメントに基づいた正確な回答を生成してください。専門的な内容も、いろんな人が理解できるように、丁寧かつ平易な言葉で説明することを心がけてください。
情報が見つからない場合は、推測で答えず、その旨を正直に伝えてください。
ドキュメントに基づくものだけ答えてほしいので他社の規約について聞かれたときは NO と答えましょう。
""",
    tools=[vertex_ai_search_tool],
)
