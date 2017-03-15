#!/usr/bin/python3
#coding=utf-8
############################################################
#
# Let's PY Bilibili - ( ゜- ゜)つロ 乾杯~
#
############################################################
import os,sys
if not sys.version_info[0] == 3:
	print("error: only support python3.x.")
	sys.exit()
import api
import json
import collections

client = api.Client()

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

	# 暂无扩展功能，只有登录
	for user in config:
		if login(user):
			pass
	

def login(userdata):
	if "username" in userdata and "password" in userdata:
		username = userdata['username']
		password = userdata['password']
		if username == "" or password == "":
			print("error: please 'username' or 'password' in config.json")
			return False
		print(">>>>>>>>>>>> ", username, " <<<<<<<<<<<")
		if client.cookies_login(username) or client.login(username, password):
			print("welcome", client.user_name)
			return True
		else:
			return False
	else:
		print("error: please 'username' or 'password' in config.json")
		return False

if __name__ == '__main__':
	main()

