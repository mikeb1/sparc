import streamlit as st

class UIComponents:
    @staticmethod
    def create_file_browser(file_list):
        selected_file = st.selectbox("Select File", file_list)
        return selected_file

    @staticmethod
    def create_progress_bar():
        progress = st.progress(0)
        status_message = st.empty()
        return progress, status_message

    @staticmethod
    def show_notification(message, type="info"):
        if type == "info":
            st.info(message)
        elif type == "success":
            st.success(message)
        elif type == "warning":
            st.warning(message)
        elif type == "error":
            st.error(message)

    @staticmethod
    def create_modal_dialog(title, content):
        if st.button("Open Dialog"):
            with st.modal(title):
                st.write(content)
                if st.button("Close"):
                    st.session_state['modal_open'] = False
