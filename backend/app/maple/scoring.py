def calculate_maple_score(anime):
    trend = anime.trend_score or 0
    mal_score = anime.score or 0
    popularity = anime.popularity or 999999
    favorites = anime.favorites or 0
    members = anime.members or 0
    rank = anime.rank or 999999

    score = 0

    # Trend is strongest signal
    score += trend * 0.35

    # MAL score
    score += mal_score * 4

    # Popularity: lower number is better
    if popularity < 1000:
        score += 12
    elif popularity < 5000:
        score += 7
    elif popularity < 10000:
        score += 3

    # Rank: lower number is better
    if rank < 500:
        score += 10
    elif rank < 2000:
        score += 5

    # Community interest
    if members > 100000:
        score += 8
    elif members > 25000:
        score += 4

    if favorites > 10000:
        score += 6
    elif favorites > 1000:
        score += 3

    # Upcoming boost
    if anime.status == "upcoming":
        score += 8

    # Trailer boost
    if anime.trailer_url:
        score += 4

    return round(min(score, 99), 2)
