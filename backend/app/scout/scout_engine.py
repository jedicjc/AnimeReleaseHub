from concurrent.futures import ThreadPoolExecutor, as_completed

from app.scout.importer import ScoutImporter
from app.scout.status import ScoutStatus


class ScoutEngine:
    def __init__(self):
        self.importer = ScoutImporter()
        self.status = ScoutStatus()

    def run(self):
        jobs = {
            "jikan_top": lambda: self.importer.import_jikan_top(),
            "jikan_season": lambda: self.importer.import_jikan_season(),
            "crunchyroll": lambda: self.importer.import_crunchyroll_news(),
            "hidive": lambda: self.importer.import_hidive_news(),
        }

        results = {}

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(job): name
                for name, job in jobs.items()
            }

            for future in as_completed(futures):
                name = futures[future]

                try:
                    result = future.result()
                except Exception as exc:
                    result = {
                        "status": "error",
                        "message": str(exc),
                    }

                results[name] = result
                self.status.update(name, result)

        return results
