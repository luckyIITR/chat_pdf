import os
from langgraph.graph import StateGraph, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage
from langchain_core.tools import tool
from app.memory.store import get_vectorstore_for_session
from pydantic import BaseModel

class RetrieveInput(BaseModel):
    query: str
    session_id: str
# Environment variables
from dotenv import load_dotenv
load_dotenv()

os.environ["LANGSMITH_TRACING"] = "true"
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")

# Initialize LLM
llm = init_chat_model("gpt-4o-mini", model_provider="openai")

# Define retrieval tool
@tool(args_schema=RetrieveInput, response_format="content_and_artifact")
def retrieve(query: str, session_id: str):
    """Retrieve information related to a query."""
    vectorstore = get_vectorstore_for_session(session_id)
    if not vectorstore:
        return "No PDF found for this session.", []
    
    docs = vectorstore.similarity_search(query, k=3)
    serialized = "\n\n".join(
        f"Source: {doc.metadata}\nContent: {doc.page_content}" for doc in docs
    )
    return serialized, docs

# Node 1: Decide whether to respond or call a tool
def query_or_respond(state: MessagesState):
    llm_with_tools = llm.bind_tools([retrieve])
    # session_id = state.get("session_id", "default")
    # Ensure session_id is passed in the message metadata
    # for msg in state["messages"]:
    #     if msg.type == "human":
    #         msg.additional_kwargs = {"session_id": session_id}
    # state['messages'][-1].content = "Must use tool!" + state['messages'][-1].content
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

# Node 2: Tool execution
tools_node = ToolNode([retrieve])

# Node 3: Final response after tool
def generate(state: MessagesState):
    # Extract latest tool responses
    recent_tool_messages = []
    for msg in reversed(state["messages"]):
        if msg.type == "tool":
            recent_tool_messages.append(msg)
        else:
            break
    tool_messages = list(reversed(recent_tool_messages))

    context = "\n\n".join(doc.content for doc in tool_messages)
    system_prompt = (
        "You are an assistant for question-answering tasks. "
        "Use the following context to answer the user's question. "
        "If unsure, say you don't know. Keep it concise.\n\n" + context
    )

    conversation = [
        msg for msg in state["messages"]
        if msg.type in ("human", "system") or (msg.type == "ai" and not msg.tool_calls)
    ]

    prompt = [SystemMessage(system_prompt)] + conversation
    response = llm.invoke(prompt)
    return {"messages": [response]}

# Build the graph
graph_builder = StateGraph(MessagesState)
graph_builder.add_node("query_or_respond", query_or_respond)
graph_builder.add_node("tools", tools_node)
graph_builder.add_node("generate", generate)

graph_builder.set_entry_point("query_or_respond")
graph_builder.add_conditional_edges("query_or_respond", tools_condition, {
    END: END,
    "tools": "tools"
})
graph_builder.add_edge("tools", "generate")
graph_builder.add_edge("generate", END)