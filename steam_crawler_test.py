import steam_crawler
import unittest, os, sys
from unittest.mock import MagicMock,patch,call
import requests
sys.path.append(os.path.realpath(".."))
sys.path.append(os.path.realpath("."))

class test_crawler(unittest.TestCase):

    def setUp(self):
        app_id = 1382330
        game_name = "Persona 5 Strikers"
        franchise_name = "ATLUS"
        batch_size = 5000
        self.uut = steam_crawler.steam_crawler(app_id = app_id, 
                             game_name = game_name,
                             franchise_name = franchise_name,
                             batch_size = batch_size)
        
        mock_id = MagicMock(int)
        mock_game_name = MagicMock(str)
        mock_franchise_name = MagicMock(str)
        mock_batch_size = MagicMock(int)
        mock_id.return_value = 1382330
        self.mock_uut = steam_crawler.steam_crawler(app_id = mock_id, 
                             game_name = mock_game_name,
                             franchise_name = mock_franchise_name,
                             batch_size = mock_batch_size)
        return super().setUp()
    # 7 Functions: 
    #__init__() (6 lines of code)

    def test_class_loader(self):
        mock_id = MagicMock(int)
        mock_game_name = MagicMock(str)
        mock_franchise_name = MagicMock(str)
        mock_batch_size = MagicMock(int)

        _uut = steam_crawler.steam_crawler(app_id = mock_id, 
                             game_name = mock_game_name,
                             franchise_name = mock_franchise_name,
                             batch_size = mock_batch_size)
        
        self.assertEqual(_uut.app_id, mock_id)
        self.assertEqual(_uut.game_name, mock_game_name)
        self.assertEqual(_uut.franchise_name, mock_franchise_name)
        self.assertEqual(_uut.batch_size, mock_batch_size)
        self.assertIsInstance(_uut.params,dict)
        self.assertEqual(_uut.source,"steam")
        self.assertIsInstance(_uut.url,str)

    #get_reviews(params) (1 line of code )
    @patch("steam_crawler.requests.get")
    def test_get_reviews(self, get_requests_patch):
        r = self.mock_uut.get_reviews(params = self.mock_uut.params)

        get_requests_patch.assert_called_with(self.mock_uut.url, params = self.mock_uut.params)
        get_requests_patch().json.assert_called_with()

        self.assertEqual(get_requests_patch(self.mock_uut.url,self.mock_uut.params).json(),r)

    #generate_uuid(base_id) (1 lines of code)
    @patch("steam_crawler.uuid")
    def test_generate_uuid(self, uuid_patch):
        base_id_mock = MagicMock(int)
        r = self.uut.generate_uuid(base_id_mock)

        uuid_patch.uuid5.assert_called_with(uuid_patch.NAMESPACE_DNS, base_id_mock)

        self.assertEqual(r, 
            uuid_patch.uuid5(uuid_patch.NAMESPACE_DNS, base_id_mock).hex)
        
    #parse_timestamp(timestamp) (1 lines of code)
    @patch("steam_crawler.datetime")
    def test_parse_timestamp(self, datetime_patch): 
        timestamp_mock = MagicMock(int)
        timestamp_mock.return_value = 1652341169

        r = self.uut.parse_timestamp(timestamp_mock)

        datetime_patch.fromtimestamp.assert_called_with(timestamp_mock)
        datetime_patch.fromtimestamp().date.assert_called_with()

        self.assertEqual(r, 
            str(datetime_patch.fromtimestamp(timestamp_mock).date()))

    #format_data() (20 lines of code)
    @patch("steam_crawler.datetime")
    @patch("steam_crawler.steam_crawler.generate_uuid")
    @patch("steam_crawler.steam_crawler.parse_timestamp")
    def test_format_data(self, parse_timestamp_mock, generate_uuid_mock, datetime_mock):
       
        id_mock, steam_id_mock, review_mock, = MagicMock(str), MagicMock(str), MagicMock(str)
        playtime_mock, comment_count_mock = MagicMock(int), MagicMock(int)
        votes_up_mock, votes_funny_mock = MagicMock(int), MagicMock(int)
        voted_up_mock = MagicMock(bool)
        timestamp_created_mock = MagicMock(int)
        timestamp_created_mock.return_value = 1652341169

        reviews = [{"recommendationid" : id_mock,
                   "author" : {"steamid" : steam_id_mock,
                               "playtime_at_review" : playtime_mock
                               },
                   "timestamp_created" : timestamp_created_mock,
                   "review" : review_mock,
                   "comment_count" : comment_count_mock,
                   "votes_up" : votes_up_mock,
                   "votes_funny" : votes_funny_mock,
                   "voted_up" : voted_up_mock
                   }]
        
        r = self.uut.format_data(reviews)
        r0 = r[0]

        generate_uuid_mock.assert_has_calls([call(id_mock),call(steam_id_mock)])
        parse_timestamp_mock.assert_called_with(timestamp_created_mock)
        datetime_mock.strptime.assert_called_with(parse_timestamp_mock(timestamp_created_mock), '%Y-%m-%d')

        self.assertEqual(generate_uuid_mock(id_mock), r0["id"])
        self.assertEqual(generate_uuid_mock(steam_id_mock), r0["author"])
        self.assertEqual(parse_timestamp_mock(timestamp_created_mock), r0["date"])
        self.assertEqual(playtime_mock, r0["hours"])
        self.assertEqual(review_mock, r0["content"])
        self.assertEqual(comment_count_mock, r0["comments"])
        self.assertEqual(self.uut.source, r0["source"])
        self.assertEqual(votes_up_mock, r0["helpful"])
        self.assertEqual(votes_funny_mock, r0["funny"])
        self.assertEqual(voted_up_mock, r0["recommended"])
        self.assertEqual(self.uut.franchise_name, r0["franchise"])
        self.assertEqual(self.uut.game_name, r0["gameName"])
        
        
  

    #process_batch() (8 lines of code)
    # @patch("steam_crawler.steam_crawler.format_data")
    # @patch("steam_crawler.steam_crawler.get_reviews")
    # def test_process_batch(self,get_reviews_patch, format_data_patch):
    #     batch_size = MagicMock(int)
    #     batch_size.return_value = 100 

    #     r = self.mock_uut.process_batch(batch_size.return_value)       

        # review_count_mock = MagicMock(int)
        # review_count_mock.return_value = 0
        # raw_review_data = MagicMock(list)

        # batch_size_mock = MagicMock(int)


    #get_all_reviews() (8 lines of code)
    @patch("steam_crawler.steam_crawler.write_json")
    @patch("steam_crawler.steam_crawler.process_batch")
    @patch("steam_crawler.steam_crawler.format_data")
    @patch("steam_crawler.steam_crawler.get_reviews")
    def test_get_all_reviews(self, get_reviews_patch, format_data_patch,
                             process_batch_patch, write_json_patch):
        
        batch_size_mock = self.mock_uut.batch_size
        total_reviews_mock = get_reviews_patch(self.mock_uut.params)["query_summary"]["total_reviews"] 
        batch_sizes_mock = [batch for batch in range(batch_size_mock, total_reviews_mock, batch_size_mock)] + [total_reviews_mock % batch_size_mock]
        
        r = self.mock_uut.get_all_reviews()

        self.assertEqual(self.mock_uut.params["cursor"],"*")
        
        total_reviews_mock.__index__.assert_called_with()
        total_reviews_mock.__mod__.assert_called_with(batch_size_mock)
        total_reviews_mock.__mod__().__str__.assert_called_with()

        process_batch_patch.assert_called_with(batch_sizes_mock.__getitem__(0))
        write_json_patch.assert_called_with(process_batch_patch(batch_sizes_mock.__getitem__(0)), 
                                            f"{self.mock_uut.game_name}_1")
        

    #filter_dates() (2 lines of code)

    #write_json() (3 lines of code)

    #def test_write_json(self):
        
        
    
        
        
 # #reviews = MagicMock(list)
        # [{"recommendationid" : '115334066',
        #            "author" : {"steamid" : '76561198142833490',
        #                        "playtime_at_review" : 1647
        #                        },
        #            "timestamp_created" : 1652341169,
        #            "review" : "This is basically just a sequel to Persona 5, set half a year after the events that took place in the game, and I would only play Strikers if you know the entire Persona 5 story. This is a pretty good sequel, and I recommend anyone that completed Persona 5 to buy this if you want more of the Phantom Thieves, and see more adventures from them, the only problem I have is...\n\n̶A̶t̶l̶u̶s̶ ̶c̶h̶o̶s̶e̶ ̶t̶o̶ ̶p̶o̶r̶t̶ ̶t̶h̶i̶s̶,̶ ̶a̶n̶d̶ ̶n̶o̶t̶ ̶R̶o̶y̶a̶l̶.̶ ̶f̶e̶e̶l̶s̶b̶a̶d̶m̶a̶n̶\n\n\nEDIT: I take back what I said about Atlus not porting Royal....IT'S COMING TO PC FINALLY\n\nanother EDIT: IT'S COMING TO STEAM TOO LETS GOOOO\n\nanother another EDIT: this is late but it's on steam now so GO BUY!!!",
        #            "comment_count" : 0,
        #            "votes_up" : 61,
        #            "votes_funny" : 4,
        #            "voted_up" : True
        #            }]
