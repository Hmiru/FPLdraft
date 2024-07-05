class Rules:
    def __init__(self, teams, players):
        self.teams = teams
        self.players = players

    def max2(self, team, player):
        team_counts = {team: 0 for team in set(p.team for p in self.players)}
        for p in self.teams[team]:
            team_counts[p.team] += 1
        return team_counts[player.team] < 2

    def quota(self, team, player):
        position_limits = {
            'GK': 2,
            'DEF': 5,
            'MID': 5,
            'FWD': 3
        }
        position_counts = {position: 0 for position in position_limits.keys()}
        for p in self.teams[team]:
            position_counts[p.position] += 1
        return position_counts[player.position] < position_limits[player.position]

    def is_valid_player(self, team, player):
        return self.max2(team, player) and self.quota(team, player)