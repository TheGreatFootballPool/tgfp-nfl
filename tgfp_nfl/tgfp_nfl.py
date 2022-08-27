"""
  This module contains all the necessary functions for interfacing with
  a data source (ESPN / Yahoo for example) for retrieving scores, schedule data, etc.
"""
from __future__ import annotations
from urllib.request import Request, urlopen
import re
import json
from dateutil import parser


class TgfpNfl:
    """ The main class for interfacing with Data Source json for sports """

    def __init__(self, week_no, debug=False):
        self._games = []
        self._teams = []
        self._games_data = None
        self._teams_data = None
        self._debug = debug
        self._week_no = week_no

    def games(self):
        """
        Returns:
            a list of all TgfpNflGames in the json structure
        """
        if self._games:
            return self._games
        if not self._games_data:
            all_headers = {'Host': 'sports.yahoo.com',
                           'Accept':
                           'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                           'Connection': 'keep-alive',
                           'Accept-Language': 'en-us',
                           'DNT': '1',
                           'User-Agent':
                           'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13)" + \
                            "AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0  Safari/604.1.38'
                           }
            # pylint: disable=invalid-name
            # schedState matches the url variable
            schedule_state = 2
            # if we're in the playoffs, we need to bump the schedState variable to 3
            week_no = self._week_no
            if self._week_no > 18:
                schedule_state = 3
            url_to_query = f'https://sports.yahoo.com/nfl/scoreboard/?dateRange={week_no}&'
            url_to_query += f'dateRangeDisplay={week_no}&schedState={schedule_state}'
            req = Request(url_to_query, headers=all_headers)
            # pylint: disable=consider-using-with
            raw_game_data = urlopen(req).read().decode('utf-8')
            games_data = None
            for line in raw_game_data.splitlines():
                if re.match(r'^root.App.main.*', line):
                    split_line = line.split(' = ')[1].rstrip(';')
                    all_data = json.loads(split_line)
                    stores = all_data['context']['dispatcher']['stores']
                    games_data = stores['GamesStore']['games']
                    if self._debug:
                        try:
                            with open('_games_data.json', 'w', encoding='utf-8') as outfile:
                                json.dump(games_data, outfile)
                        except IOError:
                            print('could not write games data to json')
                    break
            self._games_data = games_data
        for game_key in self._games_data:
            if re.match(r'^nfl*', game_key):
                self._games.append(TgfpNflGame(self, game_data=self._games_data[game_key]))

        return self._games

    def teams(self):
        """
        Returns:
            a list of all TgfpNflTeams
        """
        if self._teams:
            return self._teams
        if not self._teams_data:
            all_headers = {'Host': 'sports.yahoo.com',
                           'Accept':
                           'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                           'Connection': 'keep-alive',
                           'Accept-Language': 'en-us',
                           'DNT': '1',
                           'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13) " +\
                           "AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0  Safari/604.1.38'
                           }
            req = Request('https://sports.yahoo.com/nfl/standings/', headers=all_headers)
            # pylint: disable=consider-using-with
            raw_teams_data = urlopen(req).read().decode('utf-8')
            teams_data = None
            for line in raw_teams_data.splitlines():
                if re.match(r'^root.App.main.*', line):
                    split_line = line.split(' = ')[1].rstrip(';')
                    all_data = json.loads(split_line)
                    stores = all_data['context']['dispatcher']['stores']
                    teams_data = stores['TeamsStore']['teams']
                    if self._debug:
                        try:
                            with open('team_data.json', 'w', encoding='utf-8') as outfile:
                                json.dump(teams_data, outfile)
                        except IOError:
                            print('could not write team data to json file')
                    break
            self._teams_data = teams_data
        for team_key in self._teams_data:
            if 'default_league' in self._teams_data[team_key] and \
               self._teams_data[team_key]['default_league'] == "nfl":
                self._teams.append(TgfpNflTeam(self, team_data=self._teams_data[team_key]))

        return self._teams

    def find_games(self):
        """ There are currently no filters for this, so it just finds all games """
        return self.games()

    def find_teams(self, team_id=None) -> [TgfpNflTeam]:
        """ returns a list of all teams optionally filtered by a single team_id """
        found_teams = []
        for team in self.teams():
            found = True
            if team_id and team_id != team.id:
                found = False
            if found:
                found_teams.append(team)

        return found_teams


class TgfpNflGame:
    """ A single game from the Data Source json """
    # pylint: disable=too-many-instance-attributes

    def __init__(self, data_source, game_data):
        # pylint: disable=invalid-name
        self.id: str = game_data['gameid']
        # pylint: enable=invalid-name
        self.data_source = data_source
        self.game_data = game_data
        self.home_team = data_source.find_teams(team_id=game_data['home_team_id'])[0]
        self.away_team = data_source.find_teams(team_id=game_data['away_team_id'])[0]
        self.start_time = parser.parse(game_data['start_time'])
        self.winning_team = data_source.find_teams(team_id=game_data['winning_team_id'])[0]
        self.total_home_points = game_data['total_home_points']
        self.total_away_points = game_data['total_away_points']
        self.score_is_final = game_data['status_type'] == "final"
        self.status_type = game_data['status_type']

        self._odds = []

    def odds(self):
        """
        Returns:
            all the 'odds' from the Data Source JSON
        """
        if not self._odds:
            if 'odds' in self.game_data:
                for odd in self.game_data['odds']:
                    self._odds.append(
                        TgfpNflOdd(
                            data_source=self.data_source,
                            odd_data=self.game_data['odds'][odd]
                        )
                    )

        return self._odds

    def average_home_spread(self):
        """ Takes all the odds and averages them out """
        number_of_odds = len(self.odds())
        print(f"number of odds: {number_of_odds:d}")
        home_spread_total = 0.0
        average_spread = None
        if self.odds():
            for odd in self.odds():
                print(odd.data)
                if odd.home_spread:
                    home_spread_total += float(odd.home_spread)
            average_spread = home_spread_total / number_of_odds

        return average_spread


class TgfpNflTeam:
    """ The class that wraps the Data Source JSON for each team """
    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-few-public-methods
    def __init__(self, data_source, team_data):
        self.data_source = data_source
        self.data = team_data
        # pylint: disable=invalid-name
        self.id = team_data['team_id']
        # pylint: enable=invalid-name
        self.full_name = team_data['full_name']
        self.logo_url = team_data['sportacularLogo']
        if 'team_standing' in team_data:
            self.wins = team_data['team_standing']['team_record']['wins']
            self.losses = team_data['team_standing']['team_record']['losses']
            self.ties = team_data['team_standing']['team_record']['ties']
        else:
            self.wins = 0
            self.losses = 0
            self.ties = 0

    def tgfp_id(self, tgfp_teams):
        """
        Args:
            tgfp_teams: list of teams to loop through
        Returns:
            the tgfp_id for the current data_source's team, None if not found
        """
        found_team_id = None
        for team in tgfp_teams:
            if self.id == team.tgfp_nfl_team_id:
                found_team_id = team.id
                break
        return found_team_id


class TgfpNflOdd:
    """ Wraps the data source json for each 'odd' (spread) """
    # pylint: disable=too-few-public-methods

    def __init__(self, data_source, odd_data):
        self.data_source = data_source
        self.data = odd_data
        # pylint: disable=invalid-name
        self.id = odd_data['book_id']
        # pylint: enable=invalid-name
        self.home_spread = odd_data['home_spread']
