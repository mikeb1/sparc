import unittest
from unittest.mock import Mock, patch
from langchain.agents import AgentExecutor
from ..src.monitoringservice import MonitoringService

class TestMonitoringService(unittest.TestCase):

    def setUp(self):
        self.mock_agent = Mock(spec=AgentExecutor)
        self.service = MonitoringService(self.mock_agent)

    def test_start_monitoring(self):
        self.service.start_monitoring()
        self.mock_agent.run.assert_called_once()

    def test_stop_monitoring(self):
        self.service.stop_monitoring()
        self.mock_agent.stop.assert_called_once()

    @patch('langchain.agents.AgentExecutor')
    def test_initialize_with_tools(self, mock_executor):
        tools = ['tool1', 'tool2']
        service = MonitoringService.initialize(tools)
        mock_executor.assert_called_once_with(tools)
        self.assertIsInstance(service, MonitoringService)

    def test_handle_event_success(self):
        event = {'type': 'success', 'data': 'Task completed'}
        self.service.handle_event(event)
        self.mock_agent.run.assert_called_once()

    def test_handle_event_failure(self):
        event = {'type': 'failure', 'data': 'Task failed'}
        self.service.handle_event(event)
        self.mock_agent.run.assert_not_called()

    def test_handle_event_unknown(self):
        event = {'type': 'unknown'}
        with self.assertRaises(ValueError):
            self.service.handle_event(event)

if __name__ == '__main__':
    unittest.main()
