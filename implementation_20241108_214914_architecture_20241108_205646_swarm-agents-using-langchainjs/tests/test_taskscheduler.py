import unittest
from unittest.mock import Mock, patch
from langchain.agents import AgentExecutor
from ..src.taskscheduler import TaskScheduler

class TestTaskScheduler(unittest.TestCase):

    def setUp(self):
        self.mock_agent = Mock(spec=AgentExecutor)
        self.scheduler = TaskScheduler(self.mock_agent)

    def test_schedule_task(self):
        task = Mock()
        self.scheduler.schedule_task(task)
        self.mock_agent.run.assert_called_once_with(task)

    def test_schedule_multiple_tasks(self):
        tasks = [Mock(), Mock(), Mock()]
        for task in tasks:
            self.scheduler.schedule_task(task)
        self.assertEqual(self.mock_agent.run.call_count, len(tasks))

    def test_schedule_task_with_callback(self):
        callback = Mock()
        task = Mock()
        self.scheduler.schedule_task(task, callback=callback)
        self.mock_agent.run.assert_called_once_with(task)
        self.mock_agent.run.return_value.addCallback.assert_called_once_with(callback)

    def test_schedule_task_with_callback_error(self):
        callback = Mock(side_effect=Exception("Test error"))
        task = Mock()
        with self.assertRaises(Exception):
            self.scheduler.schedule_task(task, callback=callback)

    @patch('langchain.agents.AgentExecutor')
    def test_agent_initialization_error(self, mock_agent_class):
        mock_agent_class.side_effect = Exception("Failed to initialize agent")
        with self.assertRaises(Exception):
            TaskScheduler(mock_agent_class)

if __name__ == '__main__':
    unittest.main()
