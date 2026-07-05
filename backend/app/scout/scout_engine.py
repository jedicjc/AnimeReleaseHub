from app.scout.importer import ScoutImporter


class ScoutEngine:
    def __init__(self):
        self.importer = ScoutImporter()

    def _safe_run(self, name, func):
        try:
            return func()
        except Exception as error:
            return {
                "provider": name,
                "error": repr(error),
            }

    def run(self):
        return {
            "jikan_top": self._safe_run(
                "jikan_top",
                self.importer.import_jikan_top,
            ),
            "jikan_season": self._safe_run(
                "jikan_season",
                self.importer.import_jikan_season,
            ),
            "crunchyroll": self._safe_run(
                "crunchyroll",
                self.importer.import_crunchyroll_news,
            ),
            "hidive": self._safe_run(
                "hidive",
                self.importer.import_hidive_news,
            ),
        }
