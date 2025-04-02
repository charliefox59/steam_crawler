
import requests
import json
from datetime import datetime
import uuid
from datetime import date
from pathlib import Path
from typing import Optional, Union

class steam_crawler():
    
    def __init__(self, app_id: int, game_name: str, franchise_name : str, batch_size: int,
                 date_interval: Optional[tuple[str, str]] = None) -> None:
        '''
        Initialise variables used across multiple functions.

        Generate base url for get_reviews

        Add option to initialise date_interval to filter the reviews (2 dates in DD-MM-YYYY format)
        '''
        self.app_id = app_id
        self.game_name = game_name
        self.franchise_name = franchise_name
        self.batch_size = batch_size
        self.date_interval = date_interval

    def write_json(self, data : list[dict[str, Union[str, int, bool]]], filename : str) -> None:
        '''
        Make file directory for new games

        Write the formatted data to a .json file in "steam_crawler/output/game_name" folder

        Add date interval to folder name if applicable
        '''
        if self.date_interval is None: 
            folder = f"crawler/output/{self.game_name}"
            Path(folder).mkdir(parents=True, exist_ok=True)
            path = f"{folder}/{filename}.json"
        else: 
            folder = f"crawler/output/{self.game_name}/{self.date_interval[0]}_{self.date_interval[1]}"
            Path(folder).mkdir(parents=True, exist_ok=True)
            path = f"{folder}/{filename}.json"

        with open(path, "w") as f:
            f.write(json.dumps(data))

    def generate_uuid(self, base_id: str) -> str:
        '''
        Input string (base_id), use uuid5 to return a UUID
        
            UUID is reproducable if you input the same string

            Choose DNS namespace for generating UUIDs

        Return UUID string
        '''
        return uuid.uuid5(uuid.NAMESPACE_DNS, base_id).hex

    def parse_timestamp(self, timestamp: int) -> str:
        '''
        Input timestamp from steam data and 
        
        Return a date string in "YYYY-MM-DD format"
        '''
        return str(datetime.fromtimestamp(timestamp).date())
        
    def to_timestamp(self, date : str) -> datetime.timestamp:
         '''
        Input date string in "YYYY-MM-DD" format
        
        Return a date timestamp for filtering dates
        '''
         return datetime.timestamp(datetime.strptime(date,'%Y-%m-%d'))
    
    def request(self):
        ''' 
        Loop through requests of all steam reviews for a specific game

        Yield individual review dictionaries
        '''
        url = f"https://store.steampowered.com/appreviews/{self.app_id}"
        params = {
        'json' : 1,
        'day_range' : 9223372036854775807,
        'num_per_page' : 100, 
        "filter" : "recent",
        "language" : "all",
        "purchase_type" : "all",
        "filter_offtopic_activity": 0,
        "cursor" : "*"
        }
        
        r = requests.get(url, params).json()
        self.total_reviews = r["query_summary"]["total_reviews"] 

        reviews_seen = 0
        while reviews_seen < self.total_reviews: 
            for review in r["reviews"]:
                yield review
            reviews_seen += len(r["reviews"])
            params["cursor"] = r["cursor"]
            r = requests.get(url, params).json()

    def filter_data(self): 
        '''
        Input yield from request()

        If no date_interval exists, yield all reviews

        Else (date_interval exists), yield reviews within the interval 
        '''
        for d in self.request():
            if self.date_interval is None:
                yield d 
            elif self.to_timestamp(self.date_interval[0]) < d["timestamp_created"] <= self.to_timestamp(self.date_interval[1]):
                yield d

    def format_data(self):
        '''
        Loop through filtered data

        Format the data and append it to output

        Write output to json file every 5000 reviews and then at the end
        '''
        out = []
        batch_number = 0
        for d in self.filter_data():
                out.append({
                "id": self.generate_uuid(d["recommendationid"]),
                "author": self.generate_uuid(d["author"]["steamid"]) ,
                "date": self.parse_timestamp(d["timestamp_created"]),
                "hours": d["author"]["playtime_forever"],
                "content": d["review"],
                "comments": d["comment_count"],
                "source": "steam",
                "helpful": d["votes_up"],
                "funny": d["votes_funny"],
                "recommended": d["voted_up"],
                "franchise": self.franchise_name,
                "gameName": self.game_name
                })
                if len(out) == 5000:
                    self.write_json(out, str(batch_number))
                    batch_number += 1
                    out = []

        self.write_json(out, str(batch_number))

if __name__ == "__main__": #pragma: no-cover
    crawler = steam_crawler(app_id = 1382330,
                game_name = "Persona_5_Strikers",
                franchise_name = "ATLUS",
                batch_size = 5000,
                date_interval=("2022-01-01","2023-01-01"))

    out = crawler.format_data()

