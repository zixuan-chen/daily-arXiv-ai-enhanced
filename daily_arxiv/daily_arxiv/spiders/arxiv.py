import scrapy
import os
import re
from datetime import datetime, timedelta, timezone


class ArxivSpider(scrapy.Spider):
    name = "arxiv"
    allowed_domains = ["export.arxiv.org"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = os.environ.get("CATEGORIES", "cs.CV")
        categories = [c.strip() for c in categories.split(",")]
        self.target_categories = set(categories)

        # 用官方 API，每个分类查询最近1天的论文，最多500篇
        self.start_urls = [
            f"https://export.arxiv.org/search/?searchtype=cat&query={cat}"
            f"&start=0&max_results=300"
            for cat in categories
        ]

    def parse(self, response):
        # API 返回 Atom XML，用 xpath 解析
        response.selector.remove_namespaces()

        for entry in response.xpath("//entry"):
            arxiv_id_url = entry.xpath("id/text()").get("")
            # id 格式: http://arxiv.org/abs/2401.12345v1
            arxiv_id = arxiv_id_url.split("/abs/")[-1].split("v")[0]

            # 获取所有分类
            paper_categories = set(
                entry.xpath("category/@term").getall()
            )

            # 只保留目标分类的论文
            if paper_categories.intersection(self.target_categories):
                yield {
                    "id": arxiv_id,
                    "categories": list(paper_categories),
                }
                self.logger.info(
                    f"Found paper {arxiv_id} with categories {paper_categories}"
                )
            else:
                self.logger.debug(
                    f"Skipped {arxiv_id}: {paper_categories}"
                )
