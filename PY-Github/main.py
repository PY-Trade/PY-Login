#!/usr/bin/python3
#coding=utf-8
############################################################
#
# Let's PY Github o(*≧▽≦)ツ
#
############################################################
import os,sys
if not sys.version_info[0] == 3:
	print("error: only support python3.x.")
	sys.exit()
import api
import json
import collections
import random
client = api.Client()

FUNCTIONS = collections.OrderedDict()
FUNCTIONS["STAR"] = "auto star"
FUNCTIONS["UNSTAR"] = "auto unstar"

def main():
	config_path = os.path.join(client.root_path, 'config.json')
	try:
		f = open(config_path, 'r')
		config = json.load(f)
	except Exception as e:
		print("read config.json fail.", e)
		sys.exit()
	finally:
		f.close()

	random.shuffle(config)
	
	# 选择功能
	print("-------------please enter function-----------")
	prompt_info = ""
	for index, key in enumerate(FUNCTIONS):
		prompt_info += str(index) + ". " + key + "\t\t"
	print(prompt_info)

	selectKey = None
	while True:
		try:
			select = int(input("input your select:").strip())
			if select < 0 or select > len(FUNCTIONS):
				raise
			selectKey = list(FUNCTIONS.keys())[select]
		except Exception as e:
			print("input error")
			continue
		break

	# 运行
	if FUNCTIONS[selectKey] == FUNCTIONS["STAR"]:
		print("please enter your repo address,such as 'https://github.com/yourname/yourreponame'")
		repo_url = input().strip()
		for user in config:
			if login(user):
				client.star(repo_url)

	elif FUNCTIONS[selectKey] == FUNCTIONS["UNSTAR"]:
		print("please enter your repo address,such as 'https://github.com/yourname/yourreponame'")
		repo_url = input().strip()
		for user in config:
			if login(user):
				client.unstar(repo_url)
	

def login(userdata):
	if "username" in userdata and "password" in userdata:
		username = userdata['username']
		password = userdata['password']
		if username == "" or password == "":
			print("error: please 'username' or 'password' in config.json")
			return False
		print(">>>>>>>>>>>> ", username, " <<<<<<<<<<<")
		if client.cookies_login(username) or client.login(username, password):
			return True
		else:
			return False
	else:
		print("error: please 'username' or 'password' in config.json")
		return False

if __name__ == '__main__':
	main()

