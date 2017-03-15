#!/usr/bin/python3
#coding=utf-8
############################################################
#
#	bilibili api
#
############################################################
import os,sys
import requests
import requests.utils
import pickle
import rsa
import binascii
import json
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

	#密码执行加密
	def _encrypt(self, password):
		#获取加密的token
		response = self.get('http://passport.bilibili.com/login?act=getkey')
		token = json.loads(response.content.decode('utf-8'))
		password = str(token['hash'] + password).encode('utf-8')
		pub_key = token['key']
		pub_key = rsa.PublicKey.load_pkcs1_openssl_pem(pub_key)
		message = rsa.encrypt(password, pub_key)
		message = binascii.b2a_base64(message)
		return message

	#获取个人信息
	def check_login(self):
		response = self.get('https://account.bilibili.com/home/userInfo')
		data = json.loads(response.content.decode('utf-8'))
		try:
			if data['status'] == True:
				self.user_name = data['data']['uname']
				return True
		except Exception as e:
			print(e)
		return False

	# 普通登录
	def login(self, username, password):
		#密码加密
		password = self._encrypt(password)
		preload = {
			'userid': username,
			'pwd': password,
			'captcha':"",
			'keep':1
		}
		response = self.post('https://passport.bilibili.com/ajax/miniLogin/login', data=preload)
		data = json.loads(response.content.decode('utf-8'))
		try:
			data = data['status']
			if data == False:
				raise
			cookies_file = os.path.join(self.root_path, username + ".cookies")
			self.save_cookies(cookies_file)
			print('login success')
			return True
		except Exception as e:
			#登陆失败
			print('login fail')
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