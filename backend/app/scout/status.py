from datetime import datetime


class ScoutStatus:
    def __init__(self):
        self.providers = {}

    def update(self, provider, result):
        self.providers[provider] = {
            "last_run": datetime.utcnow().isoformat(),
            "result": result,
        }

    def snapshot(self):
        return self.providers
