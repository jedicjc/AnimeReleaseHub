from concurrent.futures import ThreadPoolExecutor, as_completed

from app.scout.importer import ScoutImporter
from app.scout.provider_registry import get_providers


class ScoutEngine:
    def __init__(self):
        self.importer = ScoutImporter()
        self.providers = get_providers()

    def _run_provider(self, provider):
        if provider.provider_type == "anime":
            imported = 0

            items = provider.fetch(limit=25)

            for item in items:
                data = self.importer.normalizer.normalize_jikan_anime(item)

                db = self.importer.get_db()

                try:
                    anime = self.importer.upsert_anime(db, data)

                    if anime:
                        imported += 1

                    db.commit()

                finally:
                    db.close()

            return imported

        if provider.provider_type == "news":
            imported = 0

            items = provider.fetch(limit=25)

            db = self.importer.get_db()

            try:
                for item in items:
                    data = self.importer.normalizer.normalize_news(item)

                    article = self.importer.save_news_article(
                        db,
                        data,
                    )

                    if article:
                        imported += 1

                db.commit()

            finally:
                db.close()

            return imported

        return 0

    def run(self):
        results = {}

        with ThreadPoolExecutor(max_workers=len(self.providers)) as executor:
            futures = {
                executor.submit(
                    self._run_provider,
                    provider,
                ): provider.name
                for provider in self.providers
            }

            for future in as_completed(futures):
                provider = futures[future]

                try:
                    results[provider] = {
                        "status": "success",
                        "imported": future.result(),
                    }

                except Exception as exc:
                    results[provider] = {
                        "status": "error",
                        "error": str(exc),
                    }

        return results
