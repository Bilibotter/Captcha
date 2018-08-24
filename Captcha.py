import re
import time
import random
import requests
# from PIL import Image
from Extract import Extract
import matplotlib.pyplot as plt
import matplotlib.image as mpimg


# 根据response更新cookie
def Cook(cookie, cookieNew):
    try:
        cookieNew = 'JSESSIONID=' + cookieNew['JSESSIONID'] + '; '
    except KeyError:
        print('No cookie update.')
        return cookie
    if 'JSESSIONID' not in cookie:
        return cookieNew + cookie
    else:
        pattern = 'JSESSIONID=(.*?);'
        return re.sub(pattern, cookieNew, cookie)


# pv自增1
def Rep(cookie):
    cookie = cookie[:-1] + str(int(cookie[-1])+1)

    return cookie


# 用于获取验证码src、JSESSIONID初始数值
def captchaInfo():
    url = "http://zxgk.court.gov.cn/shixin/index_form.do"

    cookie = '_gscu_15322769=33526032qz2hko13; _gscbrs_15322769=1; _gscs_15322769=33607294ho32vv13|pv:1'

    headers = {
        'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        'Accept-Encoding': "gzip, deflate",
        'Accept-Language': "zh-CN,zh;q=0.9",
        'Connection': "keep-alive",
        'Cookie': cookie,
        'Host': "zxgk.court.gov.cn",
        'Referer': "http://zxgk.court.gov.cn/shixin/new_index.html",
        'Upgrade-Insecure-Requests': "1",
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36",
    }
    preSrc = 'http://zxgk.court.gov.cn/shixin/'
    response = requests.request("GET", url, headers=headers)
    print('captchaInfo\'s status_code is:'+str(response.status_code))
    pattern = 'value="(.*?)"/>'
    pattern1 = '<img id="captchaImg" src="(.*?)"'
    captchaId = re.findall(pattern, response.text)[0]
    partSrc = re.findall(pattern1, response.text)[0]

    try:
        cookie = Cook(cookie, response.cookies.get_dict())
    except KeyError:
        print('No cookie update.')
        pass

    captchaSrc = preSrc + partSrc

    return cookie, captchaSrc, captchaId


# 用于下载验证码
def captchaGet(cookie, captchaID, has_ran=False):
    if has_ran:
        captchaSrc = captchaID
    else:
        ran = random.random()
        captchaSrc = f'http://zxgk.court.gov.cn/shixin/captcha.do?captchaId={captchaId}&random{ran}'

    headers = {
        'Accept': "image/webp,image/apng,image/*,*/*;q=0.8",
        'Accept-Encoding': "gzip, deflate",
        'Accept-Language': "zh-CN,zh;q=0.9",
        'Connection': "keep-alive",
        'Cookie': cookie,
        'Host': "zxgk.court.gov.cn",
        'Referer': "http://zxgk.court.gov.cn/shixin/index_form.do",
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/"
                      "68.0.3440.84 Safari/537.36",
    }

    response = requests.request("GET", captchaSrc, headers=headers)

    print(response.status_code)

    with open('captcha.jpg', 'wb')as JPG:
        JPG.write(response.content)

    try:
        cookie = Cook(cookie, response.cookies.get_dict())
    except KeyError:
        print('No cookie update.')
        pass

    with open('cookie.txt', 'w')as Cookie:
        Cookie.write(cookie)

    return cookie


info = input('输入查询信息：')
cookie, captchaSrc, captchaId = captchaInfo()
cookie = captchaGet(cookie, captchaSrc, has_ran=True)
print('Captcha is initialized')

if_continue = True

while if_continue:
    cookie = captchaGet(cookie, captchaId)

    imgplot = plt.imshow(mpimg.imread('captcha.jpg'))
    plt.ion()
    plt.show()

    pCode = input('captcha:')

    findUrl = 'http://zxgk.court.gov.cn/shixin/findDis'

    headers = {
        'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        'Accept-Encoding': "gzip, deflate",
        'Accept-Language': "zh-CN,zh;q=0.9",
        'Cache-Control': "no-cache",
        'Connection': "keep-alive",
        'Content-Length': "100",
        'Content-Type': "application/x-www-form-urlencoded",
        'Cookie': cookie,
        'Host': "zxgk.court.gov.cn",
        'Origin': "http://zxgk.court.gov.cn",
        'Referer': "http://zxgk.court.gov.cn/shixin/index_form.do",
        'Upgrade-Insecure-Requests': "1",
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36",
    }

    data = {
        'pName': info,
        'pCardNum': '',
        'pProvince': 0,
        'pCode': pCode,
        'captchaId': captchaId,
    }

    response = requests.post(findUrl, headers=headers, data=data)
    if_continue = Extract(response.text)
    cookie = Cook(cookie, response.cookies.get_dict())
    cookie = Rep(cookie)
    plt.close()
    print('Close captcha')
