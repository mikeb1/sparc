import unittest
from unittest.mock import patch
from src.main_app import MainApp

class TestMainApp(unittest.TestCase):
    def setUp(self):
        self.app = MainApp()

    @patch('src.main_app.st')
    def test_initialize_session_state(self, mock_st):
        mock_st.session_state = {}
        self.app.initialize_session_state()
        self.assertIn('project', mock_st.session_state)
        self.assertIn('dark_mode', mock_st.session_state)
