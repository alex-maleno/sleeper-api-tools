
import requests

BASE_URL = "https://api.sleeper.app/v1"


def sleeper_get(endpoint):
    """Fetch JSON data from the Sleeper API."""
    response = requests.get(f"{BASE_URL}/{endpoint}", timeout=30)
    response.raise_for_status()
    return response.json()


def get_league_rosters(league_id):
    # Fetch league users, rosters, and NFL player metadata.
    users = sleeper_get(f"league/{league_id}/users")
    rosters = sleeper_get(f"league/{league_id}/rosters")
    nfl_players = sleeper_get("players/nfl")

    # Map user IDs to display names.
    user_map = {
        user["user_id"]: user.get("display_name", "Unknown")
        for user in users
    }

    print(f"\nLeague ID: {league_id}")
    print(f"Number of rosters: {len(rosters)}")
    print("=" * 50)

    # Build and print each team's roster.
    for roster in rosters:
        owner_id = roster.get("owner_id")
        username = user_map.get(owner_id, "Unassigned")
        roster_id = roster.get("roster_id", "?")
        player_ids = roster.get("players") or []

        print(f"\nRoster {roster_id} - {username}")
        print("-" * 40)

        if not player_ids:
            print("No players on this roster!")
            continue

        for player_id in player_ids:
            player = nfl_players.get(player_id)

            if player is None:
                name = f"Unknown player (ID: {player_id})"
                position = "?"
                team = "?"
            else:
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
                    ) or f"Unknown player (ID: {player_id})"

                position = player.get("position") or "?"
                team = player.get("team") or "FA"

            print(f"- {name} ({position}, {team})")

    print()


if __name__ == "__main__":
    league_id = 1336803927403819008#input("Enter your Sleeper league ID: ").strip()

    try:
        get_league_rosters(league_id)
    except requests.RequestException as exc:
        print(f"Sleeper API request failed: {exc}")
    except (ValueError, KeyError, TypeError) as exc:
        print(f"Error processing Sleeper API data: {exc}")

