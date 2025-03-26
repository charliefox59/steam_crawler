
import requests
import json
from datetime import datetime
import uuid
from datetime import date

class steam_crawler():

    def __init__(self, app_id: int, game_name: str, franchise_name : str, batch_size: int,
                 date_interval: tuple[str, str] | None = None) -> None:
        '''
        Initialise variables used across multiple functions. 

        Generate base url for get_reviews
        '''
        self.app_id = app_id
        self.game_name = game_name
        self.franchise_name = franchise_name
        self.batch_size = batch_size
        self.date_interval = date_interval

        self.params = {
            'json' : 1,
            'day_range' : 9223372036854775807,
            'num_per_page' : 100
            }
        self.source = "steam" 
        self.url = f"https://store.steampowered.com/appreviews/{self.app_id}"
        
    def get_reviews(self, params : dict) -> dict: 
            '''
            Calls steam API and returns a list of dictionaries of raw data.

            Return response in as dictionary
            '''
            return requests.get(self.url, params = params).json()

    def write_json(self, data : list[dict], filename : str) -> None:
        '''
        Write the formatted data to a .json file in "steam_crawler/output" folder
        '''
        path = "crawler/output/" + filename + ".json"
        with open(path, "w") as f:
            f.write(json.dumps(data))


    def generate_uuid(self, base_id: str) -> str:
        '''
        Input string (base_id), use uuid5 to return a UUID.
        
            UUID is reproducable if you input the same string. 

            Choose DNS namespace for generating UUIDs.

        Return UUID string
        '''
        return uuid.uuid5(uuid.NAMESPACE_DNS, base_id).hex

    def parse_timestamp(self, timestamp: int) -> str:
        '''
        Input timestamp from steam data and 
        
        Return a date string in "YYYY-MM-DD format"
        '''
        return str(datetime.fromtimestamp(timestamp).date())

    def format_data(self, reviews_dict : list[dict]) -> list[dict]:
        '''
        Input list of dictionaries containing reviews from the steam API.
            Generate UUIDs for the review ID and the author ID.
            Parse the timestamp into date format.
            Choose "timestamp_created" for date (instead of "timestamp_updated").
            Choose "playtime_at_review" for hours (instead of "playtime_forever").
            Add other relevant fields pulled from the crawled user reviews.
        Return list of dictionaries in the desired format.
        '''
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
        sorted_output = sorted(output, key=lambda x: (datetime.strptime(x['date'], '%Y-%m-%d'),x["id"]), reverse=True)

        if self.date_interval is not None: 
            return self.filter_dates(sorted_output)
        else: 
            return sorted_output
    
    def filter_dates(self, data: list[dict]) -> list[dict]:
        '''
        Input formatted reviews data

        Return filtered reviews beween 2 dates with format "YYYY-MM-DD"
        ''' 
        start_date, end_date = date.fromisoformat(self.date_interval[0]), date.fromisoformat(self.date_interval[1])
        return [review for review in data if start_date <= date.fromisoformat(review["date"]) <= end_date]


    
        
    def process_batch(self, batch_size : int) -> list[dict]:
        raw_review_data = []
        review_count = 0
        
        while review_count < batch_size:
            response = self.get_reviews(self.params)
            raw_review_data += response["reviews"]

            #Update cursor for next batch and the number of reviews
            self.params["cursor"] = response["cursor"]
            review_count = len(raw_review_data)

        return self.format_data(raw_review_data)
    
    def get_all_reviews(self) -> list[dict] : 
        '''
        Collect batches of steam reviews data until we have at all reviews.

            These batches are usually of size 100, from 'num_per_page'.

            Some batches are smaller due to steam automatically filtering off-topic reviews (aka "Review Bombs").
    
            Setting day_range = 9223372036854775807 removes the filter that only takes the last 365 days worth of reviews.

        Return a list of n dictionaries for n reviews
        '''
        self.params["cursor"] = "*"
        total_reviews = self.get_reviews(params)["query_summary"]["total_reviews"] 
        batch_sizes = [batch for batch in range(self.batch_size, total_reviews, self.batch_size)] + [total_reviews % self.batch_size]
        batch_count = 0
        for batch_size in batch_sizes:
            batch_count += 1
            print(f"Running batch {batch_count} with {batch_size} reviews")
            
            self.write_json(self.process_batch(batch_size), 
                            f"{self.game_name}_{batch_count}")

        
crawler = steam_crawler(app_id = 1382330,
              game_name = "Persona_5_Strikers",
              franchise_name = "ATLUS",
              batch_size = 5000)
              #date_interval=("2022-01-01","2023-01-01"))

params = {
            'json' : 1,
            'day_range' : 9223372036854775807,
            'cursor' : '*',
            'num_per_page' : 100
            }

response = crawler.get_all_reviews()