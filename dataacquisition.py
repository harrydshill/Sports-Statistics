import os
import requests
import numpy as np

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://api.sportsgameodds.com/v1"

def odds_to_probability(american_odds):
    if american_odds is None or american_odds == 0:
        return 0.0
    if american_odds > 0:
        decimal = 1.0 + (american_odds / 100.0)
    else:
        decimal = 1.0 + (100.0 / abs(american_odds))
    return 1.0 / decimal

def list_sports():
    url = f"{BASE_URL}/sports"
    headers = {"X-API-Key": API_KEY}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get("data", [])

def list_leagues(sport):
    url = f"{BASE_URL}/leagues"
    headers = {"X-API-Key": API_KEY}
    params = {"sport": sport}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json().get("data", [])

def list_seasons(sport, league):
    url = f"{BASE_URL}/seasons"
    headers = {"X-API-Key": API_KEY}
    params = {"sport": sport, "league": league}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json().get("data", [])

def list_events(sport, league, season=None, status="scheduled"):
    url = f"{BASE_URL}/events"
    headers = {"X-API-Key": API_KEY}
    params = {"sport": sport, "league": league, "status": status}
    if season:
        params["season"] = season
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json().get("data", [])

def get_event(event_id):
    url = f"{BASE_URL}/events/{event_id}"
    headers = {"X-API-Key": API_KEY}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def extract_correct_score_matrix(event_data, bookmaker_name="auto", matrix_size=10):
    prob_matrix = np.zeros((matrix_size, matrix_size))
    odds_lines = event_data.get("odds", [])
    if not odds_lines:
        print("Warning: No odds found.")
        return prob_matrix, None, 0.0

    if bookmaker_name != "auto":
        odds_lines = [o for o in odds_lines if o.get("bookmaker") == bookmaker_name]
        if not odds_lines:
            print(f"Warning: Bookmaker '{bookmaker_name}' not found.")
            return prob_matrix, None, 0.0
        bookmaker_used = bookmaker_name
    else:
        bookmaker_used = odds_lines[0].get("bookmaker", "unknown")

    correct_score_lines = []
    for line in odds_lines:
        if line.get("bookmaker") != bookmaker_used:
            continue
        if line.get("market") == "correct_score":
            correct_score_lines.append(line)

    if not correct_score_lines:
        print(f"Warning: No 'correct_score' market for {bookmaker_used}.")
        return prob_matrix, bookmaker_used, 0.0

    for line in correct_score_lines:
        score_str = line.get("line", "")
        if "-" not in score_str:
            continue
        try:
            home_goals, away_goals = map(int, score_str.split("-"))
        except ValueError:
            continue
        if home_goals >= matrix_size or away_goals >= matrix_size:
            continue

        american_odds = line.get("homeOdds")
        if american_odds is None:
            continue

        prob_matrix[away_goals, home_goals] = odds_to_probability(american_odds)

    overround_sum = np.sum(prob_matrix)
    return prob_matrix, bookmaker_used, overround_sum

def select_from_list(items, display_key, prompt):
    if not items:
        print("No items found.")
        return None
    print("\n" + "=" * 50)
    for i, item in enumerate(items):
        name = item.get(display_key, "Unknown")
        print(f"{i+1:3}. {name}")
    print("=" * 50)
    while True:
        try:
            choice = input(f"{prompt} (enter number): ")
            if choice.strip() == "":
                return None
            idx = int(choice) - 1
            if 0 <= idx < len(items):
                return items[idx]
            print("Invalid selection. Try again.")
        except ValueError:
            print("Please enter a number.")

def select_bookmaker(event_data):
    odds_lines = event_data.get("odds", [])
    if not odds_lines:
        return "auto"
    bookmakers = list(set([o.get("bookmaker", "Unknown") for o in odds_lines]))
    if len(bookmakers) == 0:
        return "auto"
    if len(bookmakers) == 1:
        print(f"Only one bookmaker available: {bookmakers[0]}")
        return bookmakers[0]
    print("\n" + "=" * 50)
    print("Available bookmakers:")
    for i, b in enumerate(bookmakers):
        print(f"{i+1:3}. {b}")
    print("=" * 50)
    while True:
        try:
            choice = input("Select bookmaker (enter number, or press Enter for 'auto'): ")
            if choice.strip() == "":
                return "auto"
            idx = int(choice) - 1
            if 0 <= idx < len(bookmakers):
                return bookmakers[idx]
            print("Invalid selection.")
        except ValueError:
            print("Please enter a number.")

if __name__ == "__main__":
    print("=" * 55)
    print("SPORTSGAMEOdds CORRECT-SCORE ODDS EXTRACTOR")
    print("=" * 55)

    sports = list_sports()
    if not sports:
        print("No sports found.")
        exit(1)
    selected_sport = select_from_list(sports, "name", "Select a sport")
    if not selected_sport:
        print("No sport selected.")
        exit(1)
    sport_key = selected_sport.get("key", "football")
    print(f"\nSelected sport: {selected_sport.get('name')}")

    leagues = list_leagues(sport_key)
    if not leagues:
        print("No leagues found for this sport.")
        exit(1)
    selected_league = select_from_list(leagues, "name", "Select a league")
    if not selected_league:
        print("No league selected.")
        exit(1)
    league_key = selected_league.get("key", "EPL")
    print(f"\nSelected league: {selected_league.get('name')}")

    seasons = list_seasons(sport_key, league_key)
    if not seasons:
        print("No seasons found. Proceeding without season filter.")
        season_key = None
    else:
        selected_season = select_from_list(seasons, "name", "Select a season")
        if not selected_season:
            print("No season selected. Proceeding without season filter.")
            season_key = None
        else:
            season_key = selected_season.get("key")
            print(f"\nSelected season: {selected_season.get('name')}")

    events = list_events(sport_key, league_key, season=season_key, status="scheduled")
    if not events:
        print("No scheduled events found. Trying 'live' status...")
        events = list_events(sport_key, league_key, season=season_key, status="live")
    if not events:
        print("No events found. Please check your selections.")
        exit(1)

    selected_event = select_from_list(events, "homeTeamName", "Select a match")
    if not selected_event:
        print("No match selected.")
        exit(1)
    event_id = selected_event.get("eventId")
    event_name = f"{selected_event.get('homeTeamName', 'Unknown')} vs {selected_event.get('awayTeamName', 'Unknown')}"
    print(f"\nSelected match: {event_name} (ID: {event_id})")

    matrix_size_input = input("\nEnter matrix size (e.g., 10 for scores 0-9, press Enter for 10): ")
    if matrix_size_input.strip() == "":
        matrix_size = 10
    else:
        try:
            matrix_size = int(matrix_size_input)
            if matrix_size <= 0:
                print("Must be positive. Using default 10.")
                matrix_size = 10
        except ValueError:
            print("Invalid input. Using default 10.")
            matrix_size = 10
    print(f"Matrix size: {matrix_size}x{matrix_size}")

    print("\nFetching event data...")
    event_data = get_event(event_id)

    bookmaker_choice = select_bookmaker(event_data)

    print(f"\nExtracting correct-score odds from bookmaker: {bookmaker_choice}...")
    prob_matrix, bookmaker_used, overround = extract_correct_score_matrix(
        event_data, bookmaker_name=bookmaker_choice, matrix_size=matrix_size
    )

    if bookmaker_used is None:
        print("ERROR: Could not extract odds.")
        exit(1)

    print(f"Using bookmaker: {bookmaker_used}")
    print(f"Overround sum: {overround:.4f} (should be > 1.0)")

    output_dir = "inputdata"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{bookmaker_used}_correct_score_probs.csv")
    np.savetxt(output_path, prob_matrix, delimiter=",", fmt="%.10f")
    print(f"\nSaved probability matrix to: {output_path}")

    max_prob = np.max(prob_matrix)
    if max_prob > 0:
        y, x = np.unravel_index(np.argmax(prob_matrix), prob_matrix.shape)
        best_odds = 1.0 / max_prob
        print(f"\nBest correct-score bet: {x}-{y} @ {best_odds:.2f} (prob: {max_prob:.4%})")
    else:
        print("\nNo correct-score odds found.")