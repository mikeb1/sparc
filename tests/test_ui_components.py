import pytest
import streamlit as st
from src.ui_components import UIComponents

def test_create_file_browser():
    file_list = ["file1.py", "file2.py", "file3.py"]
    selected_file = UIComponents.create_file_browser(file_list)
    assert selected_file in file_list

def test_create_progress_bar():
    progress, status_message = UIComponents.create_progress_bar()
    assert progress is not None
    assert status_message is not None

def test_show_notification():
    UIComponents.show_notification("Test message", "info")
    # This test would require a way to verify the notification was shown

def test_create_modal_dialog():
    UIComponents.create_modal_dialog("Test Dialog", "This is a test dialog.")
    # This test would require a way to verify the dialog was created
