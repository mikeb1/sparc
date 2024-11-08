import unittest
from unittest.mock import Mock, patch
from langchain.agents import AgentExecutor
from ..src.communication_service import CommunicationService

class TestCommunicationService(unittest.TestCase):

    def setUp(self):
        self.mock_agent = Mock(spec=AgentExecutor)
        self.service = CommunicationService(self.mock_agent)

    def test_send_message(self):
        message = "Hello, world!"
        response = self.service.send_message(message)
        self.mock_agent.run.assert_called_once_with(message)
        self.assertEqual(response, self.mock_agent.run.return_value)

    def test_send_message_empty(self):
        with self.assertRaises(ValueError):
            self.service.send_message("")

    @patch('builtins.print')
    def test_print_response(self, mock_print):
        response = "This is a test response."
        self.service.print_response(response)
        mock_print.assert_called_once_with(response)

    def test_print_response_none(self):
        with self.assertLogs() as captured:
            self.service.print_response(None)
            self.assertEqual(len(captured.records), 1)
            self.assertEqual(captured.records[0].message, "Response was None")

    def test_run_agent(self):
        message = "What is the meaning of life?"
        expected_response = "42"
        self.mock_agent.run.return_value = expected_response

        response = self.service.run_agent(message)

        self.mock_agent.run.assert_called_once_with(message)
        self.assertEqual(response, expected_response)

    def test_run_agent_empty_message(self):
        with self.assertRaises(ValueError):
            self.service.run_agent("")
