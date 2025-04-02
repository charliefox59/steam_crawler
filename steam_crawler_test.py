import steam_crawler
import unittest, os, sys
from unittest.mock import MagicMock,patch,call
sys.path.append(os.path.realpath(".."))
sys.path.append(os.path.realpath("."))

class test_crawler(unittest.TestCase):

    def setUp(self):
        mock_id = MagicMock(int)
        mock_game_name = MagicMock(str)
        mock_franchise_name = MagicMock(str)
        mock_batch_size = MagicMock(int)
        mock_date_interval = MagicMock(tuple)
        self.uut = steam_crawler.steam_crawler(app_id = mock_id, 
                             game_name = mock_game_name,
                             franchise_name = mock_franchise_name,
                             batch_size = mock_batch_size,
                             date_interval = mock_date_interval)
        return super().setUp()
    
    def test_class_loader_default(self):
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
        self.assertEqual(_uut.date_interval, None)

    def test_class_loader_filterdates(self):
        mock_id = MagicMock(int)
        mock_game_name = MagicMock(str)
        mock_franchise_name = MagicMock(str)
        mock_batch_size = MagicMock(int)
        mock_date_interval = MagicMock(tuple)

        _uut = steam_crawler.steam_crawler(app_id = mock_id, 
                            game_name = mock_game_name,
                            franchise_name = mock_franchise_name,
                            batch_size = mock_batch_size,
                            date_interval = mock_date_interval)
        
        self.assertEqual(_uut.app_id, mock_id)
        self.assertEqual(_uut.game_name, mock_game_name)
        self.assertEqual(_uut.franchise_name, mock_franchise_name)
        self.assertEqual(_uut.batch_size, mock_batch_size)
        self.assertEqual(_uut.date_interval, mock_date_interval)

    @patch('builtins.open') 
    @patch("steam_crawler.json")
    @patch("steam_crawler.Path")
    def test_write_json(self, path_patch, json_patch, open_patch):
        data_mock = MagicMock(dict)
        filename_mock = MagicMock(str)

        folder_mock = f"crawler/output/{self.uut.game_name}/{self.uut.date_interval[0]}_{self.uut.date_interval[1]}"
        self.uut.date_interval.reset_mock()

        self.uut.write_json(data_mock,filename_mock)
        
        path_patch.assert_has_calls([call(folder_mock)])
        path_patch().mkdir.assert_has_calls([call(parents=True, exist_ok=True)])

        json_patch.dumps.assert_called_with(data_mock)

        open_patch.assert_has_calls([call(f"{folder_mock}/{filename_mock}.json","w"),
                                    call().__enter__(),
                                     call().__enter__().write(json_patch.dumps(data_mock)),
                                     call().__exit__(None, None, None)])
        
    @patch('builtins.open') 
    @patch("steam_crawler.json")
    @patch("steam_crawler.Path")
    def test_write_json_nofilter(self, path_patch, json_patch, open_patch):
        self.uut.date_interval = None
        data_mock = MagicMock(dict)
        filename_mock = MagicMock(str)

        folder_mock = f"crawler/output/{self.uut.game_name}/all"

        self.uut.write_json(data_mock,filename_mock)
        
        path_patch.assert_has_calls([call(folder_mock)])
        path_patch().mkdir.assert_has_calls([call(parents=True, exist_ok=True)])

        json_patch.dumps.assert_called_with(data_mock)

        open_patch.assert_has_calls([call(f"{folder_mock}/{filename_mock}.json","w"),
                                    call().__enter__(),
                                     call().__enter__().write(json_patch.dumps(data_mock)),
                                     call().__exit__(None, None, None)])

    @patch("steam_crawler.uuid")
    def test_generate_uuid(self, uuid_patch):
        base_id_mock = MagicMock(int)
        r = self.uut.generate_uuid(base_id_mock)

        uuid_patch.uuid5.assert_called_with(uuid_patch.NAMESPACE_DNS, base_id_mock)

        self.assertEqual(r, uuid_patch.uuid5(uuid_patch.NAMESPACE_DNS, base_id_mock).hex)
    
    @patch("steam_crawler.datetime")
    def test_parse_timestamp(self, datetime_patch): 
        timestamp_mock = MagicMock(int)
        r = self.uut.parse_timestamp(timestamp_mock)

        datetime_patch.fromtimestamp.assert_called_with(timestamp_mock)
        datetime_patch.fromtimestamp().date.assert_called_with()

        self.assertEqual(r, str(datetime_patch.fromtimestamp(timestamp_mock).date()))
   
    @patch("steam_crawler.datetime")
    def test_to_timestamp(self,datetime_patch):
        date_mock = MagicMock(str)
        r = self.uut.to_timestamp(date_mock)

        datetime_patch.assert_has_calls([call.strptime(date_mock,'%Y-%m-%d'),
                                         call.timestamp(datetime_patch.strptime(date_mock,'%Y-%m-%d'))])
        
        self.assertEqual(r, datetime_patch.timestamp(datetime_patch.strptime(date_mock,'%Y-%m-%d')))

    @patch("steam_crawler.requests.get")
    def test_request(self,get_patch):
        review_mock1, review_mock2 = MagicMock(dict), MagicMock(dict)
        get_patch().json().__getitem__().__getitem__().__gt__.side_effect = [True, False]
        get_patch().json().__getitem__().__iter__.return_value = [review_mock1, review_mock2]
        r = self.uut.request()
        _r = r.__next__()
        self.assertEqual(_r, review_mock1)
        

        #ADD FIRST ITER CHECKS


        _r = r.__next__()
        self.assertEqual(_r, review_mock2)


        #ADD NEXT ITER CHECKS


        self.assertRaises(StopIteration, r.__next__, )

    @patch("steam_crawler.steam_crawler.to_timestamp")
    @patch("steam_crawler.steam_crawler.request")
    def test_filter_data(self,request_patch,to_timestamp_mock):
        review_mock= MagicMock(dict)
        request_patch().__iter__.return_value = [review_mock]
        request_patch.reset_mock()

        review_mock.__getitem__().__gt__.return_value= True
        review_mock.__getitem__().__le__.return_value= True
        r = self.uut.filter_data()
        _r = r.__next__()

        self.assertEqual(_r, review_mock)
        
        to_timestamp_mock.assert_has_calls(
            [call(self.uut.date_interval.__getitem__(0)),
             call().__lt__(review_mock.__getitem__(0)),
             call(self.uut.date_interval.__getitem__(1))])
        
        request_patch.assert_has_calls(
            [call(),call().__iter__()])

        review_mock.assert_has_calls(
            [call.__getitem__('timestamp_created'),
             call.__getitem__().__gt__(to_timestamp_mock(self.uut.date_interval.__getitem__(0))),
             call.__getitem__().__le__(to_timestamp_mock(self.uut.date_interval.__getitem__(1)))])
        
        self.assertRaises(StopIteration, r.__next__, )                    
        
    @patch("steam_crawler.steam_crawler.request")
    def test_filter_data_nofilter(self,request_patch):
        self.uut.date_interval = None
        review_mock= MagicMock(dict)

        request_patch().__iter__.return_value = [review_mock]
        request_patch.reset_mock()

        r = self.uut.filter_data()
        _r = r.__next__()

        request_patch.assert_has_calls(
            [call(),call().__iter__()])

        self.assertEqual(_r, review_mock)

        self.assertRaises(StopIteration, r.__next__, )

    @patch("steam_crawler.steam_crawler.write_json")
    @patch("steam_crawler.steam_crawler.filter_data")
    @patch("steam_crawler.steam_crawler.generate_uuid")
    @patch("steam_crawler.steam_crawler.parse_timestamp")
    def test_format_data(self, parse_timestamp_patch, generate_uuid_patch, filter_data_patch, write_json_patch):
        id_mock, steam_id_mock, review_mock, = MagicMock(str), MagicMock(str), MagicMock(str)
        playtime_mock, comment_count_mock = MagicMock(int), MagicMock(int)
        votes_up_mock, votes_funny_mock = MagicMock(int), MagicMock(int)
        voted_up_mock,timestamp_created_mock = MagicMock(bool), MagicMock(int)

        self.uut.date_interval.reset_mock()

        filter_data_patch.return_value = [{"recommendationid" : id_mock,
                   "author" : {"steamid" : steam_id_mock,
                               "playtime_forever" : playtime_mock
                               },
                   "timestamp_created" : timestamp_created_mock,
                   "review" : review_mock,
                   "comment_count" : comment_count_mock,
                   "votes_up" : votes_up_mock,
                   "votes_funny" : votes_funny_mock,
                   "voted_up" : voted_up_mock
                   }]
        
        r = self.uut.format_data()
        
        generate_uuid_patch.assert_has_calls([call(id_mock),call(steam_id_mock)])
        parse_timestamp_patch.assert_called_with(timestamp_created_mock)

        formtted_data = [{
                "id": generate_uuid_patch(id_mock),
                "author": generate_uuid_patch(steam_id_mock) ,
                "date": parse_timestamp_patch(timestamp_created_mock),
                "hours": playtime_mock,
                "content": review_mock,
                "comments": comment_count_mock,
                "source": "steam",
                "helpful": votes_up_mock,
                "funny": votes_funny_mock,
                "recommended": voted_up_mock,
                "franchise": self.uut.franchise_name,
                "gameName": self.uut.game_name
                }]
        filter_data_patch.assert_called_with()
        write_json_patch.assert_called_with(formtted_data, "0")
    
    

    
    