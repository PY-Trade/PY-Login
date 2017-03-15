## PY-Login
### 简介
模拟登录各类网站，操作api完成各种不可描述的事情  

### 使用
* 打开各个功能目录下的config.json文件
* 填入账号密码，请保证json格式正确（如下），多个账号会依次登录并完成功能
```json
[
  {
    "username": "",
    "password": ""
  },
  {
    "username": "",
    "password": ""
  }
]
```

### 支持列表

| 网站     |  模拟登录    |   功能列表   |
| ---- | ---- | ---- |
|   github.com   |  ✓    |    star \ unstar  |
|   bilibili.com   |  ✓    |    -  |
|   coding.net   |  ✓    |    -  |

### PR说明
* 新网站的PR需保证登录和cookies登录功能完成
* 请保证新目录及文件命名的统一
* 请保证用户填写的config.json格式统一
* API的PR优先批量点赞、回复、顶、硬币、香蕉、肥皂等攒人气的API