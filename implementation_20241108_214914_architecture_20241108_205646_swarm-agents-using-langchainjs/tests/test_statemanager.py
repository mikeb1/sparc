import unittest
from unittest.mock import Mock, patch
from statemanager import StateManager

class TestStateManager(unittest.TestCase):

    def setUp(self):
        self.mock_vector_store = Mock()
        self.state_manager = StateManager(self.mock_vector_store)

    def test_get_state(self):
        # Test getting state for existing conversation
        self.mock_vector_store.get.return_value = {"history": ["hello", "hi"]}
        state = self.state_manager.get_state("test_id")
        self.assertEqual(state, {"history": ["hello", "hi"]})
        self.mock_vector_store.get.assert_called_once_with("test_id")

        # Test getting state for non-existent conversation
        self.mock_vector_store.get.return_value = None
        state = self.state_manager.get_state("new_id")
        self.assertEqual(state, {"history": []})

    def test_set_state(self):
        state = {"history": ["hello", "hi"]}
        self.state_manager.set_state("test_id", state)
        self.mock_vector_store.add.assert_called_once_with("test_id", state)

    def test_update_state(self):
        # Test updating existing state
        self.mock_vector_store.get.return_value = {"history": ["hello"]}
        new_state = self.state_manager.update_state("test_id", "hi")
        self.assertEqual(new_state, {"history": ["hello", "hi"]})
        self.mock_vector_store.add.assert_called_once_with("test_id", {"history": ["hello", "hi"]})

        # Test updating non-existent state
        self.mock_vector_store.get.return_value = None
        new_state = self.state_manager.update_state("new_id", "hi")
        self.assertEqual(new_state, {"history": ["hi"]})
        self.mock_vector_store.add.assert_called_once_with("new_id", {"history": ["hi"]})

    @patch('statemanager.StateManager.get_state')
    def test_get_conversation_history(self, mock_get_state):
        # Test getting history for existing conversation
        mock_get_state.return_value = {"history": ["hello", "hi"]}
        history = self.state_manager.get_conversation_history("test_id")
        self.assertEqual(history, ["hello", "hi"])

        # Test getting history for non-existent conversation
        mock_get_state.return_value = {"history": []}
        history = self.state_manager.get_conversation_history("new_id")
        self.assertEqual(history, [])

if __name__ == '__main__':
    unittest.main()
