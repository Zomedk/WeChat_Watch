from fastapi import APIRouter
from playwright.sync_api import sync_playwright
from app.config.settings import settings

router = APIRouter()

@router.get("/qrcode")
def qrcode():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://mp.weixin.qq.com/")
        page.wait_for_load_state("networkidle")
        img = page.locator("img[alt='微信公众平台登录二维码']")
        src = img.get_attribute("src") if img.count() > 0 else None
        browser.close()
        return {"qrcode_url": src} if src else {"error": "未找到二维码"}

@router.get("/qrcode/status")
def qrcode_status():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://mp.weixin.qq.com/")
        page.wait_for_load_state("networkidle")
        ok = "token=" in page.url or "cgi-bin/home" in page.url
        if ok:
            page.context.storage_state(path=settings.WECHAT_AUTH_STATE_PATH)
        browser.close()
        return {"status": "logged_in" if ok else "waiting"}
