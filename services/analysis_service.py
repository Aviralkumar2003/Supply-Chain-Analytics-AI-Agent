from agent.table_workflow import TableGraph


class AnalysisService:

    def __init__(self, graph=None):
        self.graph = graph if graph is not None else TableGraph().build_graph()

    def analyze_question(self, question: str):
        query = {
            "messages": [("user", question)]
        }
        result = self.graph.invoke(query)
        return {
            "answer": result.get("final_answer"),
            "sql": result.get("final_sql")
        }