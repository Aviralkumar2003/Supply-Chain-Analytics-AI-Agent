from typing import Annotated, TypedDict, Optional
from langchain.messages import AnyMessage
from langgraph.graph import add_messages


class State(TypedDict, total=False):
    messages: Annotated[list[AnyMessage], add_messages]
    final_sql: Optional[str]
    final_answer: Optional[str]