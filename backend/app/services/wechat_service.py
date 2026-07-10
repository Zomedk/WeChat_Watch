import os, re, datetime, requests, html2text, json
from app.config.settings import settings
from app.models.schemas import Article, Subscription
from sqlalchemy.orm import Session

class WechatService:
    def __init__(self):
        self.storage_state_path = settings.WECHAT_AUTH_STATE_PATH
        self.download_dir = settings.DOWNLOAD_DIR
        os.makedirs(self.download_dir, exist_ok=True)

    def _get_cookies(self):
        with open(self.storage_state_path, 'r', encoding='utf-8') as f:
            state = json.load(f)
        cookies = {}
        for c in state['cookies']:
            cookies[c['name']] = c['value']
        return cookies

    def get_wechat_token(self):
        cookies = self._get_cookies()
        r = requests.get('https://mp.weixin.qq.com/', cookies=cookies, timeout=10)
        m = re.search(r'token=(\d+)', r.url)
        return m.group(1) if m else None

    def search_fakeid(self, token: str, name: str):
        cookies = self._get_cookies()
        url = f"https://mp.weixin.qq.com/cgi-bin/searchbiz?action=search_biz&token={token}&lang=zh_CN&f=json&query={requests.utils.quote(name)}&begin=0&count=5"
        r = requests.get(url, cookies=cookies, timeout=10)
        if r.status_code == 200:
            for biz in r.json().get('list', []):
                if biz.get('nickname') == name:
                    return biz.get('fakeid')
        return None

    def get_latest_articles(self, token: str, fakeid: str):
        cookies = self._get_cookies()
        articles = []
        url = f"https://mp.weixin.qq.com/cgi-bin/appmsg?action=list_ex&begin=0&count=10&fakeid={fakeid}&type=9&query=&token={token}&lang=zh_CN&f=json"
        r = requests.get(url, cookies=cookies, timeout=10)
        if r.status_code == 200:
            for msg in r.json().get('app_msg_list', []):
                articles.append({
                    'title': msg.get('title'),
                    'link': msg.get('link'),
                    'date': datetime.datetime.fromtimestamp(msg.get('update_time')).strftime('%Y-%m-%d'),
                    'digest': msg.get('digest')
                })
        return articles

    def download_article(self, url: str, title: str, date_str: str):
        safe = re.sub(r'[\/:*?"<>|]', '_', title).strip()
        folder = f"[{date_str}]{safe}"
        article_dir = os.path.join(self.download_dir, folder)
        os.makedirs(article_dir, exist_ok=True)

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        r = requests.get(url, headers=headers, timeout=15)
        r.encoding = 'utf-8'

        m = re.search(r'<div id="js_content".*?</div>', r.text, re.DOTALL)
        content_html = m.group(0) if m else r.text

        h = html2text.HTML2Text()
        h.bypass_tables = False; h.ignore_links = False; h.ignore_images = False; h.body_width = 0
        md = h.handle(content_html)
        md_path = os.path.join(article_dir, f"{folder}.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n{md}")
        return md_path, md

    def sync_articles(self, db: Session, subscription: Subscription):
        token = self.get_wechat_token()
        if not token:
            return {"success": False, "message": "token失效，请重新登录"}
        arts = self.get_latest_articles(token, subscription.fakeid)
        if not arts:
            subscription.last_sync_at = datetime.datetime.now()
            db.commit()
            return {"success": True, "message": "无新文章", "count": 0}
        cnt = 0
        for a in arts:
            if db.query(Article).filter(Article.url == a['link']).first():
                continue
            try:
                mp, ct = self.download_article(a['link'], a['title'], a['date'])
                art = Article(title=a['title'], url=a['link'], publish_date=datetime.datetime.strptime(a['date'], '%Y-%m-%d').date(),
                              digest=a['digest'], content=ct, markdown_path=mp, subscription_id=subscription.id)
                db.add(art); db.commit(); cnt += 1
            except Exception as e:
                print(f"下载失败: {e}")
        subscription.last_sync_at = datetime.datetime.now()
        db.commit()
        return {"success": True, "message": f"完成", "count": cnt}