import random
from .user_agents import USER_AGENTS


class Browser:
    def __init__(self):
        self.user_agents = USER_AGENTS

    @property
    def user_agent(self):
        """
        """
        return random.choice(self.user_agents)

    @property
    def headers(self):
        """Returns Requests-ready headers
        """
        return {"User-Agent": self.user_agent}


class AerisMobileApp:
    @property
    def headers(self):
        """Returns Requests-ready headers
        """
        return {
            "User-Agent": "AerisPulse/1005 CFNetwork/1125.2 Darwin/19.4.0",
            "Referer": "com.hamweather.AerisPulse"
        }
