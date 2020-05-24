import random
from .user_agents import USER_AGENTS

class BrowserProfile:
    def __init__(self):
        self.user_agents = USER_AGENTS
        
    @property
    def user_agent(self):
        """
        """
        return random.choice(self.user_agents)

    def headers(self):
        """Returns Requests-ready headers
        """
        return {
            "User-Agent": self.user_agent
        }