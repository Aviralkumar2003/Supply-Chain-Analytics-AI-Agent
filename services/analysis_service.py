from langchain_core.messages import HumanMessage
from agent.table_workflow import TableGraph


class AnalysisService:

    def __init__(self, graph=None):
        self.graph = graph if graph is not None else TableGraph().build_graph()

    def analyze_question_stream(self, question: str):

        query = {
            "messages": [HumanMessage(content=question)]
        }

        final_answer = None
        final_sql = None
        steps = []

        for event in self.graph.stream(query):

            for node, output in event.items():

                if not output:
                    continue

                step = {
                    "node": node,
                    "output": output
                }

                if isinstance(output, dict):

                    if "final_sql" in output:
                        final_sql = output["final_sql"]

                    if "final_answer" in output:
                        final_answer = output["final_answer"]

                steps.append(step)

                yield {
                    "step": step,
                    "steps": steps,
                    "answer": final_answer,
                    "sql": final_sql
                }