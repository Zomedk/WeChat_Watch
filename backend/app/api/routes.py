from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import List, Optional
from app.models.database import get_db
from app.models.schemas import Subscription, Article, SettingsModel
from app.models.pydantic import SubscriptionCreate, SubscriptionUpdate, SubscriptionResponse, ArticleResponse, AIConfigUpdate
from app.services.wechat_service import WechatService
from app.services.ai_service import AIService

router = APIRouter()
wechat = WechatService()

@router.get("/subscriptions", response_model=List[SubscriptionResponse])
def list_subs(db: Session = Depends(get_db)):
    return db.query(Subscription).all()

@router.get("/subscriptions/search")
def search_sub(name: str = Query(..., description="公众号名称")):
    token = WechatService().get_wechat_token()
    if not token:
        raise HTTPException(400, "微信登录已失效，请重新登录")
    fakeid = wechat.search_fakeid(token, name)
    if not fakeid:
        raise HTTPException(404, f"未找到公众号「{name}」")
    return {"name": name, "fakeid": fakeid}

@router.post("/subscriptions", response_model=SubscriptionResponse)
def add_sub(sub: SubscriptionCreate, db: Session = Depends(get_db)):
    fakeid = sub.fakeid
    if not fakeid:
        token = WechatService().get_wechat_token()
        if not token:
            raise HTTPException(400, "微信登录已失效，请重新登录")
        fakeid = wechat.search_fakeid(token, sub.name)
        if not fakeid:
            raise HTTPException(404, f"未搜索到公众号「{sub.name}」，请检查名称是否正确")
    if db.query(Subscription).filter(Subscription.fakeid == fakeid).first():
        raise HTTPException(400, "该公众号已存在")
    s = Subscription(name=sub.name, fakeid=fakeid)
    db.add(s); db.commit(); db.refresh(s)
    return s

@router.put("/subscriptions/{id}", response_model=SubscriptionResponse)
def upd_sub(id: int, sub: SubscriptionUpdate, db: Session = Depends(get_db)):
    s = db.query(Subscription).filter(Subscription.id == id).first()
    if not s: raise HTTPException(404, "不存在")
    if sub.name: s.name = sub.name
    if sub.status: s.status = sub.status
    db.commit(); db.refresh(s)
    return s

@router.delete("/subscriptions/{id}")
def del_sub(id: int, db: Session = Depends(get_db)):
    s = db.query(Subscription).filter(Subscription.id == id).first()
    if not s: raise HTTPException(404, "不存在")
    db.delete(s); db.commit()
    return {"message": "已删除"}

@router.post("/subscriptions/{id}/sync")
def sync_sub(id: int, db: Session = Depends(get_db)):
    s = db.query(Subscription).filter(Subscription.id == id).first()
    if not s: raise HTTPException(404, "不存在")
    return wechat.sync_articles(db, s)

@router.get("/articles", response_model=List[ArticleResponse])
def list_articles(subscription_id: Optional[int] = Query(None), publish_date: Optional[date] = Query(None),
                  is_read: Optional[bool] = Query(None), skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    q = db.query(Article)
    if subscription_id: q = q.filter(Article.subscription_id == subscription_id)
    if publish_date: q = q.filter(Article.publish_date == publish_date)
    if is_read is not None: q = q.filter(Article.is_read == is_read)
    arts = q.order_by(Article.publish_date.desc()).offset(skip).limit(limit).all()
    result = []
    for a in arts:
        sub = db.query(Subscription).filter(Subscription.id == a.subscription_id).first()
        result.append(ArticleResponse(id=a.id, title=a.title, url=a.url, publish_date=a.publish_date,
                      digest=a.digest, summary=a.summary, is_read=a.is_read,
                      subscription_name=sub.name if sub else None, created_at=a.created_at))
    return result

@router.put("/articles/{id}/read")
def mark_read(id: int, db: Session = Depends(get_db)):
    a = db.query(Article).filter(Article.id == id).first()
    if not a: raise HTTPException(404, "不存在")
    a.is_read = not a.is_read
    db.commit()
    return {"message": "已更新", "is_read": a.is_read}

@router.post("/articles/{id}/summary")
async def gen_summary(id: int, db: Session = Depends(get_db)):
    a = db.query(Article).filter(Article.id == id).first()
    if not a: raise HTTPException(404, "不存在")
    ai = AIService.from_db(db)
    try:
        summary = await ai.generate_summary(a.content or a.digest or "")
        if not summary.startswith("AI摘要失败") and not summary.startswith("未配置"):
            a.summary = summary
            db.commit()
        return {"summary": summary}
    except Exception as e:
        return {"summary": f"AI摘要失败: {str(e)}"}

@router.get("/auth/status")
def auth_status():
    t = WechatService().get_wechat_token()
    return {"status": "logged_in" if t else "not_logged_in"}

@router.post("/settings/ai")
def save_ai(cfg: AIConfigUpdate, db: Session = Depends(get_db)):
    for k, v in {"ai_api_key": cfg.api_key, "ai_api_base_url": cfg.api_base_url, "ai_model": cfg.model, "ai_proxy": cfg.proxy}.items():
        s = db.query(SettingsModel).filter(SettingsModel.key == k).first()
        if s: s.value = v
        else: db.add(SettingsModel(key=k, value=v))
    db.commit()
    return {"message": "已保存"}

@router.get("/settings/ai")
def get_ai(db: Session = Depends(get_db)):
    return {s.key: s.value for s in db.query(SettingsModel).all() if s.key.startswith("ai_")}