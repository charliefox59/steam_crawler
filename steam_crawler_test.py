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
        return super().setUp()
    # 7 Functions: 
    #__init__() (6 lines of code)

    def test_class_loader_mock(self):
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

    #get_reviews(params) (1 line of code )
    @patch("steam_crawler.requests.get")
    def test_get_reviews(self, get_requests_patch):
        params = {
            'json' : 1,
            'day_range' : 9223372036854775807,
            'cursor' : '*',
            'num_per_page' : 100
            }
        self.assertEqual(get_requests_patch(self.uut.url,params).json(),
                         self.uut.get_reviews(params))

    #generate_uuid(base_id) (1 lines of code)
    @patch("steam_crawler.uuid")
    def test_generate_uuid(self, uuid_patch):
        base_id_mock = MagicMock(int)
        r = self.uut.generate_uuid(base_id_mock)

        self.assertEqual(r, 
            uuid_patch.uuid5(uuid_patch.NAMESPACE_DNS, base_id_mock).hex)
        
    #parse_timestamp(timestamp) (1 lines of code)
    @patch("steam_crawler.datetime")
    def test_parse_timestamp(self, datetime_patch): 
        timestamp_mock = MagicMock(int)
        timestamp_mock.return_value = 1652341169

        r = self.uut.parse_timestamp(timestamp_mock)
        self.assertEqual(r, 
            str(datetime_patch.fromtimestamp(timestamp_mock).date()))

    #format_data() (20 lines of code)

    #write_json() (3 lines of code)

    #def test_write_json(self):

    #get_all_reviews() (18 lines of code)
    @patch("steam_crawler.steam_crawler.write_json")
    @patch("steam_crawler.steam_crawler.format_data")
    @patch("steam_crawler.steam_crawler.get_reviews")
    def test_get_all_reviews(self, get_reviews_patch, format_data_patch, write_json_patch,):
        
        
        r = self.uut.get_all_reviews()
        
        

