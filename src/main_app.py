class MainApp:
    def __init__(self):
        self.session_state = self.initialize_session_state()
        self.theme = self.setup_theme()
        self.sidebar = self.create_sidebar()

    def initialize_session_state(self):
        return {"project": None, "dark_mode": True}

    def setup_theme(self):
        return "dark"

    def create_sidebar(self):
        return ["Project", "Code", "Tests", "Settings"]
