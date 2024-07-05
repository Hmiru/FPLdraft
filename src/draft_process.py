import random
import json
from dataclasses import dataclass
from dataload import players, Player
from rules import Rules

@dataclass
class Player:
    name : str
    position : str
    team : str
    ranking : int

class DraftProcess:
    def __init__(self, how_many, how_many_person, rounds):
        self.how_many = how_many
        self.how_many_person = how_many_person
        self.rounds = rounds
        self.team_names = {}
        self.draft_order = []  # 여기서 입력을 받지 않고, 나중에 설정
        self.available_players = players[:]
        self.teams = {drafter: [] for drafter in self.draft_order}  # 초기화 추가
        self.rules = Rules(self.teams, players)  # 초기화 추가

    def set_team_names(self, team_names):
        self.team_names = team_names

    def generate_draft_order(self):
        self.draft_order = list(self.team_names.keys())
        self.draft_order += [f"AI{i+1}" for i in range(self.how_many - self.how_many_person)]
        random.shuffle(self.draft_order)
        self.teams = {drafter: [] for drafter in self.draft_order}  # 초기화 추가
        self.rules = Rules(self.teams, players)  # 초기화 추가

    def draft(self, team):
        if team.startswith("AI"):
            self.ai_draft(team)
        else:
            self.user_draft(team)

    def filter_available_players(self, team):
        valid_players = [player for player in self.available_players if self.rules.is_valid_player(team, player)]
        return valid_players

    def user_draft(self, team, pick_name):
        team_name = self.team_names[team]
        valid_players = self.filter_available_players(team)
        matched_players = self.search_player(pick_name, valid_players)

        if len(matched_players) > 1:
            return "multiple", matched_players
        elif len(matched_players) == 0:
            return "none", None
        else:
            pick = matched_players[0]
            if self.rules.is_valid_player(team, pick):
                self.finalize_pick(team, pick)
                return "success", pick
            else:
                return "invalid", None

    def ai_draft(self, team):
        valid_players = self.filter_available_players(team)
        pick = valid_players[0]
        self.finalize_pick(team, pick)
        return pick

    def handle_multiple_matches(self, matched_players, pick_ranking):
        return next((player for player in matched_players if player.ranking == int(pick_ranking)), None)

    def finalize_pick(self, team, pick):
        self.available_players.remove(pick)
        self.teams[team].append(pick)

    def show_status(self):
        status = []
        for team, picked_players in self.teams.items():
            team_name = self.team_names.get(team, team)
            status.append(f"\n{team_name}'s team:")
            for player in picked_players:
                status.append(f"{player.name}, {player.position}, {player.team}, Ranking: {player.ranking}")
        return "\n".join(status)

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
        snake_order = self.draft_order + self.draft_order[::-1]
        pick_count = 0

        while pick_count < total_picks:
            for team in snake_order:
                if pick_count >= total_picks:
                    break
                self.draft(team)
                pick_count += 1
