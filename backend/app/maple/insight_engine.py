class MapleInsightEngine:
    def __init__(self, anime=None, news=None, dashboard=None):
        self.anime = anime
        self.news = news or []
        self.dashboard = dashboard or {}

    def anime_summary(self):
        if not self.anime:
            return "No anime data available yet."

        title = self.anime.title
        trend = self.anime.trend_score or 0
        maple = self.anime.maple_score or 0
        score = self.anime.score or 0

        reasons = []

        if maple >= 90:
            reasons.append("Maple considers this one of the strongest titles right now")
        elif maple >= 70:
            reasons.append("Maple sees strong potential in this title")
        else:
            reasons.append("Maple is still watching this title for more signals")

        if trend >= 60:
            reasons.append("it has strong trend momentum")
        elif trend >= 30:
            reasons.append("it is gaining steady attention")

        if score >= 8:
            reasons.append("community ratings are very strong")

        if self.anime.trailer_url:
            reasons.append("an official trailer is available")

        if self.news:
            reasons.append(f"{len(self.news)} related news update(s) are attached")

        return f"{title} stands out because " + ", ".join(reasons) + "."

    def score_explanation(self):
        if not self.anime:
            return []

        explanations = []

        if (self.anime.trend_score or 0) > 0:
            explanations.append("Trend momentum contributes to the Maple Score.")

        if self.anime.score:
            explanations.append("Community rating is included in the score.")

        if self.anime.popularity:
            explanations.append("Popularity ranking helps measure broad interest.")

        if self.anime.members:
            explanations.append("Member count reflects audience awareness.")

        if self.anime.favorites:
            explanations.append("Favorites reflect stronger fan attachment.")

        if self.anime.status == "upcoming":
            explanations.append("Upcoming titles receive a discovery boost.")

        if self.anime.trailer_url:
            explanations.append("Trailer availability increases confidence.")

        return explanations

    def score_breakdown(self):
        if not self.anime:
            return {}

        trend = min(5, round((self.anime.trend_score or 0) / 20))
        rating = min(5, round((self.anime.score or 0) / 2))
        popularity = 5 if (self.anime.popularity or 999999) < 5000 else 3
        members = 5 if (self.anime.members or 0) > 100000 else 3
        news = min(5, len(self.news))
        trailer = 5 if self.anime.trailer_url else 2

        return {
            "Trend Momentum": trend,
            "Community Rating": rating,
            "Popularity": popularity,
            "Community Size": members,
            "News Activity": news,
            "Trailer Confidence": trailer,
        }

    def dashboard_insight(self):
        trending = self.dashboard.get("trending", [])
        highest = self.dashboard.get("highest_rated", [])
        news = self.dashboard.get("latest_news", [])

        if not trending:
            return "Maple is waiting for more anime activity before generating today's insight."

        top = trending[0]
        top_title = getattr(top, "title", "the current top title")

        parts = [
            f"{top_title} is leading today's trend activity."
        ]

        if highest:
            highest_title = getattr(highest[0], "title", "a highly rated title")
            parts.append(f"{highest_title} currently has one of the strongest community ratings.")

        if news:
            parts.append(f"Maple Scout detected {len(news)} recent news update(s).")

        return " ".join(parts)
