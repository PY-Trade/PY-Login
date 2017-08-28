#!/usr/bin/python3
#coding=utf-8
############################################################
#
#	github api
#
############################################################
import os,sys
import requests
import requests.utils
import pickle

headers = {
    'Pragma': 'no-cache',
    'Origin': 'http://account.youdao.com',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.6,en;q=0.4',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'DNT': '1',
}

class Client():
	def __init__(self):
		self._clear()
		self.root_path = os.path.dirname(os.path.realpath(sys.argv[0]))

	def _clear(self):
		self.session = requests.Session()
		self.session.headers = headers

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

	# 校验是否处于登录状态
	def check_login(self):
		response = self.get('http://dict.youdao.com/wordbook/wordlist')
		if response.status_code == 200:
			return True
		else:
			return False

	# 普通登录
	def login(self, username, password):
		self._clear()
		preload = {
		  'app': 'web',
		  'tp': 'urstoken',
		  'cf': '3',
		  'fr': '1',
		  'ru': 'http://dict.youdao.com/wordbook/wordlist?keyfrom=login_from_dict2.index',
		  'product': 'DICT',
		  'type': '1',
		  'um': 'true',
		  'username': username,
		  'password': password,
		}
		response = self.post('https://logindict.youdao.com/login/acc/login', data=preload)
		if response.status_code == 200 and len(response.history) > 0:
			cookies_file = os.path.join(self.root_path, username + ".cookies")
			self.save_cookies(cookies_file)
			print("login success.")
			return True
		else:
			print("login fail.")
			return False
			
	# 使用cookies登陆
	def cookies_login(self, username):
		self._clear()
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

	# 添加单词
	def add(self, word):
		response = self.get('http://dict.youdao.com/wordbook/ajax?action=addword&q={}'.format(word))
		if response.text == "{\"message\":\"adddone\"}":
			print("'{}' add success".format(word))