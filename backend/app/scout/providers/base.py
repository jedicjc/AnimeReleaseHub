from abc import ABC, abstractmethod


class ScoutProvider(ABC):
    name = "base"
    provider_type = "unknown"

    @abstractmethod
    def fetch(self, limit=25):
        pass

    def health_check(self):
        try:
            items = self.fetch(limit=1)

            if isinstance(items, dict):
                items = items.get("items", [])

            return {
                "provider": self.name,
                "status": "healthy",
                "sample_count": len(items),
            }

        except Exception as error:
            return {
                "provider": self.name,
                "status": "error",
                "message": str(error),
            }
