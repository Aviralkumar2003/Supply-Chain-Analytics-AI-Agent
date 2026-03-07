import logging
from typing import Dict

from langchain_core.messages import AIMessage
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from agent.agent_state import State
from config.config import LLM_MODEL
from .prompts import query_gen_prompt
from .table_tool_nodes import (
    SubmitFinalAnswer,
    execute_table_query_tool,
    get_table_schema_tool,
    list_tables_tool,
)

from agent.workflow_steps.table_steps import (
    TableFirstToolStep,
    TableLLMStep,
    TableCaptureSQLStep,
    TableCaptureFinalStep,
)


#Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TableGraph")


#Binding tool to the LLM
llm_with_tools = LLM_MODEL.bind_tools([
    list_tables_tool,
    get_table_schema_tool,
    execute_table_query_tool,
    SubmitFinalAnswer,
])


query_llm_chain = query_gen_prompt | llm_with_tools


#Creating ToolNode
tool_node = ToolNode([
    list_tables_tool,
    get_table_schema_tool,
    execute_table_query_tool,
    SubmitFinalAnswer,
])



class TableGraph:

    def __init__(self):
        self.first_tool_step = TableFirstToolStep()
        self.llm_step = TableLLMStep(query_llm_chain)
        self.capture_sql_step = TableCaptureSQLStep()
        self.capture_final_step = TableCaptureFinalStep()

    def first_tool_call(self, state: State) -> Dict:
        return self.first_tool_step(state)

    def llm_node(self, state: State) -> Dict:
        return self.llm_step(state)

    def capture_sql_query(self, state: State) -> Dict:
        return self.capture_sql_step(state)

    def capture_final_answer(self, state: State):
        return self.capture_final_step(state)

    def route(self, state: State):
        last = state["messages"][-1]

        if isinstance(last, AIMessage) and last.tool_calls:
            if any(tc["name"] == "SubmitFinalAnswer" for tc in last.tool_calls):
                return "tools_final"
            return "tools"

        return END

    def build_graph(self):

        workflow = StateGraph(State)

        #Adding nodes/providing tools to the agent
        workflow.add_node("first_tool_call", self.first_tool_call)
        workflow.add_node("llm", self.llm_node)
        workflow.add_node("tools", tool_node)
        workflow.add_node("tools_final", tool_node)
        workflow.add_node("capture_sql", self.capture_sql_query)
        workflow.add_node("capture_final", self.capture_final_answer)

        #Adding edges and defining the flow of the agent
        workflow.add_edge(START, "first_tool_call")
        workflow.add_edge("first_tool_call", "tools")
        workflow.add_edge("tools", "capture_sql")
        workflow.add_edge("capture_sql", "llm")
        workflow.add_conditional_edges(
            "llm",
            self.route,
            {
                "tools": "tools",
                "tools_final": "tools_final",
                END: END,
            }
        )
        workflow.add_edge("tools_final", "capture_final")
        workflow.add_edge("capture_final", END)

        return workflow.compile()