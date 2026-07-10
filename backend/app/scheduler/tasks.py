from apscheduler.schedulers.background import BackgroundScheduler
from app.models.database import SessionLocal
from app.models.schemas import Subscription
from app.services.wechat_service import WechatService
from app.config.settings import settings

scheduler = BackgroundScheduler()
wechat = WechatService()

def sync_all():
    db = SessionLocal()
    try:
        for sub in db.query(Subscription).filter(Subscription.status == "active").all():
            print(f"同步: {sub.name}")
            print(wechat.sync_articles(db, sub))
    finally:
        db.close()

def start_scheduler():
    scheduler.add_job(sync_all, 'interval', minutes=settings.SYNC_INTERVAL_MINUTES, id='sync', replace_existing=True)
    scheduler.start()
    print(f"定时同步已启动（每{settings.SYNC_INTERVAL_MINUTES}分钟）")

def shutdown_scheduler():
    scheduler.shutdown()
