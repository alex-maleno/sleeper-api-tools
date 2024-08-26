import requests
import pprint
import json

class Team:
    def __init__(self, owner=None):
        self.owner = owner

        self.QBs = []
        self.RBs = []
        self.WRs = []
        self.TEs = []

    def to_dict(self):
        d = {}
        d["Owner"] = self.owner
        d["QBs"] = self.QBs
        d["RBs"] = self.RBs
        d["TEs"] = self.TEs
        d["WRs"] = self.WRs

        return d

    def __repr__(self):
        return pprint.pformat(self.to_dict())


def get_player_details(player_id):
    # Get player information
    players_url = "https://api.sleeper.app/v1/players/nfl"
    players_response = requests.get(players_url)
    players = players_response.json()

    # Retrieve player details
    player_info = players.get(player_id, {})
    player_name = player_info.get('full_name', 'Unknown Player')
    player_position = player_info.get('position', 'Unknown Position')

    return player_name, player_position


# Function to get league rosters from Sleeper
def get_league_rosters(league_id):
    f = open("BirchLaneDynasty2024Rosters.json", "w")
    # Get the list of all users in the league
    users_url = f"https://api.sleeper.app/v1/league/{league_id}/users"
    users_response = requests.get(users_url)
    users = users_response.json()

    # Get rosters for each user
    rosters_url = f"https://api.sleeper.app/v1/league/{league_id}/rosters"
    rosters_response = requests.get(rosters_url)
    rosters = rosters_response.json()

    # Get player information
    players_url = "https://api.sleeper.app/v1/players/nfl"
    players_response = requests.get(players_url)
    players = players_response.json()

    # Create a dictionary mapping user_id to username
    user_map = {user['user_id']: user['display_name'] for user in users}

    # Process and print each roster
    for roster in rosters:
        user_id = roster['owner_id']
        username = user_map.get(user_id, "Unknown")
        this_team = Team(username)

        print(f"Finding team for {username}")
        try:
            for player_id in roster['players']:
                player_name, position = get_player_details(player_id)
                #print(f"found {player_name}")
                if position == "QB":
                    this_team.QBs.append(player_name)
                elif position == "RB":
                    this_team.RBs.append(player_name)
                elif position == "WR":
                    this_team.WRs.append(player_name)
                elif position == "TE":
                    this_team.TEs.append(player_name)
        except Exception as e:
            print(f"Warning: Failed while parsing player names. Likely an empty Team")
            print(e)

        f.write(f"{this_team}\n\n")

    f.close()


if __name__ == "__main__":
    #league_id = input("Enter your Sleeper league ID: ")
    league_id = 1124842068661792768
    get_league_rosters(league_id)

