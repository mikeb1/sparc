import unittest
from unittest.mock import Mock, patch
from langchain.agents import AgentManager

class TestAgentManager(unittest.TestCase):

    def setUp(self):
        self.tools = [Mock(), Mock()]
        self.agent = Mock()
        self.manager = AgentManager(self.tools, self.agent)

    def test_initialize(self):
        self.assertEqual(self.manager.tools, self.tools)
        self.assertEqual(self.manager.agent, self.agent)

    def test_run_single_action(self):
        action = Mock()
        self.manager.run([action])
        action.tool.assert_called_once()

    def test_run_multiple_actions(self):
        actions = [Mock(), Mock()]
        self.manager.run(actions)
        actions[0].tool.assert_called_once()
        actions[1].tool.assert_called_once()

    def test_run_with_callback(self):
        callback = Mock()
        action = Mock()
        self.manager.run([action], callback=callback)
        action.tool.assert_called_once()
        callback.assert_called_once()

    @patch('langchain.agents.AgentManager.agent')
    def test_get_next_action(self, mock_agent):
        mock_agent.return_value = 'test action'
        action = self.manager.get_next_action('test query')
        self.assertEqual(action, 'test action')
        mock_agent.assert_called_once_with('test query')

    def test_get_next_action_with_error(self):
        self.manager.agent.get_next_action = Mock(side_effect=Exception('test error'))
        with self.assertRaises(Exception):
            self.manager.get_next_action('test query')

    def test_run_loop(self):
        actions = [Mock(), Mock()]
        self.manager.agent.get_next_action = Mock(side_effect=actions + [None])
        self.manager.run_loop('test query')
        actions[0].tool.assert_called_once()
        actions[1].tool.assert_called_once()

    def test_run_loop_with_callback(self):
        callback = Mock()
        actions = [Mock(), Mock()]
        self.manager.agent.get_next_action = Mock(side_effect=actions + [None])
        self.manager.run_loop('test query', callback=callback)
        actions[0].tool.assert_called_once()
        actions[1].tool.assert_called_once()
        callback.assert_called_once()

if __name__ == '__main__':
    unittest.main()
