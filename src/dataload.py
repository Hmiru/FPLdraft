import pandas as pd
from dataclasses import dataclass
import random

@dataclass
class Player:
    name: str
    position: str
    team: str
    ranking: int

data=pd.read_csv("../dataset/23_24_result.csv", encoding='cp949')# This is a sample Python script.


players=[]
for _, row in data.iterrows():
    player=Player(name=row['name'], team=row['team'],  position=row['position'], ranking=row['ranking'])
    players.append(player)


