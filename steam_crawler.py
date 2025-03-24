
import requests
import json
from datetime import datetime
import uuid

#Choose DNS namespace for generating uuids
#Choose "timestamp_created" for date (instead of "timestamp_updated")
#Choose "playtime_at_review" for hours (instead of "playtime_forever")

class steam_crawler():

    def __init__(self, app_id: int, game_name: str, franchise_name : str, n_reviews: int) -> None:
        self.app_id = app_id
        self.game_name = game_name
        self.franchise_name = franchise_name
        self.n_reviews = n_reviews

        self.source = "steam" 
        self.url = f"https://store.steampowered.com/appreviews/{self.app_id}"
        
    def get_reviews(self, params : dict): 
            return requests.get(self.url, params = params).json()

    def get_n_reviews(self): 
        raw_review_data = []
        n_reviews = 0
        params = {
            'json' : 1,
            'day_range' : 365,
            'cursor' : '*',
            'num_per_page' : 100
            }
        
        print(f"Fetching...")
        while n_reviews < self.n_reviews:
            response = self.get_reviews(params)
            
            params["cursor"] = response["cursor"]
            n_reviews = len(raw_review_data)

            raw_review_data += response["reviews"]
        return raw_review_data[:self.n_reviews]

    def generate_uuid(self, base_id: str):
        return uuid.uuid5(uuid.NAMESPACE_DNS, base_id).hex

    def parse_timestamp(self, timestamp: int):
        return str(datetime.fromtimestamp(timestamp).date())

    def format_data(self):
        
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
        return output
        
    def write_json(self):
        filename = self.game_name.replace(" ", "_") + "_reviews.json"
        with open("steam_crawler/output/" + filename, "w") as f:
            f.write(json.dumps(self.format_data()))


steam_crawler(app_id = 1382330,
              game_name = "Persona 5 Strikers",
              franchise_name = "ATLUS",
              n_reviews = 5000
              ).write_json()

