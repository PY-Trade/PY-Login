#!/usr/bin/python3
#coding=utf-8
############################################################
#
#	coding api
#
############################################################
import os,sys
import requests
import requests.utils
import pickle
import json
import hashlib
from bs4 import BeautifulSoup

headers = {
	'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
	'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
}

class Client():
	def __init__(self):
		self.session = requests.Session()
		self.session.headers = headers
		self.root_path = os.path.dirname(os.path.realpath(sys.argv[0]))
		self.user_name = None
		self.points_left = 0

	def post(self, url, data):
		response = self.session.post(url, data=data)
		if response.status_code == 200:
			self.session.headers['Referer'] = response.url
		return response

	def get(self, url):
		response = self.session.get(url)
		if response.status_code == 200:
			self.session.headers['Referer'] = response.url
		return response

	def load_cookies(self, path):
		with open(path, 'rb') as f:
			self.session.cookies = requests.utils.cookiejar_from_dict(pickle.load(f))

	def save_cookies(self, path):
		with open(path, 'wb') as f:
			cookies_dic = requests.utils.dict_from_cookiejar(self.session.cookies)
			pickle.dump(cookies_dic, f)

	#获取个人信息
	def check_login(self):
		response = self.get('https://coding.net/api/account/current_user')
		data = json.loads(response.text)
		try:
			if data['code'] == 0:
				self.user_name = data['data']['global_key']
				self.points_left = data['data']['points_left']
				return True
			raise
		except Exception as e:
			return False

	# 普通登录
	def login(self, username, password):
		response = self.get('https://coding.net/api/captcha/login')
		password = hashlib.sha1(password.encode('utf-8')).hexdigest()
		preload = {
			'email': username,
			'password': password,
			'remember_me': True,
		}
		response = self.post('https://coding.net/api/login', data=preload)
		try:
			data = json.loads(response.text)
			if data['code'] == 0:
				print('login success')
				self.user_name = data['data']['global_key']
				self.points_left = data['data']['points_left']
				cookies_file = os.path.join(self.root_path, username + ".cookies")
				self.save_cookies(cookies_file)
				return True
			elif 'msg' in data :
				raise Exception(data['msg'])
			raise Exception("unknow error")
		except Exception as e:
			print("login fail", e)
			return False
			
	#使用cookies登陆
	def cookies_login(self, username):
		cookies_file = os.path.join(self.root_path, username + ".cookies")
		if not os.path.exists(cookies_file):
			print("cookies login fail: " + username + '.cookies not exists.')
			return False
		self.load_cookies(cookies_file)
		if not self.check_login():
			print("cookies login fail: " + username + '.cookies expire')
			return False
		print("cookies login success")
		return True