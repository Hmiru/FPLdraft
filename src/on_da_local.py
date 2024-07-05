import random
import json
from dataload import players, Player
from rules import Rules



class DraftProcess:
    def __init__(self, how_many, how_many_person, rounds):
        self.how_many = how_many
        self.how_many_person = how_many_person
        self.rounds = rounds
        self.team_names = {}
        self.draft_order = []
        self.available_players = players[:]
        self.teams = {}
        self.rules = None

    def set_team_names(self, team_names):
        self.team_names = team_names

    def generate_draft_order(self):
        self.draft_order = list(self.team_names.keys())
        self.draft_order += [f"AI{i+1}" for i in range(self.how_many - self.how_many_person)]
        random.shuffle(self.draft_order)
        self.teams = {drafter: [] for drafter in self.draft_order}
        self.rules = Rules(self.teams, players)

    def draft(self, team):
        if team.startswith("AI"):
            self.ai_draft(team)
        else:
            self.user_draft(team)

    def filter_available_players(self, team):
        valid_players = [player for player in self.available_players if self.rules.is_valid_player(team, player)]
        return valid_players

    def user_draft(self, team):
        team_name = self.team_names[team]
        print(f"\n{team_name}'s turn. Available players:")
        valid_players = self.filter_available_players(team)
        for player in valid_players[:10]:
            print(f"{player.name}, {player.position}, {player.team}, {player.ranking}")

        pick_name = input("Choose a player by name: ").strip().lower()
        matched_players = self.search_player(pick_name, valid_players)

        while not matched_players:
            pick_name = input("No matches found. Enter part of the player's name again: ").strip().lower()
            matched_players = self.search_player(pick_name, valid_players)

        if len(matched_players) > 1:
            pick = self.handle_multiple_matches(matched_players)
        else:
            pick = matched_players[0]

        while pick is None or not self.rules.is_valid_player(team, pick):
            pick_name = input("Invalid pick. Choose a player by name: ").strip().lower()
            matched_players = self.search_player(pick_name, valid_players)
            if len(matched_players) > 1:
                pick = self.handle_multiple_matches(matched_players)
            else:
                pick = matched_players[0]

        self.finalize_pick(team, pick)

    def ai_draft(self, team):
        valid_players = self.filter_available_players(team)
        pick = valid_players[0]
        print(f"\n{team}'s turn. {pick.name} is picked.")
        self.finalize_pick(team, pick)

    def handle_multiple_matches(self, matched_players):
        print("Multiple players found:")
        for player in matched_players:
            print(f"{player.name}, {player.position}, {player.team}, {player.ranking}")
        pick_ranking = input("Enter the ranking of the player to choose (or type 'back' to go back): ").strip()
        if pick_ranking.lower() == 'back':
            return None
        return next((player for player in matched_players if player.ranking == int(pick_ranking)), None)

    def finalize_pick(self, team, pick):
        self.available_players.remove(pick)
        self.teams[team].append(pick)

    def show_status(self):
        for team, picked_players in self.teams.items():
            team_name = self.team_names.get(team, team)
            print(f"\n{team_name}'s team:")
            for player in picked_players:
                print(f"{player.name}, {player.position}, {player.team}, Ranking: {player.ranking}")

    def search_player(self, name_part, players):
        name_part = name_part.lower()
        matches = [player for player in players if name_part in player.name.lower()]
        return matches

    def save_draft_results(self, filename):
        try:
            with open(filename, 'w') as file:
                json.dump({team: [p.__dict__ for p in players] for team, players in self.teams.items()}, file, indent=4)
            print(f"Draft results saved to {filename}")
        except IOError as e:
            print(f"An error occurred while saving the draft results: {e}")

    def load_draft_results(self, filename):
        try:
            with open(filename, 'r') as file:
                data = json.load(file)
                self.teams = {team: [Player(**p) for p in players] for team, players in data.items()}
                return self.teams
        except IOError as e:
            print(f"An error occurred while loading the draft results: {e}")
            return None

    def run_draft(self):
        total_picks = self.rounds * len(self.draft_order)
        snake_order = []

        for i in range(self.rounds):
            if i % 2 == 0:
                snake_order.extend(self.draft_order)
            else:
                snake_order.extend(reversed(self.draft_order))

        pick_count = 0

        while pick_count < total_picks:
            current_team = snake_order[pick_count % len(snake_order)]
            self.draft(current_team)
            pick_count += 1

if __name__ == "__main__":
    # 사용자로부터 입력받기
    how_many = int(input("총 인원 수를 입력하세요: "))
    how_many_person = int(input("참여할 사람 수를 입력하세요: "))
    rounds = int(input("진행할 라운드 수를 입력하세요: "))

    draft_process = DraftProcess(how_many, how_many_person, rounds)

    # 사용자 이름 입력받기
    team_names = {}
    for i in range(how_many_person):
        name = input(f"Enter name for person {i + 1}: ")
        team_names[f"person{i + 1}"] = name

    draft_process.set_team_names(team_names)
    draft_process.generate_draft_order()

    draft_process.run_draft()
    draft_process.show_status()
    draft_process.save_draft_results("draft_results.json")
