
import requests
import json
from datetime import datetime
import uuid

#Choose DNS namespace for generating uuids
#Choose "timestamp_created" for date (instead of "timestamp_updated")
#Choose "playtime_at_review" for hours (instead of "playtime_forever")

class steam_crawler():

    def __init__(self) -> None:
        self.app_id = 1382330

    def request_data(self, app_id :int): 
        call = requests.get(f"https://store.steampowered.com/appreviews/{self.app_id}?json=1")
        return json.loads(call.text)["reviews"]

    def generate_uuid(self, base_id: str):
        return uuid.uuid5(uuid.NAMESPACE_DNS, base_id).hex

    def parse_timestamp(self, timestamp: int):
        return str(datetime.fromtimestamp(timestamp).date())

    def get_json(self, 
                source : str, 
                game_name : str, 
                franchise_name : str):
        
        reviews_dict = self.request_data(app_id = self.app_id)
        output = []

        for data in reviews_dict: 
            output.append({
                "id": self.generate_uuid(data["recommendationid"]),
                "author": self.generate_uuid(data["author"]["steamid"]) ,
                "date": self.parse_timestamp(data["timestamp_created"]),
                "hours": data["author"]["playtime_at_review"],
                "content": data["review"],
                "comments": data["comment_count"],
                "source": source,
                "helpful": data["votes_up"],
                "funny": data["votes_funny"],
                "recommended": data["voted_up"],
                "franchise": franchise_name,
                "gameName": game_name
                })
            
        with open("test1.json", "w") as f:
            f.write(json.dumps(output))


steam_crawler().get_json(source = "steam", 
        game_name = "Persona 5 Strikers", 
        franchise_name = "ATLUS")
