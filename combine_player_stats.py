import os
import json
import pandas as pd
from collections import defaultdict
from tqdm import tqdm

DATA_DIR = "ipl_matches"

player_stats = defaultdict(lambda: defaultdict(lambda: {
    "matches": 0,
    "runs": 0,
    "balls_faced": 0,
    "fours": 0,
    "sixes": 0,
    "wickets": 0,
    "balls_bowled": 0,
    "runs_conceded": 0
}))

print("Processing files...")

for file_name in tqdm(os.listdir(DATA_DIR)):
    if not file_name.endswith(".json"):
        continue

    with open(os.path.join(DATA_DIR, file_name), "r") as f:
        match = json.load(f)

    season = match["info"]["season"]
    innings = match.get("innings", [])
    seen_players = set()

    for inning in innings:
        for over in inning["overs"]:
            for delivery in over["deliveries"]:
                batter = delivery["batter"]
                bowler = delivery["bowler"]
                runs = delivery["runs"]["batter"]
                total_runs = delivery["runs"]["total"]

                # Batting
                stats = player_stats[season][batter]
                stats["runs"] += runs
                stats["balls_faced"] += 1
                if batter not in seen_players:
                    stats["matches"] += 1
                    seen_players.add(batter)
                if runs == 4:
                    stats["fours"] += 1
                elif runs == 6:
                    stats["sixes"] += 1

                # Bowling
                bstats = player_stats[season][bowler]
                bstats["balls_bowled"] += 1
                bstats["runs_conceded"] += total_runs
                if bowler not in seen_players:
                    bstats["matches"] += 1
                    seen_players.add(bowler)
                if "wickets" in delivery:
                    bstats["wickets"] += 1

print("Building player stats...")

final_data = []
for season, players in player_stats.items():
    for player, stats in players.items():
        runs = stats["runs"]
        balls_faced = stats["balls_faced"]
        wickets = stats["wickets"]
        balls_bowled = stats["balls_bowled"]
        runs_conceded = stats["runs_conceded"]

        strike_rate = (runs / balls_faced * 100) if balls_faced > 0 else 0
        overs = balls_bowled / 6
        economy = (runs_conceded / overs) if overs > 0 else 0
        bowling_avg = (runs_conceded / wickets) if wickets > 0 else None

        final_data.append({
            "season": season,
            "player": player,
            "matches": stats["matches"],
            "runs": runs,
            "balls_faced": balls_faced,
            "strike_rate": round(strike_rate, 2),
            "fours": stats["fours"],
            "sixes": stats["sixes"],
            "balls_bowled": balls_bowled,
            "runs_conceded": runs_conceded,
            "wickets": wickets,
            "economy": round(economy, 2),
            "bowling_avg": round(bowling_avg, 2) if bowling_avg is not None else None
        })

df = pd.DataFrame(final_data)
df.to_csv("ipl_player_stats.csv", index=False)
print("✅ Done! Saved player stats to 'ipl_player_stats.csv'")
