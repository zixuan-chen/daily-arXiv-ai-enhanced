import scrapy
import os


class ArxivSpider(scrapy.Spider):
    name = "arxiv"
    allowed_domains = ["export.arxiv.org"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = os.environ.get("CATEGORIES", "cs.CV")
        categories = [c.strip() for c in categories.split(",")]
        self.target_categories = set(categories)

        # 正确的 arXiv API 格式
        self.start_urls = [
            f"http://export.arxiv.org/api/query?search_query=cat:{cat}&start=0&max_results=300&sortBy=submittedDate&sortOrder=descending"
            for cat in categories
        ]

    def parse(self, response):
        response.selector.remove_namespaces()

        for entry in response.xpath("//entry"):
            arxiv_id_url = entry.xpath("id/text()").get("")
            # id 格式: http://arxiv.org/abs/2401.12345v1
            arxiv_id = arxiv_id_url.split("/abs/")[-1].split("v")[0]

            if not arxiv_id:
                continue

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
