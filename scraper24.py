from bs4 import BeautifulSoup as bs
from utilities import combine_dicts
import requests, json, fpl, unidecode





''' Class for scraping Expected Goals (xG) for a team
    from understat.com

args
    team_name (string): team name used by understat in their url
                         after team/
'''

class understatScrapeTeam(object):

    '''Initialize class by setting team name and appropriate url'''
    def __init__(self, team_name):
        self.team = team_name
        self.base_url = 'https://understat.com/team/'
        self.url_suffix = '/2018'
        self.url = self.base_url +  team_name + self.url_suffix

    '''Function to open understat webpage via Beautiful Soup.
       Sets Beautiful Soup object to html_contents'''
    def open_understat_page(self):
        page_response = requests.get(self.url, timeout=5)
        page_content = bs(page_response.content, "html.parser")
        self.html_content = page_content

    '''Function takes in Beatiful Soup page content
       and sets class property json_data with a
        string containing JSON data

    args
        html_content (BS object): BS html parsed content
    '''
    def get_JSON_data(self):
        html_data = str(self.html_content.find('script'))
        start = html_data.find("'")
        end = html_data.find("'", start+1)
        json_raw = html_data[start+1:end]
        json_decoded = json_raw.encode().decode('unicode_escape')
        json_data = json.loads(json_decoded)
        self.json_data = json_data

    '''Function to clean a raw JSON string from
       understat.com

    args
        json_data (string): String with raw encoded JSON data
    '''
    def clean_JSON_data(self):
        clean_json = []
        for i in range(0, len(self.json_data)):
            gw_data = self.json_data[i]
            clean_gw_data = {}

            clean_gw_data['gw'] = i+1
            clean_gw_data['away_team'] = gw_data['a']['title']
            clean_gw_data['away_id'] = gw_data['a']['id']
            clean_gw_data['home_team'] = gw_data['h']['title']
            clean_gw_data['home_id'] = gw_data['h']['id']
            clean_gw_data['home_xG'] = gw_data['xG']['h']
            clean_gw_data['away_xG'] = gw_data['xG']['a']

            clean_json.append(clean_gw_data)
        self.clean_json

    '''This function returns the xG for a team
       during each of the gameweeks in the interval
       specified by gw_start and gw_end

    args
        gw_start (int): Gameweek to start at
        gw_end   (int): Gameweek to end at
    '''
    def scrape(self, gw_start=1, gw_end=4):
        self.open_understat_page()
        self.get_JSON_data()
        clean_json = self.clean_JSON_data()[gw_start-1: gw_end]

        xG_data = []
        for gw in clean_json:
            gw_data = {}
            gw_data['gw'] = gw['gw']
            if gw['home_team'] == self.team:
                gw_data['xG'] = gw['home_xG']
                gw_data['was_home'] = 1
                gw_data['opponent'] = gw['away_team']
            elif gw['away_team'] == self.team:
                gw_data['xG'] = gw['away_xG']
                gw_data['was_home'] = 0
                gw_data['opponent'] = gw['home_team']
            else:
                gw_data['xG'] = None
            xG_data.append(gw_data)

        return xG_data


''' Class for scraping Expected Goals (xG) for a team
    from understat.com

args
    team_name (string): team name used by understat in their url
                         after team/
'''
class understatScrapePlayer(object):
    '''Initialize class by setting team name and appropriate url'''
    def __init__(self, player_id):
        self.player_id = player_id
        self.base_url = 'https://understat.com/player/'
        self.season = '2018'
        self.url = self.base_url + self.player_id

        self.get_player_data()
        self.open_understat_page()
        self.get_JSON_data()
        self.clean_JSON_data()

    def get_player_data(self):
        players_info = understatScrapePlayers()
        id_name_map = players_info.get_id_name_map()
        id_team_map = players_info.get_id_team_map()
        self.name = id_name_map[self.player_id]
        split_name = self.name.split(" ", 1)
        if len(split_name) > 1:
            self.last_name = unidecode.unidecode(split_name[1])
        else:
            self.last_name = unidecode.unidecode(split_name[0])
        self.team = id_team_map[self.player_id]

    '''Function to open understat webpage via Beautiful Soup.
       Returns Beautiful Soup object with page contents'''
    def open_understat_page(self):
        page_response = requests.get(self.url)# timeout=5)
        page_content = bs(page_response.content, "html.parser")
        self.page_content = page_content

    '''Function takes in Beatiful Soup page content
       and returns relevant string with JSON data

    args
        html_content (BS object): BS html parsed content
    '''
    def get_JSON_data(self):
        html_data = str(self.page_content.find_all('script')[3])
        start = html_data.find("'")
        end = html_data.find("'", start+1)
        json_raw = html_data[start+1:end]
        json_decoded = json_raw.encode().decode('unicode_escape')
        json_data = json.loads(json_decoded)
        self.json_data = json_data

    '''Function to clean a raw JSON string from
       understat.com

    args
        json_data (string): String with raw encoded JSON data
    '''
    def clean_JSON_data(self):
        clean_json = []
        for i in range(0, len(self.json_data)):
            gw_data = self.json_data[i]
            clean_gw_data = {}
            if gw_data['season'] == self.season:
                if gw_data['a_team'] == self.team:
                    clean_gw_data['team_goals'] = gw_data['a_goals']
                    clean_gw_data['opponent_goals'] = gw_data['h_goals']
                    clean_gw_data['opponent'] = gw_data['h_team']
                    clean_gw_data['was_home'] = False
                else:
                    clean_gw_data['team_goals'] = gw_data['h_goals']
                    clean_gw_data['opponent_goals'] = gw_data['a_goals']
                    clean_gw_data['opponent'] = gw_data['a_team']
                    clean_gw_data['was_home'] = True

                clean_gw_data['date'] = gw_data['date']
                clean_gw_data['team'] = self.team
                clean_gw_data['goals'] = gw_data['goals']
                clean_gw_data['key_passes'] = gw_data['key_passes']
                clean_gw_data['position'] = gw_data['position']
                clean_gw_data['np_G'] = gw_data['npg']
                clean_gw_data['np_xG'] = gw_data['npxG']
                clean_gw_data['shots'] = gw_data['shots']
                clean_gw_data['mins_played'] = gw_data['time']
                clean_gw_data['xA'] = gw_data['xA']
                clean_gw_data['xG'] = gw_data['xG']
                clean_gw_data['xGBuildup'] = gw_data['xGBuildup']
                clean_gw_data['xGChain'] = gw_data['xGChain']

                clean_json.append(clean_gw_data)
        self.clean_json = clean_json

    '''This function returns the xG for a team
       during each of the gameweeks in the interval
       specified by gw_start and gw_end
    args
        gw_start (int): Gameweek to start as
        gw_end   (int): Gameweek to end as
    '''
    def scrape(self, gw_start=1, gw_end=4):
        clean_json = self.clean_json[gw_start-1: gw_end]

        xG_data = []
        i=len(clean_json)
        for gw in clean_json:
            gw_data = {}
            #gw_data['gw'] = i
            gw_data['name'] = self.name
            gw_data.update(gw)
            xG_data.append(gw_data)
            i-=1
        return xG_data


''' Class for scraping Expected Goals (xG) for a team
    from understat.com

args
    team_name (string): team name used by understat in their url
                         after team/
'''
class understatScrapePlayers(object):
    '''Initialize class by setting team name and appropriate url'''
    def __init__(self):
        self.base_url = 'https://understat.com/league/EPL/2018'
        self.url = self.base_url
        self.open_understat_page()
        self.get_JSON_data()

    '''Function to open understat webpage via Beautiful Soup.
       Returns Beautiful Soup object with page contents'''
    def open_understat_page(self):
        page_response = requests.get(self.url, timeout=5)
        page_content = bs(page_response.content, "html.parser")
        self.page_content = page_content

    '''Function takes in Beatiful Soup page content
       and returns relevant string with JSON data

    args
        html_content (BS object): BS html parsed content
    '''
    def get_JSON_data(self):
        html_data = str(self.page_content.find_all('script')[2])
        start = html_data.find("'")
        end = html_data.find("'", start+1)
        json_raw = html_data[start+1:end]
        json_decoded = json_raw.encode().decode('unicode_escape')
        json_data = json.loads(json_decoded)
        self.player_data = json_data


    def get_players_data(self):
        return self.player_data

    def get_player_data(self, id):
        for player in self.player_data:
            if player['id'] == id:
                return player
        return None

    def get_name_id_map(self):
        player_list = self.player_data
        name_id_mapping = {}

        for player in player_list:
            player_name = player['player_name']
            #if len(player_name) > 1:
            #   player_name = unidecode.unidecode(player_name[1])
            #else:
            #    player_name = unidecode.unidecode(player_name[0])
            player_id = player['id']
            name_id_mapping[player_name] = player_id

        return name_id_mapping

    def get_id_name_map(self):
        player_list = self.player_data
        id_name_mapping = {}

        for player in player_list:
            player_name = player['player_name']
            player_id = player['id']
            id_name_mapping[player_id] = player_name

        return id_name_mapping

    def get_id_team_map(self):
        player_list = self.player_data
        id_team_map = {}

        for player in player_list:
            player_id = player['id']
            player_team = player['team_title']
            id_team_map[player_id] = player_team
        return id_team_map


class understatScrapeTeams(object):
    '''Initialize class by setting team name and appropriate url'''
    def __init__(self):
        self.base_url = 'https://understat.com/league/EPL/2018'
        self.url = self.base_url
        self.open_understat_page()
        self.get_JSON_data()

    '''Function to open understat webpage via Beautiful Soup.
       Returns Beautiful Soup object with page contents'''
    def open_understat_page(self):
        page_response = requests.get(self.url, timeout=5)
        page_content = bs(page_response.content, "html.parser")
        self.page_content = page_content

    '''Function takes in Beatiful Soup page content
       and returns relevant string with JSON data

    args
        html_content (BS object): BS html parsed content
    '''
    def get_JSON_data(self):
        html_data = str(self.page_content.find_all('script')[1])
        start = html_data.find("'")
        end = html_data.find("'", start+1)
        json_raw = html_data[start+1:end]
        json_decoded = json_raw.encode().decode('unicode_escape')
        json_data = json.loads(json_decoded)
        self.teams_data = json_data


    def get_teams_data(self):
        return self.teams_data

    def get_team_data(self, id):
        for team in self.teams_data:
            if team['id'] == id:
                return team
        return None

    def scrape(self):
        self.team_ids = self.teams_data.keys()
        teams_clean_data = []
        for team in self.teams_data.values():
            team_clean_data = {}
            team_clean_data['id'] = team['id']
            team_clean_data['team_name'] = team['title']
            team_clean_data['fixtures'] = team['history']
            teams_clean_data.append(team_clean_data)
        return teams_clean_data



'''
    def get_name_id_map(self):
        player_list = self.player_data
        name_id_mapping = {}

        for player in player_list:
            player_name = player['player_name']
            #if len(player_name) > 1:
            #   player_name = unidecode.unidecode(player_name[1])
            #else:
            #    player_name = unidecode.unidecode(player_name[0])
            player_id = player['id']
            name_id_mapping[player_name] = player_id

        return name_id_mapping

    def get_id_name_map(self):
        player_list = self.player_data
        id_name_mapping = {}

        for player in player_list:
            player_name = player['player_name']
            player_id = player['id']
            id_name_mapping[player_id] = player_name

        return id_name_mapping

    def get_id_team_map(self):
        player_list = self.player_data
        id_team_map = {}

        for player in player_list:
            player_id = player['id']
            player_team = player['team_title']
            id_team_map[player_id] = player_team
        return id_team_map
'''
