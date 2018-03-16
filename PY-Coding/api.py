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

class MergeRequest(object):
	DEFAULT_TITLE = 'Merge Request'
	DEFAULT_CONTENT = ''

	def __init__(self, src_branch, dst_branch):
		self.src_branch = src_branch
		self.dst_branch = dst_branch
		self.title = MergeRequest.DEFAULT_TITLE
		self.content = MergeRequest.DEFAULT_CONTENT

class Client():
	def __init__(self):
		self._clear()
		self.root_path = os.path.dirname(os.path.realpath(sys.argv[0]))

	def _clear(self):
		self.session = requests.Session()
		self.session.headers = headers
		self.user_name = None
		self.points_left = 0
		self.id = None

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

	def delete(self, url):
		response = self.session.delete(url)
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
				self.id = data['data']['id']
				return True
			raise
		except Exception as e:
			return False

	# 普通登录
	def login(self, username, password):
		self._clear()
		# response = self.get('https://coding.net/api/captcha/login')
		password = hashlib.sha1(password.encode('utf-8')).hexdigest()
		preload = {
			'account': username,
			'password': password,
			'remember_me': True,
		}
		response = self.post('https://coding.net/api/v2/account/login', data=preload)
		try:
			data = json.loads(response.text)
			if data['code'] == 0:
				print('login success')
				self.user_name = data['data']['global_key']
				self.points_left = data['data']['points_left']
				self.id = data['data']['id']
				cookies_file = os.path.join(self.root_path, username + ".cookies")
				self.save_cookies(cookies_file)
				print('save success')
				return True
			elif 'msg' in data :
				raise Exception(data['msg'])
			raise Exception("unknow error")
		except Exception as e:
			print("login fail", e)
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

	def create_task(self, project, content):
		payload = {
			'content': content,
			'owner_id': self.id,
		}
		response = self.post('https://coding.net/api/user/{}/project/{}/task'.format(self.user_name, project), data=payload)
		# print("create_task", response.text)
		try:
			data = json.loads(response.text)
			if data['code'] == 0:
				return data['data']['id']
			else:
				raise Exception(data['msg'])
		except Exception as e:
			print("create_task fail", e)
			return False

	def delete_task(self, project, task_id):
		response = self.delete('https://coding.net/api/user/{}/project/{}/task/{}'.format(self.user_name, project, task_id))
		# print("delete_task", response.text)
		try:
			data = json.loads(response.text)
			if data['code'] == 0:
				return True
			else:
				raise Exception(data['msg'])
		except Exception as e:
			print("delete_task fail", e)
			return False

	def create_merge_request(self, project, request):
		payload = {
			'srcBranch': request.src_branch,
			'desBranch': request.dst_branch,
			'title': request.title,
			'content': request.content,
		}
		response = self.post('https://coding.net/api/user/{}/project/{}/git/merge'.format(self.user_name, project), data=payload)
		# print("create_merge_request", response.text)
		try:
			data = json.loads(response.text)
			if data['code'] == 0:
				return data['data']['merge_request']['iid']
			else:
				raise Exception(data['msg'])
		except Exception as e:
			print("create_merge_request fail", e)
			return False

	def delete_merge_request(self, project, mr_id):
		response = self.post('https://coding.net/api/user/{}/project/{}/git/merge/{}/cancel'.format(self.user_name, project, mr_id), data=None)
		# print("delete_merge_request", response.text)
		try:
			data = json.loads(response.text)
			if data['code'] == 0:
				return True
			else:
				raise Exception(data['msg'])
		except Exception as e:
			print("delete_merge_request fail", e)
			return False

	def create_push_request(self, project, branch, content):
		response = self.get('https://coding.net/api/user/{}/project/{}/git/edit/{}%252FREADME.md'.format(self.user_name, project, branch))
		# print("create_push_request", response.text)
		lastCommitSha = ""
		try:
			data = json.loads(response.text)
			if data['code'] == 0:
				lastCommitSha = data['data']['lastCommit']
			else:
				raise Exception(data['msg'])
		except Exception as e:
			print("create_push_request fail", e)
			return False

		payload = {
			'content': content,
			'message': 'DailyPush',
			'lastCommitSha': lastCommitSha,
		}

		response = self.post('https://coding.net/api/user/{}/project/{}/git/edit/{}%252FREADME.md'.format(self.user_name, project, branch), data=payload)
		# print("create_push_request", response.text)
		try:
			data = json.loads(response.text)
			if data['code'] == 0:
				return True
			else:
				raise Exception(data['msg'])
		except Exception as e:
			print("create_push_request fail", e)
			return False

	def create_project_request(self, project):
		payload = {
			'type': 2,
			'gitEnabled': 'true',
			'gitReadmeEnabled': 'true',
			'gitIgnore': 'no',
			'gitLicense': 'no',
			'vcsType': 'git',
			'name': project,
			'importFrom': '',
			'members': '',
		}
		response = self.post('https://coding.net/api/project', data=payload)
		# print("create_project_request", response.text)
		try:
			data = json.loads(response.text)
			if data['code'] == 0:
				return True
			else:
				raise Exception(data['msg'])
		except Exception as e:
			print("create_project_request fail", e)
			return False

	def create_branch_request(self, project, branch):
		payload = {
			'branch_name': branch,
		}
		response = self.post('https://coding.net/api/user/{}/project/{}/git/branches/create'.format(self.user_name, project), data=payload)
		# print("create_branch_request", response.text)
		try:
			data = json.loads(response.text)
			if data['code'] == 0:
				return True
			else:
				raise Exception(data['msg'])
		except Exception as e:
			print("create_branch_request fail", e)
			return False
