import httpx
from app.models.schemas import Article, SettingsModel
from sqlalchemy.orm import Session

class AIService:
    def __init__(self, api_key: str = "", api_base_url: str = "", model: str = "", proxy: str = "http://localhost:10808"):
        self.api_key = api_key
        self.api_base_url = api_base_url or "https://generativelanguage.googleapis.com/v1"
        self.model = model
        self.proxy = proxy

    @classmethod
    def from_db(cls, db: Session):
        rows = {s.key: s.value for s in db.query(SettingsModel).all() if s.key.startswith("ai_")}
        return cls(
            api_key=rows.get("ai_api_key", ""),
            api_base_url=rows.get("ai_api_base_url", ""),
            model=rows.get("ai_model", ""),
            proxy=rows.get("ai_proxy", ""),
        )

    async def generate_summary(self, content: str) -> str:
        if not self.api_key:
            return "未配置API Key"
        if not content:
            return "文章内容为空，无法生成摘要"
        if not self.model:
            return "未配置AI模型，请在系统设置中设置"

        model_name = self.model.replace("models/", "")
        prompt = """你是我的生物医药行业学习助手，服务对象是生物医药海外BD，不是研发科学家。
我会给你一篇医药行业文章、公司新闻、技术文章、管线分析或临床试验解读。你的任务不是普通摘要，而是生成一份"文章总结与行业解读学习笔记"。

请按照以下结构输出：
1. 文章概述
用简洁语言说明这篇文章讲了什么、为什么重要、和生物医药产业链有什么关系。
2. 核心信息表
提取药物类型、技术路线、适应症、靶点/机制、临床阶段、关键数据、核心结论、涉及公司、失败或成功原因。
3. 背景知识补全
自动识别文章中非研发背景读者可能不理解的专业概念。每个概念按照"专业定义 → 通俗解释 → 和本文的关系"解释。
4. 关键问题预测与回答
请站在一个生物医药海外BD的角度，自动提出读完文章后最可能产生的关键问题，并直接回答。问题必须包括机制问题、临床问题、商业问题、CRO服务相关问题和BD沟通问题。
5. 行业解读
从研发、临床、商业、临床前CRO、海外BD五个角度分析这篇文章的意义。
6. 临床前CRO相关启发
说明这篇文章对动物模型、药效评价、PK/PD、毒理、安全性、机制研究、转化医学证据有什么启发。
7. BD可用话术
把文章中的洞察转化成可以用于LinkedIn、邮件、客户沟通或官网内容的表达。
8. 最终学习笔记
用适合长期复习的方式整理：我需要记住什么、容易误解什么、以后看到类似文章应该怎么看。

要求：
* 不要只复述文章。
* 必须补充文章没有明说但理解文章所必需的背景知识。
* 必须解释专业术语。
* 必须指出文章背后的行业逻辑。
* 语言适合非研发背景但从事生物医药BD的人理解。
* 输出要有结构，但不要过度碎片化。
* 使用纯文本格式输出，不要使用Markdown标记（如**、#、-等）。

文章内容：
""" + content[:8000]

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.3, "maxOutputTokens": 4000}
        }
        url = f"{self.api_base_url}/models/{model_name}:generateContent?key={self.api_key}"
        async with httpx.AsyncClient(proxy=self.proxy) as cli:
            r = await cli.post(url, json=payload, timeout=120)
            r.raise_for_status()
            d = r.json()
            parts = d.get('candidates', [{}])[0].get('content', {}).get('parts', [])
            return parts[0].get('text', '').strip() if parts else "摘要生成失败"

    async def generate_summary_for_article(self, db: Session, article_id: int) -> str:
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            return "文章不存在"
        if article.summary:
            return article.summary
        summary = await self.generate_summary(article.content or article.digest or "")
        article.summary = summary
        db.commit()
        return summary