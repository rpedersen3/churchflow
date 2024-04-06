from enum import Enum
from typing import Optional, List
from datetime import datetime
import json

class Context:
    title: str

    def __init__(self, title: str) -> None:
        self.title = title


class Kind(Enum):
    CUSTOMSEARCH_RESULT = "customsearch#result"


class CSEImage:
    src: str

    def __init__(self, src: str) -> None:
        self.src = src


class CSEThumbnail:
    src: str
    width: int
    height: int

    def __init__(self, src: str, width: int, height: int) -> None:
        self.src = src
        self.width = width
        self.height = height


class Metatag:
    og_image: Optional[str]
    og_type: Optional[str]
    og_image_width: Optional[int]
    twitter_title: Optional[str]
    twitter_card: Optional[str]
    og_site_name: Optional[str]
    viewport: Optional[str]
    twitter_url: Optional[str]
    og_title: Optional[str]
    og_image_height: Optional[int]
    og_url: Optional[str]
    twitter_image: Optional[str]
    msapplication_tileimage: Optional[str]
    twitter_text_title: Optional[str]
    og_locale: Optional[str]
    og_description: Optional[str]
    article_publisher: Optional[str]
    twitter_site: Optional[str]
    article_modified_time: Optional[datetime]
    apple_mobile_web_app_status_bar_style: Optional[str]
    apple_mobile_web_app_capable: Optional[str]
    twitter_label1: Optional[str]
    twitter_data1: Optional[str]
    msapplication_tilecolor: Optional[str]
    facebook_domain_verification: Optional[str]
    twitter_description: Optional[str]
    og_image_type: Optional[str]
    al_ios_app_name: Optional[str]
    bingbot: Optional[str]
    al_ios_url: Optional[str]
    al_ios_app_store_id: Optional[int]
    format_detection: Optional[str]

    def __init__(self, og_image: Optional[str], og_type: Optional[str], og_image_width: Optional[int], twitter_title: Optional[str], twitter_card: Optional[str], og_site_name: Optional[str], viewport: Optional[str], twitter_url: Optional[str], og_title: Optional[str], og_image_height: Optional[int], og_url: Optional[str], twitter_image: Optional[str], msapplication_tileimage: Optional[str], twitter_text_title: Optional[str], og_locale: Optional[str], og_description: Optional[str], article_publisher: Optional[str], twitter_site: Optional[str], article_modified_time: Optional[datetime], apple_mobile_web_app_status_bar_style: Optional[str], apple_mobile_web_app_capable: Optional[str], twitter_label1: Optional[str], twitter_data1: Optional[str], msapplication_tilecolor: Optional[str], facebook_domain_verification: Optional[str], twitter_description: Optional[str], og_image_type: Optional[str], al_ios_app_name: Optional[str], bingbot: Optional[str], al_ios_url: Optional[str], al_ios_app_store_id: Optional[int], format_detection: Optional[str]) -> None:
        self.og_image = og_image
        self.og_type = og_type
        self.og_image_width = og_image_width
        self.twitter_title = twitter_title
        self.twitter_card = twitter_card
        self.og_site_name = og_site_name
        self.viewport = viewport
        self.twitter_url = twitter_url
        self.og_title = og_title
        self.og_image_height = og_image_height
        self.og_url = og_url
        self.twitter_image = twitter_image
        self.msapplication_tileimage = msapplication_tileimage
        self.twitter_text_title = twitter_text_title
        self.og_locale = og_locale
        self.og_description = og_description
        self.article_publisher = article_publisher
        self.twitter_site = twitter_site
        self.article_modified_time = article_modified_time
        self.apple_mobile_web_app_status_bar_style = apple_mobile_web_app_status_bar_style
        self.apple_mobile_web_app_capable = apple_mobile_web_app_capable
        self.twitter_label1 = twitter_label1
        self.twitter_data1 = twitter_data1
        self.msapplication_tilecolor = msapplication_tilecolor
        self.facebook_domain_verification = facebook_domain_verification
        self.twitter_description = twitter_description
        self.og_image_type = og_image_type
        self.al_ios_app_name = al_ios_app_name
        self.bingbot = bingbot
        self.al_ios_url = al_ios_url
        self.al_ios_app_store_id = al_ios_app_store_id
        self.format_detection = format_detection


class Webpage:
    image: str
    url: str

    def __init__(self, image: str, url: str) -> None:
        self.image = image
        self.url = url


class Pagemap:
    cse_thumbnail: Optional[List[CSEThumbnail]]
    metatags: List[Metatag]
    cse_image: Optional[List[CSEImage]]
    webpage: Optional[List[Webpage]]

    def __init__(self, cse_thumbnail: Optional[List[CSEThumbnail]], metatags: List[Metatag], cse_image: Optional[List[CSEImage]], webpage: Optional[List[Webpage]]) -> None:
        self.cse_thumbnail = cse_thumbnail
        self.metatags = metatags
        self.cse_image = cse_image
        self.webpage = webpage


class Item:
    kind: Kind
    title: str
    htmlTitle: str
    link: str
    displayLink: str
    snippet: str
    htmlSnippet: str
    cacheId: Optional[str]
    formattedUrl: str
    htmlFormattedUrl: str
    pagemap: Pagemap

    def __init__(self, kind: Kind, title: str, htmlTitle: str, link: str, displayLink: str, snippet: str, htmlSnippet: str, cacheId: Optional[str], formattedUrl: str, htmlFormattedUrl: str, pagemap: Pagemap) -> None:
        self.kind = kind
        self.title = title
        self.htmlTitle = htmlTitle
        self.link = link
        self.displayLink = displayLink
        self.snippet = snippet
        self.htmlSnippet = htmlSnippet
        self.cacheId = cacheId
        self.formattedUrl = formattedUrl
        self.htmlFormattedUrl = htmlFormattedUrl
        self.pagemap = pagemap


class NextPage:
    title: str
    totalResults: int
    searchTerms: str
    count: int
    startIndex: int
    inputEncoding: str
    outputEncoding: str
    safe: str
    cx: str

    def __init__(self, title: str, totalResults: int, searchTerms: str, count: int, startIndex: int, inputEncoding: str, outputEncoding: str, safe: str, cx: str) -> None:
        self.title = title
        self.totalResults = totalResults
        self.searchTerms = searchTerms
        self.count = count
        self.startIndex = startIndex
        self.inputEncoding = inputEncoding
        self.outputEncoding = outputEncoding
        self.safe = safe
        self.cx = cx


class Queries:
    request: List[NextPage]
    next_page: List[NextPage]

    def __init__(self, request: List[NextPage], nextPage: List[NextPage]) -> None:
        self.request = request
        self.nextPage = nextPage


class SearchInformation:
    searchTime: float
    formattedSearchTime: str
    totalResults: int
    formattedTotalResults: str

    def __init__(self, search_time: float, formattedSearchTime: str, totalResults: int, formattedTotalResults: str) -> None:
        self.search_time = search_time
        self.formattedSearchTime = formattedSearchTime
        self.totalResults = totalResults
        self.formattedTotalResults = formattedTotalResults


class URL:
    type: str
    template: str

    def __init__(self, type: str, template: str) -> None:
        self.type = type
        self.template = template


class GoogleJsonResponse:
    kind: str
    url: URL
    queries: Queries
    context: Context
    searchInformation: SearchInformation
    items: List[Item]

    def __init__(self, kind: str, url: URL, queries: Queries, context: Context, searchInformation: SearchInformation, items: List[Item]) -> None:
        self.kind = kind
        self.url = url
        self.queries = queries
        self.context = context
        self.searchInformation = searchInformation
        self.items = items
