from app.services.graph_builder import graph_builder  # raw graph builder
from langgraph.checkpoint.memory import MemorySaver

# Enable checkpointing in memory
memory = MemorySaver()

# Compile graph with checkpointing
graph = graph_builder.compile(checkpointer=memory)

# Function to run with checkpointed thread
def run_graph_with_message(session_id, message):
    config = {"configurable": {"thread_id": session_id}}

    # Build the input message format expected by LangGraph
    input_data = {"messages": [{"role": "user", "content": message + "\n session_id: " + session_id + " \n Must USE TOOL!"}]}

    # Invoke the graph (no streaming)
    result = graph.invoke(input_data, config=config)

    # all_msg = []
    # for msg in result.get("messages", []):
    #     all_msg.append({'type': msg['type'], 'content': msg['content']})
    
    # Return final message content
    # print(result)
    return result['messages'][-1].content if "messages" in result else "No response."