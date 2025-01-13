import unittest
from hello_world import run, create_graph

class TestHelloWorld(unittest.TestCase):
    def test_graph_creation(self):
        """Test that the graph is created with correct structure."""
        graph = create_graph()
        self.assertIsNotNone(graph)
        
    def test_execution_flow(self):
        """Test the state changes through graph execution."""
        graph = create_graph()
        result = graph.invoke({})  # Change to use invoke()
        
        # Verify final output format
        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("Final output:"))
        
    def test_hello_world_output(self):
        """Test that the graph produces expected Hello World output."""
        # Run the graph
        result = run()
        
        # Basic output validation
        self.assertIsInstance(result, str)
        
        # Content checks
        self.assertIn("Hello World", result)
        self.assertTrue(result.startswith("Final output:"))
        self.assertEqual(result, "Final output: Hello World")

if __name__ == '__main__':
    unittest.main()
