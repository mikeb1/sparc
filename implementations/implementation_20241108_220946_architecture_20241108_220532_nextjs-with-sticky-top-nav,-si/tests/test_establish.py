import unittest
from unittest.mock import Mock, patch
from langchain.agents import initialize_agent
from langchain.agents.agent_toolkits import create_python_agent
from langchain.tools import PythonREPLTool
from langchain.python import PythonREPL

class TestEstablish(unittest.TestCase):

    def setUp(self):
        self.agent = create_python_agent(
            llm=Mock(),
            tool=PythonREPLTool(),
            callback_manager=Mock()
        )

    def test_establish_agent(self):
        agent = initialize_agent(self.agent)
        self.assertIsInstance(agent, PythonREPL)

    def test_establish_invalid_agent(self):
        with self.assertRaises(ValueError):
            initialize_agent(None)

    @patch('langchain.agents.agent.AgentExecutor.run')
    def test_establish_execution(self, mock_run):
        agent = initialize_agent(self.agent)
        agent.run("print('hello world')")
        mock_run.assert_called_once()

    def test_establish_callback(self):
        callback = Mock()
        agent = initialize_agent(self.agent, callback_manager=callback)
        agent.run("print('test')")
        callback.assert_called()
