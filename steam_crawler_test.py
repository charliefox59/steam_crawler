from steam_crawler import steam_crawler
import unittest, os, sys
from unittest.mock import MagicMock,patch,call
sys.path.append(os.path.realpath(".."))
sys.path.append(os.path.realpath("."))

class test_crawler(unittest.TestCase):

    # def setUp(self):
    #     mock_id = MagicMock(int)
    #     mock_game_name = MagicMock(str)
    #     mock_franchise_name = MagicMock(str)
    #     mock_n_reviews = MagicMock(int)
    #     self.uut = steam_crawler(app_id = mock_id, 
    #                          game_name = mock_game_name,
    #                          franchise_name = mock_franchise_name,
    #                          n_reviews = mock_n_reviews)
    #     return super().setUp()
    # 7 Functions: 
    #__init__() (6 lines of code)

    def test_class_loader_mock(self):
        mock_id = MagicMock(int)
        mock_game_name = MagicMock(str)
        mock_franchise_name = MagicMock(str)
        mock_n_reviews = MagicMock(int)
        _uut = steam_crawler(app_id = mock_id, 
                             game_name = mock_game_name,
                             franchise_name = mock_franchise_name,
                             n_reviews = mock_n_reviews)
        self.assertEqual(_uut.app_id, mock_id)
        self.assertEqual(_uut.game_name, mock_game_name)
        self.assertEqual(_uut.franchise_name, mock_franchise_name)
        self.assertEqual(_uut.n_reviews, mock_n_reviews)

    #get_reviews(params) (1 line of code )

    #get_n_reviews() (18 lines of code)

    #generate_uuid(base_id) (1 lines of code)

    #parse_timestamp(timestamp) (1 lines of code)

    #format_data() (20 lines of code)

    #write_json() (3 lines of code)