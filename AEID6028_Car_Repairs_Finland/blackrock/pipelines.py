from datetime import datetime as dt
from os import environ



class BlackrockPipeline:
    @staticmethod
    def process_item(item, spider):
        item["record_create_dt"] = dt.utcnow().strftime("%Y-%m-%d %T")
        item["feed_code"] = spider.AEID_project_id
        item["site"] = spider.site
        item["record_create_by"] = spider.name
        item["execution_id"] = environ.get("SHUB_JOBKEY", None)
        item["file_create_dt"] = spider.file_create_dt
        item["source_country"] = spider.source_country
        return item


class DefaultValuesPipeline:
    @staticmethod
    def process_item(item, spider):
        for field in item.fields:
            item.setdefault(field, "Null")
        return item
