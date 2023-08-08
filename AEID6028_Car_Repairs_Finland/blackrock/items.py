# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Item, Field

class DataItem(Item):
    url = Field()
    site = Field()
    context_identifier = Field()
    source_country = Field()
    feed_code = Field()
    file_create_dt = Field()
    record_create_dt = Field()
    record_create_by = Field()
    execution_id = Field()

    information = Field()
    month_or_date = Field()
    industry = Field()
    variable = Field()
    value = Field()
