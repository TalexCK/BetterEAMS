#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
上海科技大学 EAMS 教务系统课程数据独立抓取脚本
"""

import os
import sys
import json
import time
import requests
import urllib3
from bs4 import BeautifulSoup

# 忽略 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 配置项
UNDERGRAD_JSON = 'undergrad_courses.json'
GRAD_JSON = 'grad_courses.json'
SSO_COOKIE_FILE = 'sso_cookie.txt'
REQUEST_TIMEOUT = 15

def load_cookies(filepath):
    """
    加载 Cookie 凭证，支持两种格式：
    1. 浏览器 F12 控制台 copy(document.cookie) 导出的原始 Key-Value 字符串 (e.g. JSESSIONID=xxx; casp-portal=yyy)
    2. 浏览器插件导出的 Netscape HTTP Cookie 格式 (tab分隔)
    """
    if not os.path.exists(filepath):
        return None
        
    cookies = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read().strip()
        
    if not content:
        return None

    # 判断是否为 Netscape 格式
    if content.startswith('#') or '\t' in content:
        for line in content.splitlines():
            if line.startswith('#') or not line.strip():
                continue
            parts = line.split('\t')
            if len(parts) >= 7:
                name = parts[5].strip()
                value = parts[6].strip()
                cookies[name] = value
    else:
        # 解析标准 key=value; 键值对
        for part in content.split(';'):
            part = part.strip()
            if '=' in part:
                k, v = part.split('=', 1)
                cookies[k.strip()] = v.strip()
                
    return cookies if cookies else None

def download_undergrad_courses():
    """
    下载本科生课程（公开免登录接口）
    """
    print("==================================================")
    print("1. 开始下载本科生课程...")
    print("==================================================")
    
    url = 'https://eams.shanghaitech.edu.cn/eams/courseSearchOther!search.action'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    courses = []
    page_no = 1
    page_size = 500
    
    while True:
        print(f"  正在拉取第 {page_no} 页...")
        data = {
            'pageNo': str(page_no),
            'pageSize': str(page_size)
        }
        try:
            r = requests.post(url, data=data, headers=headers, verify=False, timeout=REQUEST_TIMEOUT)
            if r.status_code != 200:
                print(f"  [Error] HTTP 状态码异常: {r.status_code}")
                break
                
            soup = BeautifulSoup(r.text, 'html.parser')
            rows = soup.find_all('tr')
            if len(rows) <= 1:
                print("  已到达尾页。")
                break
                
            page_count = 0
            for row in rows[1:]:
                tds = [td.get_text(strip=True) for td in row.find_all('td')]
                if len(tds) >= 10:
                    code = tds[1]
                    name = tds[2]
                    credits = tds[5]
                    try:
                        credits_val = float(credits)
                    except ValueError:
                        credits_val = 0.0
                    courses.append({
                        'code': code,
                        'name': name,
                        'credits': credits_val
                    })
                    page_count += 1
            
            print(f"    成功解析出 {page_count} 门课程")
            if page_count < page_size:
                print("  抓取完毕。")
                break
                
            page_no += 1
            time.sleep(0.5)
        except Exception as e:
            print(f"  [Error] 抓取本科课程异常: {e}")
            break
            
    if courses:
        with open(UNDERGRAD_JSON, 'w', encoding='utf-8') as f:
            json.dump(courses, f, ensure_ascii=False, indent=2)
        print(f"🎉 成功保存 {len(courses)} 门本科课程到 {UNDERGRAD_JSON}")
    else:
        print("❌ 未能获取到任何本科课程，请检查网络连接或接口地址是否变更。")

def download_grad_courses():
    """
    下载研究生课程（需要 SSO Cookie）
    """
    print("\n==================================================")
    print("2. 开始下载研究生及本研一体化课程...")
    print("==================================================")
    
    cookies = load_cookies(SSO_COOKIE_FILE)
    if not cookies:
        print(f"⚠️  警告: 未在当前目录找到 '{SSO_COOKIE_FILE}' 或其内容为空。")
        print("   研究生课程由于受登录保护，将被跳过更新。")
        print("   如需抓取研究生课程，请按照以下指引操作：")
        print("   1. 在浏览器登录教务系统 (EAMS)；")
        print("   2. 控制台输入 copy(document.cookie) 并回车；")
        print("   3. 将剪贴板内容保存到该目录下的 'sso_cookie.txt' 中，然后重新运行本脚本。")
        return
        
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    })
    
    # 注入解析出的 Cookie
    for name, value in cookies.items():
        session.cookies.set(name, value, domain='eams.shanghaitech.edu.cn')
        
    url = 'https://eams.shanghaitech.edu.cn/eams/postLesson!search.action'
    
    try:
        # 预测试会话有效性
        r = session.get(url, allow_redirects=True, verify=False, timeout=REQUEST_TIMEOUT)
        if "postLesson" not in r.url or r.status_code != 200:
            print("❌ 错误: 会话凭证已过期或无效。请重新抓取最新 Cookie 填入 sso_cookie.txt。")
            return
            
        print("🔑 SSO Cookie 会话验证通过，开始下载...")
        
        courses = []
        page_no = 1
        page_size = 500
        
        while True:
            print(f"  正在拉取第 {page_no} 页...")
            data = {
                'pageNo': str(page_no),
                'pageSize': str(page_size)
            }
            r_post = session.post(url, data=data, headers={'X-Requested-With': 'XMLHttpRequest'}, verify=False, timeout=REQUEST_TIMEOUT)
            if r_post.status_code != 200:
                print(f"  [Error] HTTP 状态码异常: {r_post.status_code}")
                break
                
            soup = BeautifulSoup(r_post.text, 'html.parser')
            rows = soup.find_all('tr')
            if len(rows) <= 1:
                print("  已到达尾页。")
                break
                
            page_count = 0
            for row in rows[1:]:
                tds = [td.get_text(strip=True) for td in row.find_all('td')]
                if len(tds) >= 10:
                    code = tds[1]
                    name = tds[2]
                    credits = tds[5]
                    try:
                        credits_val = float(credits)
                    except ValueError:
                        credits_val = 0.0
                    courses.append({
                        'code': code,
                        'name': name,
                        'credits': credits_val
                    })
                    page_count += 1
                    
            print(f"    成功解析出 {page_count} 门课程")
            if page_count < page_size:
                print("  抓取完毕。")
                break
                
            page_no += 1
            time.sleep(0.5)
            
        if courses:
            with open(GRAD_JSON, 'w', encoding='utf-8') as f:
                json.dump(courses, f, ensure_ascii=False, indent=2)
            print(f"🎉 成功保存 {len(courses)} 门研究生及本研一体课程到 {GRAD_JSON}")
        else:
            print("❌ 未能成功解析出任何研究生课程数据。")
            
    except Exception as e:
        print(f"❌ 运行异常: {e}")

if __name__ == '__main__':
    download_undergrad_courses()
    download_grad_courses()
    print("\n任务结束。可以直接打开 index.html 看板查阅。")
