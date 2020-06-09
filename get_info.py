import asyncio
import pyppeteer
from collections import namedtuple

Response = namedtuple("rs", "title url html cookies headers history status")


async def get_html(url):
    browser = await pyppeteer.launch(headless=True, args=['--no-sandbox'])
    page = await  browser.newPage()
    res = await page.goto(url, options={'timeout': 8000})
    data = await page.content()
    title = await page.title()
    resp_cookies = await page.cookies()  # cookie
    resp_headers = res.headers  # 响应头
    resp_status = res.status  # 响应状态
    print(data)
    print(title)
    print(resp_headers)
    print(resp_status)
    return title


if __name__ == '__main__':
    url_list = ["https://www.toutiao.com/",
                "http://jandan.net/ooxx/page-8#comments",
                "https://www.12306.cn/index/"
                ]
    task = [get_html(url) for url in url_list]

    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(asyncio.gather(*task))
    for res in results:
        print(res)