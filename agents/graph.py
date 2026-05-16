from typing import Any, TypedDict
from langgraph.graph import StateGraph, END

from agents.planner import planner_node
from agents.sql_generator import sql_generator_node
from agents.governance import governance_node


class AgentState(TypedDict):
    user_question: str
    plan: str
    generated_sql: str
    governance_result: str
    query_result: list[dict]
    answer: str


def build_graph() -> Any:
    graph = StateGraph(AgentState)
    graph.add_node("planner", planner_node)
    graph.add_node("sql_generator", sql_generator_node)
    graph.add_node("governance", governance_node)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "sql_generator")
    graph.add_edge("sql_generator", "governance")
    graph.add_edge("governance", END)

    return graph.compile()


# Singleton compiled graph — import this in other modules
app = build_graph()


def run_query_pipeline(question: str) -> AgentState:
    initial_state: AgentState = {
        "user_question": question,
        "plan": "",
        "generated_sql": "",
        "governance_result": "",
        "query_result": [],
        "answer": "",
    }
    return app.invoke(initial_state)


if __name__ == "__main__":
    result = run_query_pipeline("How many high-risk claims are still open?")
    print("Plan:", result["plan"])
    print("\nSQL:", result["generated_sql"])
    print("\nGovernance:", result["governance_result"])
    print("\nRows:", result["query_result"])
