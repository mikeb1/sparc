from typing import Annotated, TypeVar
from langgraph.graph import StateGraph, END, START

# Define state type for type checking
State = TypeVar("State", bound=dict)

def greeting_node(state: State) -> dict:
    """Generate initial greeting message."""
    return {"message": "Hello World"}

def output_node(state: State) -> str:
    """Format and return final message."""
    return f"Final output: {state['message']}"

def create_graph() -> StateGraph:
    """
    Configure the workflow graph:
    1. greeting_node generates message
    2. output_node formats and returns it
    """
    # Initialize graph with state type
    workflow = StateGraph(State)
    
    # Add nodes
    workflow.add_node("greeting", greeting_node)
    workflow.add_node("output", output_node)
    
    # Connect nodes: greeting -> output
    workflow.add_edge("greeting", "output")
    
    # Set entry and exit points
    workflow.set_entry_point("greeting")
    workflow.set_finish_point("output")
    
    return workflow.compile()

def run() -> str:
    """Execute the graph workflow."""
    graph = create_graph()
    return graph.invoke({})  # Execute with empty initial state

if __name__ == "__main__":
    result = run()
    print(result)
