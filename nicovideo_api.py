# -*- coding: utf-8 -*-

'''
 -----------------------------------------------------------------------------------
|Copyright (c) 2016 http://www.guri-tech.com 										|
|Twitter: @GuriTech 																|
|Released under the MIT license  													|
 -----------------------------------------------------------------------------------
 '''

import requests
import xml.etree.ElementTree as ET
import urllib.parse
import re

class NicoVideo_API:
	#初期化
	def __init__(self):
		self.__session = requests.Session()
		self.__api_token = ""

	def get_video_info(self,video_id):
		url = "http://ext.nicovideo.jp/api/getthumbinfo/" + video_id
		r = requests.get(url)
		result = {}
		root = ET.fromstring(r.text)
		for e in root.findall(".//"):
			if e.text[0] == '\n':
				continue

			if e.tag not in result.keys():
				result[e.tag] = e.text
			else:
				if isinstance(result[e.tag],str):
					result[e.tag] = [result[e.tag]]
				result[e.tag].append(e.text)
		return result

	def get_video_comments(self,video_id):
		pass

	def get_video_original_url(self,video_id):
		url = "http://www.nicovideo.jp/api/getflv?v="+video_id
		r = self.__session.get(url)
		print(urllib.parse.unquote(r.text.split("&")[2].replace("url=","")))

	def view_video(self,video_id):
		self.__session.get("http://www.nicovideo.jp/watch/"+video_id)

	def set_cookie(self,mailadd,password):
		page_url = "https://account.nicovideo.jp/api/v1/login?show_button_twitter=1&site=niconico&show_button_facebook=1&next_url="
		params = {"mail_tel":mailadd,
				"password":password}
		r = self.__session.post(page_url,params=params)

	#Snapshot検索APIを実行する(実装後回し)
	def snapshot_search(self,search_query):
		end_point = "http://api.search.nicovideo.jp/api/v2/snapshot/video/contents/search"
		return requests.post(end_point,json = search_query) 

	#Snapshot検索APIの結果更新日時を取得する
	def get_last_renovation_time(self):
		return requests.get("http://api.search.nicovideo.jp/api/v2/snapshot/version")

	'''About Comment Information'''
	#動画内のコメント情報を取得する(修正中)
	def get_comment_information(self,res_from = 10):
		try:
			response = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.__cookie)).open("http://www.nicovideo.jp/api/getflv?v=" + self.__video_id).read()

			response = response.split("&")
			thread_id = response[0].replace("thread_id=","")
			ms = response[4].replace("ms_sub=http%3A%2F%2Fsub.msg.nicovideo.jp%2F","").replace("%2Fapi%2F","")
			comments = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.__cookie)).open("http://msg.nicovideo.jp/"+ms+"/api/thread?version=20090904&thread="+thread_id+"&res_from=-"+str(res_from)).read()
		except:
			return -1
		return xmltodict.parse(comments)["packet"]

	#仕様が変わっため使用不可
	def get_history_api_token(self):
		r = self.__session.get("http://www.nicovideo.jp/my/history")
		print(r.text)
		index = r.text.find("VideoViewHistory.Action(")
		print(r.text[index:].split("\'")[1])
		self.__api_token = r.text[index:].split("\'")[1]

	#視聴履歴を全削除する（使用不可）
	def delete_all_view_history(self):
		page_url = "http://www.nicovideo.jp/my/history"
		params = {
			'mode' : 'delete',
			'video_id' : 'all',
			'token' : self.__api_token,
			'innerPage' : '1'
		}

		self.__session.post(page_url,params=params)
	#特定の視聴履歴のみを削除（使用不可）
	def delete_view_history(self,video_id):
		self.get_history_api_token()
		page_url = "http://www.nicovideo.jp/my/history"
		params = {
			'mode' : 'delete',
			'video_id' : video_id,
			'token' : self.__api_token,
			'innerPage' : '1'
		}
		
		self.__session.post(page_url,params=params)