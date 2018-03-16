#!/usr/bin/python3
#coding=utf-8
############################################################
#
# Let's PY Coding (╯‵□′)╯︵┻━┻
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
import time

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

	random.shuffle(config)
	
	# 暂无扩展功能，只有登录
	for user in config:
		if login(user):
			# 自动创建的项目名
			project = 'mission-p'
			# 自动创建的分支名
			branch = 'auto-merge'
			# 格式化时间
			now_timestr = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()));
			#获取当前时间
			now = time.localtime(int(time.time()))
			year = now.tm_year
			month = now.tm_mon
			day = now.tm_mday

			#尝试创建项目（必要）
			if client.create_project_request(project):
				print('首次运行，创建项目: "{}" 成功'.format(project))

			#尝试创建分支（必要）
			if client.create_branch_request(project,branch):
				print('首次运行，创建分支: "{}" 成功'.format(branch))
				if client.create_push_request(project,branch,now_timestr):
					print('首次运行，差异化分支使之可合并操作完成')

			#推送代码
			if client.create_push_request(project,branch, now_timestr):
				print('推送代码: "{}" 成功'.format(now_timestr))

			#创建任务
			task_id = client.create_task(project, now_timestr)
			if task_id:
				print('任务: "{}" 操作成功'.format(task_id))
				if client.delete_task(project, task_id):
					print('任务: "{}" 删除成功'.format(task_id))

			#创建合并请求
			mr = api.MergeRequest(branch, 'master')
			mr.title = now_timestr
			mr_id = client.create_merge_request(project, mr)
			if mr_id:
				print('合并请求: "{}" 创建成功'.format(mr_id))
				if client.delete_merge_request(project, mr_id):
					print('合并请求: "{}" 删除成功'.format(mr_id))
	

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
			print("your points left", client.points_left)
			return True
		else:
			return False
	else:
		print("error: please 'username' or 'password' in config.json")
		return False

if __name__ == '__main__':
	main()

