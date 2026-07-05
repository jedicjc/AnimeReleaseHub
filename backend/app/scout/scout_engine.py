from app.scout.importer import ScoutImporter


class ScoutEngine:
    def __init__(self):
        self.importer = ScoutImporter()

    def run(self):
        return {
            "jikan_top": self.importer.import_jikan_top(),
            "jikan_season": self.importer.import_jikan_season(),
            "crunchyroll": self.importer.import_crunchyroll_news(),
            "hidive": self.importer.import_hidive_news(),
        }
