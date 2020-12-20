from selenium import webdriver
from urllib import parse
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import requests
from lxml import etree
import json
import os
from fpdf import FPDF
from PIL import Image


book = {}       # 一本漫画书的章节页面信息
book_name = ''  # 一本漫画书的名字 也作为存放图片的目录名


def get_chapter_url(book_url: str) -> dict:
    """
    获取每一章节名称和链接信息
    :param book_url: 漫画书的链接
    :return: dict: 返回每一章节名称和链接信息
    """
    global book_name
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/87.0.4280.88 Safari/537.36'}
    rep = requests.get(url=book_url, headers=headers).text
    tree = etree.HTML(rep)
    book_name = tree.xpath('//span[@class="anim_title_text"]//h1/text()')[0]
    if not os.path.exists(book_name):
        os.mkdir(book_name)
    links = tree.xpath('//div[@class="cartoon_online_border"]/ul/li/a/@href')
    vols = tree.xpath('//div[@class="cartoon_online_border"]/ul/li/a/text()')
    for vol in vols:
        book[vol] = ''
    chap_dict = dict(zip(vols, links))
    return chap_dict


def get_pic(directory: str, kw: str, pic_url: str, referer: str):
    """
    下载漫画的每一页图片
    :param directory: 保存的目录
    :param kw: 保存的文件名
    :param pic_url: 图片url
    :param referer: 请求需要的referer参数
    :return:
    """
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/87.0.4280.88 Safari/537.36',
               'Referer': referer,
               }
    res = requests.get(url=pic_url, headers=headers).content
    with open(f'./{directory}/{kw}', 'wb') as fp:
        fp.write(res)
        print(f'saved {kw}...')


def get_chapter_content(directory: str, driver, url: str, vol: str):
    """
    获取漫画的每一章节内容
    :param directory: 保存的目录
    :param driver: 浏览器driver对象
    :param url: 章节的url
    :param vol: 章节的名称
    :return:
    """
    driver.get(url)
    print(f'{vol}开始下载...')
    pages = []
    try:
        driver.find_element_by_class_name('login_tip').click()
    except Exception:
        pass
    while True:
        img = driver.find_element_by_xpath('//div[@id="center_box"]/img')
        raw_link = img.get_attribute('src')
        link = parse.unquote(raw_link.split('/b/')[-1])
        keyword = ''
        for i in link.split('/'):
            keyword = keyword + i.strip(' ')
        pages.append(keyword)
        # print(keyword)
        get_pic(directory, keyword, raw_link, url)
        next_img = driver.find_element_by_class_name('img_land_next')
        driver.execute_script("arguments[0].click();", next_img)
        time.sleep(1)
        if driver.find_element_by_class_name('pop_bbsadmin_top').text == '提示信息':
            break
        try:
            if driver.find_element_by_class_name('info').text == '你已浏览完本漫画所有内容，您可以：':
                break
        except Exception:
            pass
    book[vol] = pages


def gen_pdf(book, directory):
    img_direction = True
    page_direction = True

    first_img_path = book[list(book.keys())[0]][0]
    first_img = Image.open(f'./{directory}/{first_img_path}')
    width = first_img.size[0]
    height = first_img.size[1]
    first_img.close()
    if width > height:
        page_direction = True
    else:
        page_direction = False
    pdf = FPDF(unit='pt', format=[width, height])
    pdf.set_auto_page_break(0)
    pdf.set_margins(0, 0, 0)
    for vol in list(book.keys()):
        pages = book[vol]
        for page in pages:
            img = Image.open(f'./{directory}/{page}')
            img_w = img.size[0]
            img_h = img.size[1]
            print(f'{img_w}  {img_h}')
            if img_w > img_h:
                img_direction = True
            else:
                img_direction = False
            pdf.add_page()
            if img_direction == page_direction:
                pdf.image(f'{directory}/{page}', w=width, h=height)
            else:
                img.rotate(-90).save('./temp.jpg')
                pdf.image(f'./temp.jpg', w=width, h=height)
                os.remove('./temp.jpg')
            img.close()
            print(f'add page {page}...')
    pdf.output(f'./{directory}.pdf', 'F')
    print('ok!')


def main():
    book_url = input('enter url: ')
    driver = webdriver.Chrome('./chromedriver')
    url_dict = get_chapter_url(book_url)
    for vol in list(url_dict.keys()):
        url = 'https://manhua.dmzj.com' + url_dict[vol]
        get_chapter_content(book_name, driver, url, vol)
    driver.close()
    # print(book)
    with open(f'./{book_name}/info.json', 'w') as fp:
        json.dump(book, fp)
    gen_pdf(book, book_name)


if __name__ == '__main__':
    main()
