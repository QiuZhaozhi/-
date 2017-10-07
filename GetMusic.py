#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import urllib.request
import urllib.error
import re
import urllib.parse
import time
import datetime
import base64
import os

site = 'https://music.liuli.lol/list'
m_regex = '/music/'
chk_box = 'on'

LOG = 1

def download(url, num_retries = 2, user_agent = 'GetMuisc', music_list = None):
	print ('正在下载网页：', url)
	headers = {'User-agent': user_agent}
	if music_list:
		data = {'listId': music_list, 'h': chk_box}
		en_data = urllib.parse.urlencode(data).encode('utf-8')
		request = urllib.request.Request(url, en_data, headers = headers)	
		#用GerMusic用户请求url页面，并传递music_list参数
	else:
		request = urllib.request.Request(url, headers = headers)
	try:
		html = urllib.request.urlopen(request).read()
	except urllib.error.URLError as e:
		print ('网页下载错误，错误码：', e.reason)
		html = None
		if num_retries > 0:
			if hasattr(e, 'code') and 500 <= e.code < 600:
				return download(url, num_retries - 1)
			else:
				print("下载失败")
	return html

def Get_Music(music_list, seed_url = site, m_regex = m_regex, max_depth = 2, delay = 10):
	max_depth = 2
	crawl_queue = [seed_url]
	seen = set(crawl_queue)
	throttle = Throttle(delay)
	while crawl_queue:
		url = crawl_queue.pop()
		throttle.wait(url)
		if site == url:
			html = download(url = url, music_list = music_list).decode('utf-8')
			music_link =re.findall('<a[^>]+href=["\'](.*/music/.*?)["\']', html, re.I)
			if LOG:
				print("已传入歌单，正在解析网页...")
		else:
			html = download(url = url).decode('utf-8')
		if re.search(m_regex, url, re.I):
			DownMusic(html)
		for link in music_link:
			link = urllib.parse.urljoin(seed_url, link)
			if link not in seen:
				seen.add(link)
				crawl_queue.append(link)
	print("所有歌曲已下载完毕")

def DownMusic(html):
	down_music_link = re.search('<a[^>]+href=["\'](\S+\.mp3?)["\']', html, re.I).group(1)
	if LOG:
		print("正在获取歌曲下载链接...")
	#获取歌曲下载链接
	music_name = re.search('download=\"(.*)\.mp3\"', html, re.I).group(1)
	if LOG:
		print("正在获取歌曲名...")
	#获取歌曲名字
	music_artist = re.search('<p>(\S+)</p>', html, re.I).group(1)
	if LOG:
		print("正在获取作曲家...")
	#获取歌曲作者
	try:
		urllib.request.urlretrieve(down_music_link, music_artist+'-'+music_name+'.mp3')
	except urllib.error.URLError as e:
		if e.code:
			print("下载失败，不存在该文件：", music_artist+'-'+music_name+'.mp3')
			return 1
	print("已下载：", music_artist+'-'+music_name+'.mp3')
	#以$艺术家-$歌名.mp3的形式将文件存入本地


class Throttle:
	def __init__(self, delay):
		self.delay = delay
		self.domains = {}

	def wait(self, url):
		domain = urllib.parse.urlparse(url).netloc
		last_accessed = self.domains.get(domain)

		if self.delay >0 and last_accessed is not None:
			sleep_secs = self.delay - (datetime.datetime.now() - last_accessed).seconds

			if sleep_secs > 0:
				time.sleep(sleep_secs)

		self.domains[domain] = datetime.datetime.now()
