from app.scout.providers.animedubhub import AnimeDubUpdatesProvider
from app.scout.providers.crunchyroll import CrunchyrollProvider
from app.scout.providers.hidive import HidiveProvider
from app.scout.providers.jikan import JikanProvider


def get_providers():
    return [
        JikanProvider(),
        CrunchyrollProvider(),
        HidiveProvider(),
        AnimeDubUpdatesProvider(),
    ]


def provider_health():
    results = {}

    for provider in get_providers():
        results[provider.name] = provider.health_check()

    return results
