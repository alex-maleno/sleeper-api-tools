import requests
import json

# Function to get league rosters from Sleeper
def get_league_rosters(league_id):
    # Get the list of all users in the league
    users_url = f"https://api.sleeper.app/v1/league/{league_id}/users"
    users_response = requests.get(users_url)
    users = users_response.json()

    # Get rosters for each user
    rosters_url = f"https://api.sleeper.app/v1/league/{league_id}/rosters"
    rosters_response = requests.get(rosters_url)
    rosters = rosters_response.json()

    # Create a dictionary mapping user_id to username
    user_map = {user['user_id']: user['display_name'] for user in users}

    # Process and print each roster
    for roster in rosters:
        user_id = roster['owner_id']
        username = user_map.get(user_id, "Unknown")
        print(f"Roster for {username}:")
        players = roster.get('players', None)
        if players is None:
            print("no team yet!")
            continue
        for player_id in roster['players']:
            print(f"- {player_id.get('full_name', 'unknown player')}")
        print()

if __name__ == "__main__":
    league_id = input("Enter your Sleeper league ID: ")
    get_league_rosters(league_id)

