import json, requests, re, html2text, time, sys

WECHAT_AUTH_STATE = './wechat_auth_state.json'

def get_cookies_from_state():
    with open(WECHAT_AUTH_STATE, 'r', encoding='utf-8') as f:
        state = json.load(f)
    cookies = {}
    for c in state['cookies']:
        cookies[c['name']] = c['value']
    return cookies

def get_token_via_request(cookies):
    r = requests.get('https://mp.weixin.qq.com/', cookies=cookies, timeout=10)
    m = re.search(r'token=(\d+)', r.url)
    return m.group(1) if m else None

def search_fakeid(token, name, cookies):
    url = f"https://mp.weixin.qq.com/cgi-bin/searchbiz?action=search_biz&token={token}&lang=zh_CN&f=json&query={requests.utils.quote(name)}&begin=0&count=5"
    r = requests.get(url, cookies=cookies, timeout=10)
    if r.status_code == 200:
        for biz in r.json().get('list', []):
            if biz.get('nickname') == name:
                return biz.get('fakeid')
    return None

def get_articles(token, fakeid, cookies):
    url = f"https://mp.weixin.qq.com/cgi-bin/appmsg?action=list_ex&begin=0&count=5&fakeid={fakeid}&type=9&query=&token={token}&lang=zh_CN&f=json"
    r = requests.get(url, cookies=cookies, timeout=10)
    if r.status_code == 200:
        return r.json().get('app_msg_list', [])
    return []

def fetch_article(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'
    }
    r = requests.get(url, headers=headers, timeout=15)
    r.encoding = 'utf-8'
    m = re.search(r'<div id="js_content".*?</div>', r.text, re.DOTALL)
    html = m.group(0) if m else r.text
    h = html2text.HTML2Text()
    h.bypass_tables = False; h.ignore_links = False; h.ignore_images = False; h.body_width = 0
    return h.handle(html)

if __name__ == '__main__':
    print("="*50)
    print("微信公众号监控 - 极速测试脚本")
    print("="*50)

    name = sys.argv[1] if len(sys.argv) > 1 else "MDL科研助手"
    print(f"测试公众号: {name}")

    t0 = time.time()
    
    cookies = get_cookies_from_state()
    print(f"[1/4] 加载Cookie... ({time.time()-t0:.2f}s)")

    token = get_token_via_request(cookies)
    if not token:
        print("❌ 获取token失败")
        exit(1)
    print(f"[2/4] 获取token: {token[:10]}... ({time.time()-t0:.2f}s)")

    fakeid = search_fakeid(token, name, cookies)
    if not fakeid:
        print(f"❌ 未找到公众号「{name}」")
        exit(1)
    print(f"[3/4] 获取fakeid: {fakeid} ({time.time()-t0:.2f}s)")

    articles = get_articles(token, fakeid, cookies)
    print(f"[4/4] 获取文章列表: {len(articles)} 篇 ({time.time()-t0:.2f}s)")

    for a in articles:
        print(f"   - {a['title']}")

    print(f"\n✅ 全部完成! 总耗时: {time.time()-t0:.2f}s")
    
    if articles:
        print("\n[测试] 抓取第一篇文章...")
        try:
            content = fetch_article(articles[0]['link'])
            print(f"✅ 成功! 内容长度: {len(content)}")
        except Exception as e:
            print(f"❌ 失败: {e}")