import unittest
from unittest.mock import Mock, patch
from langchain.agents import AgentExecutor
from ..components.continuous import Continuous

class TestContinuous(unittest.TestCase):

    def setUp(self):
        self.agent = Mock(spec=AgentExecutor)
        self.continuous = Continuous(self.agent)

    def test_run(self):
        # Test normal execution
        self.continuous.run()
        self.agent.run.assert_called_once()

    def test_run_with_error(self):
        # Test error handling
        self.agent.run.side_effect = Exception("Test exception")
        with self.assertRaises(Exception):
            self.continuous.run()

    @patch('components.continuous.time.sleep')
    def test_run_loop(self, mock_sleep):
        # Test continuous loop
        self.continuous.stop_event.wait.side_effect = [False, False, True]
        self.continuous.run_loop()
        self.assertEqual(mock_sleep.call_count, 2)
        self.agent.run.call_count == 2

    def test_stop(self):
        # Test stop event
        self.continuous.stop()
        self.assertTrue(self.continuous.stop_event.is_set())

    def test_start(self):
        # Test start creates new thread
        self.continuous.start()
        self.assertIsNotNone(self.continuous.thread)
        self.assertTrue(self.continuous.thread.is_alive())

    def test_join(self):
        # Test join waits for thread
        self.continuous.start()
        self.continuous.stop()
        self.continuous.join()
        self.assertFalse(self.continuous.thread.is_alive())

if __name__ == '__main__':
    unittest.main()
