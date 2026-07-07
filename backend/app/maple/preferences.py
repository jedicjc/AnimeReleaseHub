class MaplePreferences:
    def __init__(self):
        self.likes = set()
        self.dislikes = set()

    def add_like(self, anime):
        if anime:
            self.likes.add(anime)

    def add_dislike(self, anime):
        if anime:
            self.dislikes.add(anime)

    def summary(self):
        return {
            "likes": sorted(self.likes),
            "dislikes": sorted(self.dislikes),
        }
