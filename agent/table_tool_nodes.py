from pydantic import BaseModel, Field
from sqlalchemy import create_engine
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit

from config.config import LLM_MODEL

#Database Setup
db_path = "database/coffee_warehouse.duckdb"
engine = create_engine(f"duckdb:///{db_path}")

sql_db = SQLDatabase(engine)
toolkit = SQLDatabaseToolkit(db=sql_db, llm=LLM_MODEL)
tools = toolkit.get_tools()

# Extract specific tools
list_tables_tool = next(t for t in tools if t.name == "sql_db_list_tables")
get_table_schema_tool = next(t for t in tools if t.name == "sql_db_schema")
execute_table_query_tool = next(t for t in tools if t.name == "sql_db_query")

#Final answer tool
class SubmitFinalAnswer(BaseModel):
    final_answer: str = Field(
        ...,
        description="The final natural language answer to the user's question. "
                    "Must include the SQL query used and a clear explanation."
    )