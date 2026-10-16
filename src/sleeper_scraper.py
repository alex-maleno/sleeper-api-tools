
import json
import pprint
import requests
from pathlib import Path
from argparse import ArgumentParser


BASE_URL = "https://api.sleeper.app/v1"


class Team:
    def __init__(self, owner=None):
        self.owner = owner
        self.QBs = []
        self.RBs = []
        self.WRs = []
        self.TEs = []

    def to_dict(self):
        return {
            "Owner": self.owner,
            "QBs": self.QBs,
            "RBs": self.RBs,
            "WRs": self.WRs,
            "TEs": self.TEs,
        }

    def __repr__(self):
        return pprint.pformat(self.to_dict())


def sleeper_get(endpoint):
    """Fetch JSON from the Sleeper API."""
    response = requests.get(
        f"{BASE_URL}/{endpoint}",
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


def get_player_details(player_id, players):
    """Look up a player using the already-fetched player database."""
    player = players.get(player_id)

    if not player:
        return f"Unknown Player ({player_id})", None

    name = player.get("full_name")

    if not name:
        name = " ".join(
            filter(
                None,
                [
                    player.get("first_name"),
                    player.get("last_name"),
                ],
            )
        )

    return name or f"Unknown Player ({player_id})", player.get("position")


def get_league_rosters(league_id, output_file):
    # Store output in a jsons directory alongside this script.
    json_dir = Path(__file__).resolve().parent / "jsons"
    json_dir.mkdir(parents=True, exist_ok=True)

    output_path = json_dir / output_file

    # Fetch all required API data.
    print(f"Fetching league data for {league_id}...")
    users = sleeper_get(f"league/{league_id}/users")
    rosters = sleeper_get(f"league/{league_id}/rosters")

    print("Fetching NFL player database...")
    players = sleeper_get("players/nfl")

    # Map user IDs to display names.
    user_map = {
        user["user_id"]: user.get("display_name", "Unknown")
        for user in users
    }

    teams = []

    for roster in rosters:
        owner_id = roster.get("owner_id")
        username = user_map.get(owner_id, "Unknown")
        this_team = Team(username)

        print(f"Building roster for {username}...")

        # Empty rosters may have either a missing or empty player list.
        player_ids = roster.get("players") or []

        for player_id in player_ids:
            player_name, position = get_player_details(
                player_id, players
            )

            if position == "QB":
                this_team.QBs.append(player_name)
            elif position == "RB":
                this_team.RBs.append(player_name)
            elif position == "WR":
                this_team.WRs.append(player_name)
            elif position == "TE":
                this_team.TEs.append(player_name)

        teams.append(this_team.to_dict())

    # Write a valid JSON document.
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(teams, f, indent=4)

    print(f"\nWrote {len(teams)} team rosters to {output_path}")


if __name__ == "__main__":
    league_ids = {
            
        "birch": 1336803927403819008,
        "tufts": 1135624719665180672,
        "str": 1132007178480529408,
    }

    file_names = {
        "birch": "BirchLaneDynasty.json",
        "tufts": "TuftsAdjacentRedraft.json",
        "str": "STRsBestFantasyLeague.json",
    }

    parser = ArgumentParser("Fantasy football shiii")

    parser.add_argument(
        "-l",
        "--league",
        default="birch",
        type=str,
        help="League to scrape: str, birch, or tufts",
    )

    parser.add_argument(
        "-f",
        "--file",
        default=None,
        type=str,
        help="Output filename (defaults to the league's filename)",
    )

    args = parser.parse_args()
    league = args.league.lower()

    if league not in league_ids:
        parser.error(
            f"Unrecognized league: {league}. "
            f"Choose from: {', '.join(league_ids)}"
        )

    output_file = args.file or file_names[league]

    try:
        get_league_rosters(league_ids[league], output_file)
    except requests.RequestException as exc:
        parser.exit(1, f"Error communicating with Sleeper API: {exc}\n")
    except (ValueError, KeyError, TypeError) as exc:
        parser.exit(1, f"Error processing Sleeper data: {exc}\n")

