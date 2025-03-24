
import requests
import json
from datetime import datetime
import uuid

class steam_crawler():

    def __init__(self, app_id: int, game_name: str, franchise_name : str, n_reviews: int) -> None:
        '''
        Initialise variables used across multiple functions. 
        Generate base url for steam getreviews to avoid redundant code.
        '''
        self.app_id = app_id
        self.game_name = game_name
        self.franchise_name = franchise_name
        self.n_reviews = n_reviews

        self.source = "steam" 
        self.url = f"https://store.steampowered.com/appreviews/{self.app_id}"
        
    def get_reviews(self, params : dict): 
            '''Calls steam API and returns a list of dictionaries of raw data, passes the arguments within "params" to the call.'''
            return requests.get(self.url, params = params).json()

    def get_n_reviews(self): 
        '''
        Collect batches of steam reviews data until we have at least n review
        These batches are usually of size 100, from 'num_per_page' : 100
        Some batches are smaller due to steam automatically filtering off-topic reviews (aka "Review Bombs")
        Setting day_range = 9223372036854775807 removes the filter that only takes the last 365 days worth of reviews
        Return a list of n dictionaries for n reviews
        '''
        raw_review_data = []
        n_reviews = 0
        params = {
            'json' : 1,
            'day_range' : 9223372036854775807,
            'cursor' : '*',
            'num_per_page' : 100
            }
        ids = []
        print(f"Fetching...")
        while n_reviews < self.n_reviews:
            response = self.get_reviews(params)
            
            params["cursor"] = response["cursor"]
            n_reviews = len(raw_review_data)

            raw_review_data += response["reviews"]

        return raw_review_data[:self.n_reviews]

    def generate_uuid(self, base_id: str):
        '''
        Use uuid5 to return a UUID based on a string, this UUID is reproducable if you input the same string. 
        Choose DNS namespace for generating uuids
        '''
        return uuid.uuid5(uuid.NAMESPACE_DNS, base_id).hex

    def parse_timestamp(self, timestamp: int):
        '''Input timestamp from steam data and return a date string in "YYYY-MM-DD format"'''
        return str(datetime.fromtimestamp(timestamp).date())

    def format_data(self):
        '''
        Input list of dictionaries containing reviews from the steam API.
        Generate UUIDs for the review ID and the author ID.
        Parse the timestamp into date format.
        Choose "timestamp_created" for date (instead of "timestamp_updated").
        Choose "playtime_at_review" for hours (instead of "playtime_forever").
        Add other relevant fields pulled from the crawled user reviews.
        Return list of dictionaries in the desired format.
        '''
        reviews_dict = self.get_n_reviews()
        output = []

        for data in reviews_dict: 
            output.append({
                "id": self.generate_uuid(data["recommendationid"]),
                "author": self.generate_uuid(data["author"]["steamid"]) ,
                "date": self.parse_timestamp(data["timestamp_created"]),
                "hours": data["author"]["playtime_at_review"],
                "content": data["review"],
                "comments": data["comment_count"],
                "source": self.source,
                "helpful": data["votes_up"],
                "funny": data["votes_funny"],
                "recommended": data["voted_up"],
                "franchise": self.franchise_name,
                "gameName": self.game_name
                })
        sorted_output = sorted(output, key=lambda x: (datetime.strptime(x['date'], '%Y-%m-%d'),x["id"]))
        return sorted_output
        
    def write_json(self):
        '''
        Write the formatted data to a .json file in "steam_crawler/output" folder
        Name the file by the game name, replacing spaces with underscores.
        '''
        filename = self.game_name.replace(" ", "_") + "_reviews.json"
        with open("steam_crawler/output/" + filename, "w") as f:
            f.write(json.dumps(self.format_data()))


steam_crawler(app_id = 1382330,
              game_name = "Persona 5 Strikers",
              franchise_name = "ATLUS",
              n_reviews = 5000
              ).write_json()

