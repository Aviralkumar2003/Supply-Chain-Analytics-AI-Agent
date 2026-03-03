import uuid
from langchain_core.messages import AIMessage, ToolMessage
from agent.agent_state import State

class TableFirstToolStep:
    def __call__(self, state: State):
        call_id = f"list_tables_{uuid.uuid4().hex[:8]}"
        return {
            "messages": [
                AIMessage(
                    content="",
                    tool_calls=[{
                        "name": "sql_db_list_tables",
                        "args": {},
                        "id": call_id,
                    }]
                )
            ]
        }

class TableLLMStep:
    def __init__(self, query_llm_chain):
        self.query_llm_chain = query_llm_chain
    def __call__(self, state: State):
        response = self.query_llm_chain.invoke({"messages": state["messages"]})
        return {"messages": [response]}

class TableCaptureSQLStep:
    def __call__(self, state: State):
        messages = state["messages"]

        # We only care if last message is a sql_db_query tool result
        last = messages[-1]

        if not isinstance(last, ToolMessage):
            return {}

        if last.name != "sql_db_query":
            return {}

        # Walk backwards to find the AIMessage that triggered this tool call
        for msg in reversed(messages[:-1]):
            if isinstance(msg, AIMessage) and msg.tool_calls:
                for call in msg.tool_calls:
                    if call["name"] == "sql_db_query":
                        return {"final_sql": call["args"]["query"]}

        return {}

class TableCaptureFinalStep:
    def __call__(self, state: State):
        messages = state["messages"]
        last = messages[-1]

        if not isinstance(last, ToolMessage):
            return {}

        if last.name != "SubmitFinalAnswer":
            return {}

        # Walk backwards to find AIMessage that triggered final answer tool
        for msg in reversed(messages[:-1]):
            if isinstance(msg, AIMessage) and msg.tool_calls:
                for call in msg.tool_calls:
                    if call["name"] == "SubmitFinalAnswer":
                        return {
                            "final_answer": call["args"]["final_answer"]
                        }

        return {}
