import os
from playwright.sync_api import sync_playwright

STORAGE_PATH = os.path.join(os.path.dirname(__file__), "wechat_auth_state.json")

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        ctx = browser.new_context()
        page = ctx.new_page()
        page.goto("https://mp.weixin.qq.com/")
        print("\n请在打开的浏览器中扫码登录微信公众平台...")
        while True:
            url = page.url
            if "cgi-bin/home" in url or "token=" in url:
                page.wait_for_load_state("networkidle")
                ctx.storage_state(path=STORAGE_PATH)
                print(f"登录状态已保存: {STORAGE_PATH}")
                break
            page.wait_for_timeout(1000)
        ctx.close()
        browser.close()

if __name__ == "__main__":
    run()
