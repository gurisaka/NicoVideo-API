# -*- coding: utf-8 -*-

'''
 -----------------------------------------------------------------------------------
|Copyright (c) 2016 http://www.guri-tech.com 										|
|Twitter: @GuriTech 																|
|Released under the MIT license  													|
 -----------------------------------------------------------------------------------
 '''

#required Non-standard modules
import xmltodict

#required standard modules
import cookielib
import urllib
import urllib2
import re
import json
import requests
import sys
import time
from cookielib import CookieJar

class NicoAPI:
	__cookie = CookieJar()
	__connection_error = 0
	__token = 0
	__video_id = ""
	__video_info = {
		'video_id' : ''
	}

	#初期化
	def __init__(self,mailadd,passwd):
		self.set_cookie_by_login(mailadd,passwd)
		self.__connection_error = self.__connection_Check()

	def get_connection_error(self):
		return self.__connection_error

	'''About Cookie setting'''
	#ログインによってCookieを作成する
	def set_cookie_by_login(self,mailadd,passwd):
		page_url = "https://account.nicovideo.jp/api/v1/login?show_button_twitter=1&site=niconico&show_button_facebook=1&next_url="
		post_value = {
			'mail_tel' : mailadd,
			'password' :passwd
		}
		try:
			urllib2.build_opener(urllib2.HTTPCookieProcessor(self.__cookie)).open(page_url,urllib.urlencode(post_value))
		except:
			return -1
		self.__connection_error = self.__connection_Check()
		return self.__connection_error

	#ファイルからCookieを読み込む
	def set_cookie_by_file(self,file_name):
		cookie.load(file_name)
		self.__connection_error = self.__connection_Check()
		return self.__connection_error

	#現在セットされているCookieを取得する
	def get_set_cookie(self):
		return __cookie

	#動画を取得できるか確認
	def __connection_Check(self):
		URL = "http://nicovideo.jp/watch/" + self.__video_id
		r = re.compile("<body id=\"PAGETOP\" class=\"ja-jp\">")
		if r.search(urllib2.build_opener(urllib2.HTTPCookieProcessor(self.__cookie)).open(URL).read()) != None:
			return -1
		else:
			return 1


	'''About vide_id setting'''
	#注目する動画のvideo_idをセットする
	def set_video_id(self,video_id):
		self.__video_id = video_id

	#現在セットされているvideo_idを取得する
	def get_set_video_id(self):
		return self.__video_id


	'''About NicoAPI_token setting'''
	#NicoAPIトークンをセットする
	def set_NicoAPI_token(self):
		html = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.__cookie)).open("http://www.nicovideo.jp/my/mylist").read()
		p = html.find("NicoAPI.token")
		t,a = html[p:].split(';',1)
		self.__token = re.search('"(.*?)"', t).group(1)
	
	#現在セットされているNicoAPIトークンを取得する
	def get_set_NicoAPI_token(self):
		return self.__token


	'''About Nicovideo Operation'''
	#視聴を行う
	def view_video(self):
		try:
			urllib2.build_opener(urllib2.HTTPCookieProcessor(self.__cookie)).open("http://nicovideo.jp/watch/"+self.__video_id)
			return 1
		except:
			return -1

	#視聴履歴を全削除する
	def delete_all_view_history(self):
		page_url = "http://www.nicovideo.jp/my/history"
		post_value = {
			'mode' : 'delete',
			'video_id' : 'all',
			'token' : self.__token,
			'innerPage' : '1'
		}
		try:
			urllib2.build_opener(urllib2.HTTPCookieProcessor(self.__cookie)).open(page_url,urllib.urlencode(post_value))
			return 1
		except:
			return -1

	def delete_view_history(self,video_id):
		page_url = "http://www.nicovideo.jp/my/history"
		post_value = {
			'mode' : 'delete',
			'video_id' : video_id,
			'token' : self.__token,
			'innerPage' : '1'
		}
		try:
			urllib2.build_opener(urllib2.HTTPCookieProcessor(self.__cookie)).open(page_url,urllib.urlencode(post_value))
			return 1
		except:
			return -1

	'''About Snapshot search API'''
	#Snapshot検索APIを実行する
	def snapshot_search(self,search_query):
		try:
			end_point = "http://api.search.nicovideo.jp/api/snapshot/"
		except:
			return -1
		return requests.post(end_point,json = search_query) 

	#Snapshot検索APIの結果更新日時を取得する
	def get_last_renovation_time(self):
		return requests.get("http://api.search.nicovideo.jp/api/snapshot/version")


	'''About Download Video'''
	#動画の元ファイルのURLを取得する
	def get_original_video_url(self):
		try:
			self.view_video()
		except:
			return -1
		try:
			response = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.__cookie)).open("http://www.nicovideo.jp/api/getflv?v=" + self.__video_id).read()
		except:
			return -1
		return response.split("&")[2].replace("url=","").replace("%3A",":").replace("%2F","/").replace("%3F","?").replace("%3D","=")

	#動画データを取得する
	def get_original_video_data(self,progress = True):
		self.view_video()
		start = time.clock()
		cookies = {}
		data = []

		for cookie in self.__cookie:
			cookies[cookie.name] = cookie.value

		video_url = self.get_original_video_url()
		video_req = requests.get(video_url,cookies = cookies,stream = True)
		video_size = int(video_req.headers.get('content-length'))
		dl = 0

		if video_size is None:
			return video_req.content
		else:
			for chunk in video_req.iter_content(1024):
				dl += len(chunk)
				done = int(50 * dl / video_size)
				if progress == True:
					sys.stdout.write("\r[%s%s] %s bps" % ('=' * done, ' ' * (50-done), dl//(time.clock() - start)))
					sys.stdout.flush()
	
				data.append(chunk)
		return "".join(data)

	#動画データを保存する
	def save_video(self,file_location,progress = True):
		file_name = self.get_title().encode("utf-8")+"."+self.get_movie_type().encode("utf-8")
		file_name = file_name.replace('*','').replace('/','')
		file_name = file_location.encode("utf-8")+"\\"+file_name

		file = open(file_name.decode("utf-8"),"wb")

		file.write(self.get_original_video_data(progress))
		file.close()
		return 1


	'''About Get Video Information'''
	#動画に関するデータを取得する
	def __get_video_info(self):
		xml = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.__cookie)).open("http://ext.nicovideo.jp/api/getthumbinfo/"+self.__video_id).read()
		try:
			self.__video_info = xmltodict.parse(xml)["nicovideo_thumb_response"]["thumb"]
		except:
			return -1
		
		return self.__video_info

	def get_title(self):
		if self.get_set_video_id() != self.__video_info["video_id"]:
			if self.__get_video_info() == -1:
				return -1
			return self.__video_info["title"]
		return self.__video_info["title"]

	def get_description(self):
		if self.get_set_video_id() != self.__video_info["video_id"]:
			if self.__get_video_info() == -1:
				return -1
			return self.__video_info["description"]
		return self.__video_info["description"]		

	def get_thumbnail_url(self):
		if self.get_set_video_id() != self.__video_info["video_id"]:
			if self.__get_video_info() == -1:
				return -1
			return self.__video_info["thumbnail_url"]
		return self.__video_info["thumbnail_url"]	

	def get_first_retrieve(self):
		if self.get_set_video_id() != self.__video_info["video_id"]:
			if self.__get_video_info() == -1:
				return -1
			return self.__video_info["first_retrieve"]
		return self.__video_info["first_retrieve"]	

	def get_length(self):
		if self.get_set_video_id() != self.__video_info["video_id"]:
			if self.__get_video_info() == -1:
				return -1
			return self.__video_info["length"]
		return self.__video_info["length"]	

	def get_movie_type(self):
		if self.get_set_video_id() != self.__video_info["video_id"]:
			if self.__get_video_info() == -1:
				return -1
			return self.__video_info["movie_type"]
		return self.__video_info["movie_type"]	

	def get_size_high(self):
		if self.get_set_video_id() != self.__video_info["video_id"]:
			if self.__get_video_info() == -1:
				return -1
			return self.__video_info["size_high"]
		return self.__video_info["size_high"]

	def get_size_low(self):
		if self.get_set_video_id() != self.__video_info["video_id"]:
			if self.__get_video_info() == -1:
				return -1
			return self.__video_info["size_low"]
		return self.__video_info["size_low"]	

	def get_view_counter(self):
		if self.get_set_video_id() != self.__video_info["video_id"]:
			if self.__get_video_info() == -1:
				return -1
			return self.__video_info["view_counter"]
		return self.__video_info["view_counter"]	

	def get_comment_num(self):
		if self.get_set_video_id() != self.__video_info["video_id"]:
			if self.__get_video_info() == -1:
				return -1
			return self.__video_info["comment_num"]
		return self.__video_info["comment_num"]	

	def get_mylist_counter(self):
		if self.get_set_video_id() != self.__video_info["video_id"]:
			if self.__get_video_info() == -1:
				return -1
			return self.__video_info["mylist_counter"]
		return self.__video_info["mylist_counter"]	

	def get_last_res_body(self):
		if self.get_set_video_id() != self.__video_info["video_id"]:
			if self.__get_video_info() == -1:
				return -1
			return self.__video_info["last_res_body"]
		return self.__video_info["last_res_body"]	

	def get_thumb_type(self):
		if self.get_set_video_id() != self.__video_info["video_id"]:
			if self.__get_video_info() == -1:
				return -1
			return self.__video_info["thumb_type"]
		return self.__video_info["thumb_type"]	

	def get_embeddable(self):
		if self.get_set_video_id() != self.__video_info["video_id"]:
			if self.__get_video_info() == -1:
				return -1
			return self.__video_info["embeddable"]
		return self.__video_info["embeddable"]	

	def get_no_live_play(self):
		if self.get_set_video_id() != self.__video_info["video_id"]:
			if self.__get_video_info() == -1:
				return -1
			return self.__video_info["no_live_play"]
		return self.__video_info["no_live_play"]	

	def get_tags(self):
		if self.get_set_video_id() != self.__video_info["video_id"]:
			if self.__get_video_info() == -1:
				return -1
			return self.__video_info["tags"]
		return self.__video_info["tags"]	

	def get_user_id(self):
		if self.get_set_video_id() != self.__video_info["video_id"]:
			if self.__get_video_info() == -1:
				return -1
			return self.__video_info["user_id"]
		return self.__video_info["user_id"]		

	def get_user_nickname(self):
		if self.get_set_video_id() != self.__video_info["video_id"]:
			if self.__get_video_info() == -1:
				return -1
			return self.__video_info["user_nickname"]
		return self.__video_info["user_nickname"]	

	def get_user_icon_url(self):
		if self.get_set_video_id() != self.__video_info["video_id"]:
			if self.__get_video_info() == -1:
				return -1
			return self.__video_info["user_icon_url"]
		return self.__video_info["user_icon_url"]


	'''About Comment Information'''
	#動画内のコメント情報を取得する
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

	def get_comments(self,res_from = 10):
		comment_info = self.get_comment_information(res_from)
		if comment_info == -1:
			return -1
		comments = []

		for comment in comment_info["chat"]:
			comments.append(comment["#text"])
		return comments