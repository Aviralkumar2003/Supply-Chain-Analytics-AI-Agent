import uuid
from langchain_core.messages import AIMessage
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
        last = state["messages"][-1]
        if last.type == "tool" and last.name == "sql_db_query":
            previous_ai = state["messages"][-2]
            if previous_ai.tool_calls:
                for call in previous_ai.tool_calls:
                    if call["name"] == "sql_db_query":
                        return {"final_sql": call["args"]["query"]}
        return {}

class TableCaptureFinalStep:
    def __call__(self, state: State):
        last = state["messages"][-1]
        if last.type == "tool" and last.name == "SubmitFinalAnswer":
            previous_ai = state["messages"][-2]
            if previous_ai.tool_calls:
                for call in previous_ai.tool_calls:
                    if call["name"] == "SubmitFinalAnswer":
                        return {"final_answer": call["args"]["final_answer"]}
        return {}
