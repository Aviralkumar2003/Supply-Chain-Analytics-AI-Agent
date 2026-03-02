from agent.table_workflow import TableGraph


agent=TableGraph()
workflow = agent.build_graph()

query={"messages": [("user", "Who are our top 5 customers by total revenue, and what is their fully-loaded margin after COGS and shipping? Rank them by margin dollars, not margin percentage.")]}

response = workflow.invoke(query)

print(response["messages"][-1].content)