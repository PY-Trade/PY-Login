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
from bs4 import BeautifulSoup

headers = {
    'Pragma': 'no-cache',
    'Origin': 'https://github.com',
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
		response = self.get('https://github.com/login')
		if response.status_code == 200 and len(response.history) > 0:
			return True
		else:
			return False

	# 普通登录
	def login(self, username, password):
		self._clear()
		# 访问登陆页面
		response = self.get('https://github.com/login')
		# 截取token
		soup = BeautifulSoup(response.text, "html.parser")
		token = soup.find_all("input", attrs={"name": "authenticity_token"})[0]["value"]
		# 请求登陆
		preload = {
			'utf8': '✓',
			'authenticity_token': token,
			'login': username,
			'password': password
		}
		response = self.post('https://github.com/session', data=preload)
		if response.status_code == 200 and len(response.history) > 0:
			cookies_file = os.path.join(self.root_path, username + ".cookies")
			self.save_cookies(cookies_file)
			print("login success.")
			return True
		else:
			print("login fail.")
			return False
			
	#使用cookies登陆
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

	def _getTokenAndId(self, repo_url):
		response = self.get(repo_url)
		soup = BeautifulSoup(response.text, "html.parser")
		tokens = soup.find_all("input", attrs={"name": "authenticity_token"})
		repo_ids = soup.find_all("input", attrs={"name": "repository_global_id"})
		token = tokens[0]["value"] if len(tokens) > 0 else None
		repo_id = repo_ids[0]["value"] if len(repo_ids) > 0 else None
		return token,repo_id

	# star一个项目
	def star(self, repo_url):
		token = self._getTokenAndId(repo_url)[0]
		preload = {
			'utf8': '✓',
			'authenticity_token': token
		}
		response = self.post(repo_url + '/star', data=preload)
		if response.status_code == 200 and len(response.history) > 0:
			print(repo_url, "star success")
			return True
		else:
			print(repo_url, "star fail")
			return False

	# unstar一个项目
	def unstar(self, repo_url):
		token = self._getTokenAndId(repo_url)[0]
		preload = {
			'utf8': '✓',
			'authenticity_token': token
		}
		response = self.post(repo_url + '/unstar', data=preload)
		if response.status_code == 200 and len(response.history) > 0:
			print(repo_url, "unstar success")
			return True
		else:
			print(repo_url, "unstar fail")
			return False