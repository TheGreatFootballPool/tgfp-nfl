"""
  This module contains all the necessary functions for interfacing with
  a data source (ESPN / Yahoo for example) for retrieving scores, schedule data, etc.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List, Dict
from urllib.request import Request, urlopen
import re
import json
from dateutil import parser
import httpx


class TgfpNfl:
    """ The main class for interfacing with Data Source json for sports """

    def __init__(self, week_no, debug=False):
        self._games = []
        self._teams = []
        self._standings = []
        self._games_source_data = None
        self._teams_source_data = None
        self._standings_source_data = None
        self._debug = debug
        self._week_no = week_no
        self._base_url = 'https://site.api.espn.com/apis/v2/sports/football/nfl/'
        self._base_site_url = 'https://site.api.espn.com/apis/site/v2/sports/football/nfl'

    def __get_games_source_data(self) -> List:
        """ Get Games from ESPN -- defaults to current season
        :season_type:
           -Season types are:
            1: Preseason
                weeks 1-4 (HOF game is week=1)
            2: Regular Season
                weeks 1-18
            3: Post Season
                Week #'s
                -#1 = Wild Card Round
                -#2 = Divisional Round
                -#3 = Conference Championships
                -#4 = Super Bowl
        if week number is > 18 we shift season type to '3', otherwise we use 2
        :return: list of games
        """
        content: dict = {}
        season_type = 3 if self._week_no > 18 else 2
        week_no = self._week_no - 18 if self._week_no > 18 else self._week_no
        url_to_query = self._base_site_url + f'/scoreboard?seasontype={season_type}&week={week_no}'
        try:
            response = httpx.get(url_to_query)
            content = response.json()
        except httpx.RequestError:
            print('HTTP Request failed')
        return content['events']

    def __get_teams_source_data(self) -> List:
        """ Get Teams from ESPN
        :return: list of teams
        """
        content: dict = {}
        url_to_query = self._base_site_url + '/teams'
        try:
            response = httpx.get(url_to_query)
            content = response.json()
        except httpx.RequestError:
            print('HTTP Request failed')
        return content['sports'][0]['leagues'][0]['teams']

    def __get_standings_source_data(self) -> List:
        """ Get Standings from ESPN
        :return: list of teams / standings
        """
        content: dict = {}
        url_to_query = self._base_url + '/standings?seasontype=2'
        try:
            response = httpx.get(url_to_query)
            content = response.json()
        except httpx.RequestError:
            print('HTTP Request failed')
        afc_standings: List = content['children'][0]['standings']['entries']
        nfc_standings: List = content['children'][1]['standings']['entries']
        all_standings: List = afc_standings + nfc_standings
        return all_standings

    def games(self) -> List[TgfpNflGame]:
        """
        Returns:
            a list of all TgfpNflGames in the json structure
        """
        if self._games:
            return self._games
        if not self._games_source_data:
            self._games_source_data = self.__get_games_source_data()
        for game_data in self._games_source_data:
            self._games.append(TgfpNflGame(self, game_data=game_data))

        return self._games

    def teams(self) -> List[TgfpNflTeam]:
        """
        Build a list of teams using the teams source and standings source data
        Returns:
            a list of all TgfpNflTeams
        """
        if self._teams:
            return self._teams
        if not self._teams_source_data:
            self._teams_source_data = self.__get_teams_source_data()
        if not self._standings_source_data:
            self._standings_source_data = self.__get_standings_source_data()
        for team_data in self._teams_source_data:
            single_team_data: dict = team_data['team']
            team_id: str = single_team_data['uid']
            single_team_standings: TgfpNflStanding = self.find_tgfp_nfl_standing_for_team(team_id)
            team: TgfpNflTeam = TgfpNflTeam(single_team_data, single_team_standings)
            self._teams.append(team)
        return self._teams

    def standings(self) -> List[Dict]:
        """
        Returns:
            a list of all TgfpNflGames in the json structure
        """
        if self._standings:
            return self._standings
        if not self._standings_source_data:
            self._standings_source_data = self.__get_standings_source_data()
        for standing_data in self._standings_source_data:
            self._standings.append(TgfpNflStanding(
                standing_data
            ))
        return self._standings

    def find_game(self, game_id: str) -> Optional[TgfpNflGame]:
        """ returns a list of all games that optionally """
        found_game: Optional[TgfpNflGame] = None
        for game in self.games():
            found = True
            if game_id and game_id != game.id:
                found = False
            if found:
                found_game = game
                break

        return found_game

    def find_teams(self, team_id=None, short_name=None) -> [TgfpNflTeam]:
        """ returns a list of all teams optionally filtered by a single team_id """
        found_teams = []
        for team in self.teams():
            found = True
            if team_id and team_id != team.id:
                found = False
            if short_name and short_name != team.short_name:
                found = False
            if found:
                found_teams.append(team)

        return found_teams

    def find_tgfp_nfl_standing_for_team(self, team_id: str) -> TgfpNflStanding:
        """ Returns the 'TgfpNflStanding' for a team in the form of a dict
            'wins': <int>
            'losses': <int>
            'ties': <int>
        """
        standing: TgfpNflStanding
        for standing in self.standings():
            found = True
            if team_id == standing.team_id:
                return standing
        return TgfpNflStanding(team_id, 0, 0, 0)


class TgfpNflGame:
    """ A single game from the Data Source json """

    # pylint: disable=too-many-instance-attributes

    def __init__(self, data_source: TgfpNfl, game_data):
        # pylint: disable=invalid-name
        self.id: str = game_data['uid']
        # pylint: enable=invalid-name
        self._data_source = data_source
        self._game_source_data = game_data
        self._game_status_source_data: dict = game_data['competitions'][0]['status']
        self._odds_source_data: List = []
        if 'odds' in game_data['competitions'][0]:
            self._odds_source_data = game_data['competitions'][0]['odds']
        self._home_team: Optional[TgfpNflTeam] = None
        self._away_team: Optional[TgfpNflTeam] = None
        self._favored_team: Optional[TgfpNflTeam] = None
        self._winning_team: Optional[TgfpNflTeam] = None
        self._spread: float = 0.0
        self._total_home_points: int = 0
        self._total_away_points: int = 0
        self.start_time = parser.parse(game_data['date'])
        self.game_status_type = game_data['status']['type']['name']

    def _odds(self) -> Optional[TgfpNflOdd]:
        """
        Returns:
            the first odds, ignoring all others
        """
        return_odds: Optional[TgfpNflOdd] = None
        if self._odds_source_data:
            first_odd: dict = self._odds_source_data[0]
            return_odds = TgfpNflOdd(
                data_source=self._data_source,
                odd_data=first_odd
            )
        return return_odds

    @property
    def favored_team(self) -> Optional[TgfpNflTeam]:
        if self._favored_team:
            return self._favored_team
        self.__set_home_away_favorite_teams_and_score()
        return self._favored_team

    @property
    def spread(self):
        if self._spread:
            return self._spread
        self.__set_home_away_favorite_teams_and_score()
        return self._spread

    @property
    def is_pregame(self):
        return self.game_status_type == 'STATUS_SCHEDULED'

    @property
    def is_final(self):
        return self.game_status_type == 'STATUS_FINAL'

    @property
    def home_team(self):
        if self._home_team:
            return self._home_team
        self.__set_home_away_favorite_teams_and_score()
        return self._home_team

    @property
    def away_team(self) -> TgfpNflTeam:
        if self._away_team:
            return self._away_team
        self.__set_home_away_favorite_teams_and_score()
        return self._away_team

    @property
    def winning_team(self) -> Optional[TgfpNflTeam]:
        teams: List = self._game_source_data['competitions'][0]['competitors']
        if not self._winning_team:
            if 'winner' in teams[0]:
                if teams[0]['winner']:
                    self._winning_team = self._data_source.find_teams(teams[0]['uid'])[0]
                else:
                    self._winning_team = self._data_source.find_teams(teams[1]['uid'])[0]
        return self._winning_team

    @property
    def total_home_points(self) -> int:
        if self._total_home_points:
            return self._total_home_points
        else:
            self.__set_home_away_favorite_teams_and_score()
        return self._total_home_points

    @property
    def total_away_points(self) -> int:
        if self._total_away_points:
            return self._total_away_points
        else:
            self.__set_home_away_favorite_teams_and_score()
        return self._total_away_points

    def __set_home_away_favorite_teams_and_score(self):
        teams: List = self._game_source_data['competitions'][0]['competitors']
        if self._odds():
            if self._odds().favored_team_short_name is None:
                self._favored_team = self._home_team
                self._spread = 0.5
            else:
                self._favored_team = self._data_source.find_teams(
                    short_name=self._odds().favored_team_short_name
                )[0]
                self._spread = self._odds().favored_team_spread
        if teams[0]['homeAway'] == 'home':
            self._total_home_points = int(teams[0]['score'])
            self._home_team = self._data_source.find_teams(team_id=teams[0]['uid'])[0]
            self._total_away_points = int(teams[1]['score'])
            self._away_team = self._data_source.find_teams(team_id=teams[1]['uid'])[0]
        else:
            self._total_home_points = int(teams[1]['score'])
            self._home_team = self._data_source.find_teams(team_id=teams[1]['uid'])[0]
            self._total_away_points = int(teams[0]['score'])
            self._away_team = self._data_source.find_teams(team_id=teams[0]['uid'])[0]

    @property
    def extra_info(self) -> dict:
        return {
            'description': self._game_source_data['name'],
            'game_time': self._game_source_data['status']['type']['detail']
        }


class TgfpNflTeam:
    """ The class that wraps the Data Source JSON for each team """

    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-few-public-methods
    def __init__(self, team_data: Dict, team_standings: TgfpNflStanding):
        self.data = team_data
        # pylint: disable=invalid-name
        self.id = team_data['uid']
        # pylint: enable=invalid-name
        self.city = team_data['location']
        self.long_name = team_data['shortDisplayName']
        self.short_name: str = str(team_data['abbreviation']).lower()
        self.full_name = team_data['displayName']
        self.logo_url = team_data['logos'][0]['href']
        self.wins = team_standings.wins
        self.losses = team_standings.losses
        self.ties = team_standings.ties

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
        self._data_source = data_source
        self._odd_source_data = odd_data

    @property
    def favored_team_short_name(self) -> Optional[str]:
        """
        Get the favorite team short name
        Returns:
            Optional[str]: favored team short name (lower case) or None if no team is favored
        Notes:
                the string we're parsing looks like:
                DAL -3.5
                or
                EVEN
        """
        favorite: str = self._odd_source_data['details'].split()[0].lower()
        if favorite == 'even':
            return None
        return favorite

    @property
    def favored_team_spread(self) -> float:
        if self.favored_team_short_name is None:
            return 0
        favorite: str = self._odd_source_data['details']
        spread: float = float(favorite.split()[1]) * -1
        return spread


class TgfpNflStanding:
    """ Wraps the data source json for standings data for a team"""

    def __init__(self, source_standings_data: dict):
        self.team_id: str = source_standings_data['team']['uid']
        self.wins = 0
        self.losses = 0
        self.ties = 0
        for stat in source_standings_data['stats']:
            if stat['type'] == 'wins':
                self.wins = int(stat['value'])
            if stat['type'] == 'losses':
                self.losses = int(stat['value'])
            if stat['type'] == 'ties':
                self.ties = int(stat['value'])
