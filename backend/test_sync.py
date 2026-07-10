import os, re, requests, datetime, html2text

WECHAT_AUTH_STATE = './wechat_auth_state.json'

def get_token():
    print("[1] 获取微信token...")
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=WECHAT_AUTH_STATE)
        page = context.new_page()
        page.goto("https://mp.weixin.qq.com/")
        page.wait_for_load_state("networkidle")
        m = re.search(r'token=(\d+)', page.url)
        browser.close()
        return m.group(1) if m else None

def search_fakeid(token, name):
    print(f"[2] 搜索公众号「{name}」...")
    from playwright.sync_api import sync_playwright
    import urllib.parse
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=WECHAT_AUTH_STATE)
        page = context.new_page()
        page.goto("https://mp.weixin.qq.com/")
        page.wait_for_load_state("networkidle")
        url = f"https://mp.weixin.qq.com/cgi-bin/searchbiz?action=search_biz&token={token}&lang=zh_CN&f=json&query={urllib.parse.quote(name)}&begin=0&count=5"
        r = page.request.get(url)
        browser.close()
        if r.status == 200:
            for biz in r.json().get('list', []):
                if biz.get('nickname') == name:
                    return biz.get('fakeid')
    return None

def get_articles(token, fakeid):
    print(f"[3] 获取文章列表...")
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=WECHAT_AUTH_STATE)
        page = context.new_page()
        page.goto("https://mp.weixin.qq.com/")
        page.wait_for_load_state("networkidle")
        url = f"https://mp.weixin.qq.com/cgi-bin/appmsg?action=list_ex&begin=0&count=5&fakeid={fakeid}&type=9&query=&token={token}&lang=zh_CN&f=json"
        r = page.request.get(url)
        browser.close()
        if r.status == 200:
            return r.json().get('app_msg_list', [])
    return []

def fetch_article(url):
    print(f"[4] 抓取文章: {url[:60]}...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    r = requests.get(url, headers=headers, timeout=15)
    r.encoding = 'utf-8'
    m = re.search(r'<div id="js_content".*?</div>', r.text, re.DOTALL)
    if m:
        html = m.group(0)
    else:
        html = r.text
    h = html2text.HTML2Text()
    h.bypass_tables = False; h.ignore_links = False; h.ignore_images = False; h.body_width = 0
    return h.handle(html)

if __name__ == '__main__':
    print("="*50)
    print("微信公众号监控 - 极简测试脚本")
    print("="*50)

    token = get_token()
    if not token:
        print("❌ 获取token失败，请运行get_cookie.py登录")
        exit(1)
    print(f"✅ token: {token[:10]}...")

    name = input("请输入公众号名称: ").strip()
    fakeid = search_fakeid(token, name)
    if not fakeid:
        print(f"❌ 未找到公众号「{name}」")
        exit(1)
    print(f"✅ fakeid: {fakeid}")

    articles = get_articles(token, fakeid)
    if not articles:
        print("❌ 未获取到文章")
        exit(1)
    print(f"✅ 找到 {len(articles)} 篇文章")
    for a in articles:
        print(f"   - {a['title']} ({datetime.datetime.fromtimestamp(a['update_time']).strftime('%Y-%m-%d')})")

    print("\n[测试] 抓取第一篇文章内容...")
    try:
        content = fetch_article(articles[0]['link'])
        print(f"✅ 抓取成功! 内容长度: {len(content)} 字符")
        print(f"\n--- 内容预览 (前500字符) ---")
        print(content[:500])
        print("--- 预览结束 ---")
    except Exception as e:
        print(f"❌ 抓取失败: {e}")

    print("\n" + "="*50)
    print("测试完成!")