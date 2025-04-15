
import requests
import json
import utils
from pathlib import Path
from typing import Optional, Union
from collections.abc import Generator

class SteamCrawler():

    app_id: int 
    game_name: str
    franchise_name: str
    batch_size: int
    date_interval: Optional[tuple[str, str]]

    def __init__(self, app_id: int, game_name: str, 
                 franchise_name: str, batch_size: int = 5000, 
                 date_interval: Optional[tuple[str, str]] = None) -> None:
        '''
        Initialise variables used across multiple functions.

        Generate base url for get_reviews

        Add option to initialise date_interval to filter the reviews (2 dates in YYYY-MM-DD format)
        '''
        self.app_id = app_id
        self.game_name = game_name
        self.franchise_name = franchise_name
        self.batch_size = batch_size
        self.date_interval = date_interval

    def write_json(self, data: list[dict[str, Union[str, int, bool]]], filename: str) -> None:
        '''
        Make file directory for new games

        Write the formatted data to a .json file in "steam_crawler/output/game_name" folder

        Add date interval to folder name if applicable
        '''
        if self.date_interval is None: 
            folder = f"output/{self.game_name}/all"
            Path(folder).mkdir(parents=True, exist_ok=True)
            path = f"{folder}/{filename}.json"
        else: 
            folder = f"output/{self.game_name}/{self.date_interval[0]}_{self.date_interval[1]}"
            Path(folder).mkdir(parents=True, exist_ok=True)
            path = f"{folder}/{filename}.json"

        with open(path, "w") as f:
            f.write(json.dumps(data))

    def generate_reviews(self) -> Generator[dict[str, Union[str, int, bool]]]:
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

    def filter_data(self) -> Generator[dict[str, Union[str, int, bool]]]:
        '''
        Input yield from request()

        If no date_interval exists, yield all reviews

        Else (date_interval exists), yield reviews within the interval 
        '''
        for d in self.generate_reviews():
            if self.date_interval is None:
                yield d 
            elif utils.to_timestamp(self.date_interval[0]) < d["timestamp_created"] <= utils.to_timestamp(self.date_interval[1]):
                yield d

    def format_data(self, d: dict[str, Union[str, int, bool]]) -> dict[str, Union[str, int, bool]]:
        '''
        Input steam api data 

        Return data in preferred format
        '''
        return {"id": utils.generate_uuid(d["recommendationid"]),
                "author": utils.generate_uuid(d["author"]["steamid"]) ,
                "date": utils.parse_timestamp(d["timestamp_created"]),
                "hours": d["author"]["playtime_forever"],
                "content": d["review"],
                "comments": d["comment_count"],
                "source": "steam",
                "helpful": d["votes_up"],
                "funny": d["votes_funny"],
                "recommended": d["voted_up"],
                "franchise": self.franchise_name,
                "gameName": self.game_name}
    
    def crawl(self, num_batches: Optional[int] = None) -> None:
        '''
        Loop through filtered data

        Format the data and append it to output

        Write output to json file every batch_size reviews 
        
        Write leftover reviews to final json file
        '''
        out = []
        batch_number = 0
        for d in self.filter_data():
            out.append(self.format_data(d))
            if len(out) == self.batch_size:
                self.write_json(out, str(batch_number))
                out = []
                batch_number += 1
                if batch_number == num_batches: 
                        break
        if out:
            self.write_json(out, str(batch_number))

if __name__ == "__main__":
    crawler = SteamCrawler(app_id = 730,
                game_name = "CS2",
                franchise_name = "Valve",
                batch_size = 5000,
                date_interval=("2022-04-08","2025-04-15"))

    out = crawler.crawl(num_batches = 10)

