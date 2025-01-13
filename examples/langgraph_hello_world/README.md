# LangGraph Hello World Example

A simple example demonstrating the basic concepts of LangGraph using a Hello World workflow.

## Overview

This example shows how to:
- Create a basic LangGraph workflow
- Define and connect nodes
- Pass state between nodes
- Execute the graph

## Installation

1. Create and activate a Python virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the example:

```bash
python hello_world.py
```

This will execute the graph and output: "Final output: Hello World"

## Graph Workflow

The graph consists of two nodes:

1. `greeting_node`: Generates the initial "Hello World" message 
2. `output_node`: Formats and returns the final message

State is passed between nodes as a dictionary containing the message.

## Testing

Run the tests:

```bash
python -m unittest test_hello_world.py
```

The tests verify:
- Graph creation
- Execution flow 
- Expected output format and content
