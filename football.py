import pandas as pd
from apyori import apriori
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np

# create dataframes
goalscorers = pd.read_csv("goalscorers.csv")
results = pd.read_csv("results.csv")
shootouts = pd.read_csv("shootouts.csv")
master_df = pd.read_csv("results_with_winner.csv")

# add new columns to results_with_winners dataframe
master_df.insert(6, "home_scorers", "", True)
master_df.insert(7, "away_scorers", "", True)

# set config to show full dataframe
desired_width=320
pd.set_option('display.width', desired_width)
pd.set_option('display.max_columns',16)

# add game winner to results dataframe and export as new csv
def add_winner_column(results):
    winner_column = []
    for i in range(len(results)):
        if results.loc[i, "home_score"] > results.loc[i, "away_score"]:
            winner_column.append(results.loc[i, "home_team"])
        if results.loc[i, "home_score"] < results.loc[i, "away_score"]:
            winner_column.append(results.loc[i, "away_team"])
        elif results.loc[i, "home_score"] == results.loc[i, "away_score"]:
            winner_column.append("draw")
    return winner_column
# run function & export to csv
# winner_column = add_winner_column(results)
# results_copy = results.copy()
# results_copy.insert(5, "winner", winner_column, True)
# results_copy.to_csv("results_with_winner.csv")

# retrieving all games for one team
def find_team_games(team_name):
    team_games = results.loc[((results['home_team'] == team_name) | (results['away_team'] == team_name))]
    return team_games
# print(find_team_games("England"))

# function to calculate wins for every team
def calculate_wins(results):
    all_winners = defaultdict(int)
    for i in range(len(results)):
        if results.loc[i, "home_score"] > results.loc[i, "away_score"]:
            all_winners[results.loc[i, "home_team"]] += 1
        if results.loc[i, "home_score"] < results.loc[i, "away_score"]:
            all_winners[results.loc[i, "away_team"]] += 1
    all_winners = dict(sorted(all_winners.items(), key=lambda item: -item[1]))
    return all_winners

# function for team with most wins
def team_with_most_wins():
    most_winningest_team = list(calculate_wins(results).keys())[0]
    return most_winningest_team

# print(results.head())
def find_world_cup_finals():
    world_cup_games = results.loc[results['tournament'] == 'FIFA World Cup']
    world_cup_finals = []
    i = 0
    while i < len(world_cup_games):
        current_year = str(world_cup_games.iloc[i, 0])[0:4]
        next_year = str(world_cup_games.iloc[i+1, 0])[0:4]
        if current_year != next_year:
            world_cup_finals.append(world_cup_games.iloc[i].values.tolist())
        i+= 1
        if i == (len(world_cup_games) - 1):
            break
    return world_cup_finals

# find_world_cup_finals()

# find team with most world cup wins by checking winner of each final
# 1950 world cup - 3rd place game played at same time as final so is listed after it in database
def team_world_cup_wins():
    # list_of_tournaments = [results.tournament.unique()]
    world_cup_games = results.loc[results['tournament'] == 'FIFA World Cup']
    i = 0
    world_cup_final_winners = defaultdict(int)
    while i < len(world_cup_games):
        # save the year of the current row and the next row
        current_year = str(world_cup_games.iloc[i, 0])[0:4]
        next_year = str(world_cup_games.iloc[i+1, 0])[0:4]
        # if years don't match, add winner of that game to winners
        if current_year != next_year:
            if world_cup_games.iloc[i, 3] > world_cup_games.iloc[i, 4]:
                world_cup_final_winners[world_cup_games.iloc[i, 1]] += 1
            if world_cup_games.iloc[i, 3] < world_cup_games.iloc[i, 4]:
                world_cup_final_winners[world_cup_games.iloc[i, 2]] += 1
            # code for if final was drawn, find who won penalty shootout
            if world_cup_games.iloc[i, 3] == world_cup_games.iloc[i, 4]:
                final_date = world_cup_games.iloc[i, 0]
                shootout = find_shootout_from_date(f"{final_date}")
                shootout_winner = shootout["winner"]
                world_cup_final_winners[shootout_winner.iloc[0]] += 1
        i+= 1
        # prevent i+1 from going past final row of world_cup_games in the next_year check
        if i == (len(world_cup_games)-1):
            if world_cup_games.iloc[i, 3] > world_cup_games.iloc[i, 4]:
                world_cup_final_winners[world_cup_games.iloc[i, 1]] += 1
            if world_cup_games.iloc[i, 3] < world_cup_games.iloc[i, 4]:
                world_cup_final_winners[world_cup_games.iloc[i, 2]] += 1
            elif world_cup_games.iloc[i, 3] == world_cup_games.iloc[i, 4]:
                final_date = world_cup_games.iloc[i, 0]
                shootout = find_shootout_from_date(f"{final_date}")
                shootout_winner = shootout["winner"]
                world_cup_final_winners[shootout_winner.iloc[0]] += 1
            break
    # fix error due to 1950 final not being last game of tournament due to 3rd place playoff (remove Sweden, +1 Uruguay)
    world_cup_final_winners.pop("Sweden")
    world_cup_final_winners["Uruguay"] += 1
    # sort winners dict descending (most wins first)
    world_cup_final_winners = dict(sorted(world_cup_final_winners.items(), key=lambda item: -item[1]))
    return world_cup_final_winners

# function to return all games from x world cup
def return_all_games_from_world_cup(year):
    world_cup_games = results.loc[results['tournament'] == 'FIFA World Cup']
    world_cup_year = world_cup_games[world_cup_games["date"].str.contains(f"{year}")]
    return world_cup_year

# find game from date of shootout
def find_shootout_from_date(date):
    shootout_from_date = shootouts[shootouts["date"].str.contains(date)]
    return shootout_from_date

# find game from date of game
def find_game_from_date(date):
    game_from_date = master_df[master_df["date"].str.contains(date)]
    return game_from_date

# find game from date and teams involved
def find_game_from_home_team_and_date(home_team, date):
    date_rows = find_game_from_date(date)
    game_row = date_rows[date_rows["home_team"].str.contains(home_team)]
    return game_row

# function for finding how many games a country has hosted
def how_many_games_hosted(country):
    pass

# function for finding which country has hosted most games - friendlies/tournaments? - make list of major tournaments to compare against
def find_most_games_hosted():
    pass

# when are most goals scored? do teams that score an early goal (under 10 mins) usually go on to win the game?

# add goals to the master_df under "home_scorers" and "away_scorers" headings
### OWN GOALS ARE COUNTED UNDER THE TEAM WHO BENEFITED FROM THE GOAL

# goalscorers_between_40_50 = goalscorers.loc[((goalscorers["minute"] > 40.0) & (goalscorers["minute"] < 50.0))]
# print(goalscorers.tail(10))
# print(goalscorers.head(30))
# print(master_df.head())

# function to create columns to add goalscorers to master df
def create_goalscorers_columns():
    i = 0
    # create temp lists for storing scorers
    goal_and_time = []
    game_home_scorers = []
    game_away_scorers = []
    # main lists that will be converted to dataframe columns
    home_scorers_column = []
    away_scorers_column = []
    while i < len(goalscorers):
        # find which game on master sheet that goal was scored in and whether for home or away team
        goal_game = find_game_from_home_team_and_date(goalscorers.iloc[i, 1], goalscorers.iloc[i, 0]).values.tolist()
        next_game = find_game_from_home_team_and_date(goalscorers.iloc[i+1, 1], goalscorers.iloc[i+1, 0]).values.tolist()
        print(goal_game)
        # add goalscorer & goal scored time to temp list
        # store home/away goalscorers in list per home/away team for that game
        if goalscorers.iloc[i, 3] == goalscorers.iloc[i, 1]:
            # game_home_scorers.append(goalscorers.iloc[i, 4])
            goal_and_time.append(goalscorers.iloc[i, 4])
            goal_and_time.append(goalscorers.iloc[i, 5])
            game_home_scorers.append(goal_and_time)
            goal_and_time = []  # reset temp list
        if goalscorers.iloc[i, 3] == goalscorers.iloc[i, 2]:
            # game_away_scorers.append(goalscorers.iloc[i, 4])
            goal_and_time.append(goalscorers.iloc[i, 4])
            goal_and_time.append(goalscorers.iloc[i, 5])
            game_away_scorers.append(goal_and_time)
            goal_and_time = []  # reset temp list
        # if next game is different, add this game's scorers to the main column and then clear the temp home/away scorers lists
        if goal_game != next_game:
            home_scorers_column.append(game_home_scorers)
            away_scorers_column.append(game_away_scorers)
            game_home_scorers = []
            game_away_scorers = []
        # if the next goal in the goalscorers df is from a different game, add the home/away lists to the master df column lists
        # add master column home/away goalscorers columns list to the master df

        i+= 1
        # if i == 100:
        #     print("100 reached")
        # if i == 500:
        #     print("500 reached")
        # if i == 1000:
        #     print("1000 reached")
        # if i == 5000:
        #     print("5000 reached")
        # if i == 10000:
        #     print("10,000 reached")
        # if i == 20000:
        #     print("20,000 reached")
        # if i == 30000:
        #     print("30,000 reached")
        # stop at i=x lines for testing
        if i ==30:
            print(home_scorers_column)
            print(away_scorers_column)
            break
    return home_scorers_column, away_scorers_column

# 2nd attempt at function to add goalscorers to master df
def add_goalscorers_to_df():
    i = 430
    # temp lists for storing goalscorers & goal times
    goal_and_time = []
    game_home_scorers = []
    game_away_scorers = []
    while i < len(master_df):
        # find indices of goalscorers df for the goalscorers for current game
        goalscorers_index = find_goalscorer_index_from_home_team_and_date(master_df.iloc[i, 2], master_df.iloc[i, 1])
        print(goalscorers_index)
        # for each index in the goalscorers_index, add the goalscorer + time to goal_and_time, then add to home/away goal scorers lists
        # for scorer in goalscorers_index:

        # if there are no recorded goalscorers for the current game, assign null value for the goalscorers in the master_df

        i += 1
        if i == 450:
            break

def find_goalscorer_index_from_home_team_and_date(home_team, date):
    goalscorer_index = goalscorers.index[(goalscorers['date'] == date) & (goalscorers["home_team"] == home_team)].tolist()
    return goalscorer_index

# print(find_goalscorer_index_from_home_team_and_date("Chile", "1916-07-02"))
# print(find_goalscorer_index_from_home_team_and_date("Argentina", "1916-07-06"))
# home_scorers, away_scorers = create_goalscorers_columns()
# master_df["home_scorers"] = home_scorers
# master_df["away_scorers"] = away_scorers
print(master_df[438:450])
add_goalscorers_to_df()

# print(list_of_results)
# print(master_df.head(100))
# print(goalscorers.head(50))

# Questions
# which team has scored most goals, scored most multi-goal games
# is home team more likely to overturn a deficit than away
# do larger cities have a higher win %
# average goals scored per country/continent per game for home and away teams
# home team and away team win % for each decade
# when is the "ideal time to concede"? i.e. pundits always say "that's a bad time to concede" - is conceding just before half time as bad as people think?