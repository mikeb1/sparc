import unittest
from unittest.mock import Mock, patch
from langchain.agents import AgentManager

class TestAgentManager(unittest.TestCase):

    def setUp(self):
        self.mock_agent1 = Mock()
        self.mock_agent2 = Mock()
        self.agents = [self.mock_agent1, self.mock_agent2]

    def test_init(self):
        manager = AgentManager(self.agents)
        self.assertEqual(manager.agents, self.agents)

    def test_add_agent(self):
        manager = AgentManager([])
        mock_agent = Mock()
        manager.add_agent(mock_agent)
        self.assertIn(mock_agent, manager.agents)

    def test_remove_agent(self):
        manager = AgentManager(self.agents)
        manager.remove_agent(self.mock_agent1)
        self.assertNotIn(self.mock_agent1, manager.agents)
        self.assertIn(self.mock_agent2, manager.agents)

    @patch('langchain.agents.AgentManager.delegate_to_agents')
    def test_run(self, mock_delegate):
        manager = AgentManager(self.agents)
        query = "test query"
        manager.run(query)
        mock_delegate.assert_called_once_with(query)

    @patch('langchain.agents.AgentManager.delegate_to_agents')
    def test_delegate_to_agents(self, mock_delegate):
        manager = AgentManager(self.agents)
        query = "test query"
        result = manager.delegate_to_agents(query)
        for agent in self.agents:
            agent.run.assert_called_once_with(query)
        self.assertEqual(result, [agent.run(query) for agent in self.agents])

    def test_delegate_to_agents_empty(self):
        manager = AgentManager([])
        query = "test query"
        result = manager.delegate_to_agents(query)
        self.assertEqual(result, [])

    def test_delegate_to_agents_error(self):
        mock_error_agent = Mock(side_effect=Exception("Test error"))
        manager = AgentManager([mock_error_agent])
        query = "test query"
        with self.assertRaises(Exception):
            manager.delegate_to_agents(query)

if __name__ == '__main__':
    unittest.main()
