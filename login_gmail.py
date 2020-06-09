import asyncio
import time
from pyppeteer import launch


async def gmailLogin(username, password, url):
    # 'headless': False如果想要浏览器隐藏更改False为True
    # 127.0.0.1:1080为代理ip和端口，这个根据自己的本地代理进行更改，如果是vps里或者全局模式可以删除掉'--proxy-server=127.0.0.1:1080'
    browser = await launch({'headless': False, 'args': ['--no-sandbox']})
    page = await browser.newPage()
    await page.setUserAgent(
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36')

    await page.goto(url)

    # 输入Gmail
    await page.type('#identifierId', username)
    # 点击下一步
    await page.click('#identifierNext > content')
    page.mouse  # 模拟真实点击
    time.sleep(20)
    # 输入password
    await page.type('#password input', password)
    # 点击下一步
    await page.click('#passwordNext > content > span')
    page.mouse  # 模拟真实点击
    time.sleep(20)
    # 点击安全检测页面的DONE
    # await page.click('div > content > span')#如果本机之前登录过，并且page.setUserAgent设置为之前登录成功的浏览器user-agent了，
    # 就不会出现安全检测页面，这里如果有需要的自己根据需求进行更改，但是还是推荐先用常用浏览器登录成功后再用python程序进行登录。

    # 登录成功截图
    await page.screenshot({'path': './gmail-login.png', 'quality': 100, 'fullPage': True})
    # 打开谷歌全家桶跳转，以Youtube为例
    await page.goto('https://www.youtube.com')
    time.sleep(10)


if __name__ == '__main__':
    username = 'bnpysse@gmail.com'
    password = r'Gwvbmgfn3631'
    url = 'https://gmail.com'
    loop = asyncio.get_event_loop()
    loop.run_until_complete(gmailLogin(username, password, url))
