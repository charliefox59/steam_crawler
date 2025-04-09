## steam_crawler

# Hertzian Junior Technical Test 

To initialise to crawler:

```
crawler = SteamCrawler(app_id = 1382330,
                game_name = "Persona_5_Strikers",
                franchise_name = "ATLUS",
                batch_size = 5000)
```

This includes the option to change the SteamCrawler variables for a specific steam game and batch size<br/><br/>

To filter between 2 dates, initialise following variable in the crawler:
```
date_interval=("2022-01-01","2023-01-01")
```
This is a tuple of 2 strings, with date formats "YYYY-MM-DD"<br/><br/>


To run the crawler:

```
crawler.crawl(batch_number = x)
```

Where x is the maximum number of batches required.<br/><br/>

This will output the reviews to file "output/all" or "output/date_interval", depending on if a date filter is used.