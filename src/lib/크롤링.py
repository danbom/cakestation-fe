# 25개구 for문으로 돌려서 레터링 케이크 가게 정보 크롤링하기
import os
from time import sleep
import time
import re
from turtle import home
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

##########################################################################
##################### variable related selenium ##########################
##########################################################################
# 서울 특별시 구 리스트
# gu_list = ['마포구','서대문구','은평구','종로구','중구','용산구','성동구','광진구',
#             '동대문구','성북구','강북구','도봉구','노원구','중랑구','강동구','송파구',
#             '강남구','서초구','관악구','동작구','영등포구','금천구','구로구','양천구','강서구']

gu_list = ['도봉구']

# csv 파일에 헤더 만들어 주기
for index, gu_name in enumerate(gu_list): # index.__str__() + '_' + gu_name + '.'+'csv'
    fileName = 'test.csv'
    file = open(fileName, 'w', encoding='utf-8')
    file.write("가게명" + "|" + "주소" + "|" + "영업시간" + "|" + "전화번호" + "|" + "대표사진주소" + "|" + "홈페이지" + "|" + "카카오맵주소" + "\n") # 처음에 csv파일에 칼럼명 만들어주기
    file.close()
    
    options = webdriver.ChromeOptions()
    options.add_argument('lang=ko_KR')

    chromedriver_path = "C:/Users/yuri/Downloads/chromedriver_win32/chromedriver.exe"
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)  # chromedriver 열기
    driver.get('https://map.kakao.com/')  # 주소 가져오기

    search_area = driver.find_element("xpath", '//*[@id="search.keyword.query"]') # 검색 창
    search_area.send_keys(gu_name + ' 레터링케이크')  # 검색어 입력

    submit = driver.find_element("xpath", '//*[@id="search.keyword.submit"]') # 검색
    submit.send_keys(Keys.ENTER)
    driver.implicitly_wait(3) # wait
    
    more_page = driver.find_element("xpath", '//*[@id="info.search.place.more"]') # 상세보기
    more_page.send_keys(Keys.ENTER)
    # 첫 번째 검색 페이지 끝

    time.sleep(1)

    # 다음 
    next_btn = driver.find_element("id", "info.search.page.next")
    has_next = "disabled" not in next_btn.get_attribute("class").split(" ")
    Page = 1
    while has_next: # 다음 페이지가 있으면 loop
        file = open(fileName, 'a', encoding='utf-8')
        time.sleep(1)
        page_links = driver.find_elements("css selector", "#info\.search\.page a")
        pages = [link for link in page_links if "HIDDEN" not in link.get_attribute("class").split(" ")]

        # pages를 하나씩 클릭하면서
        for i in range(1, 6):
            xPath = '//*[@id="info.search.page.no' + str(i) + '"]'
            try:
                page = driver.find_element("xpath", xPath)
                page.send_keys(Keys.ENTER)
            except ElementNotInteractableException:
                print('End of Page')
                break;
            sleep(1)
            place_lists = driver.find_elements('css selector', '#info\.search\.place\.list > li')
            for p in place_lists: # WebElement
                time.sleep(1)
                store_html = p.get_attribute('innerHTML')
                store_info = BeautifulSoup(store_html, "html.parser")
                place_name = store_info.select('.head_item > .tit_name > .link_name')

                if len(place_name) == 0:
                    continue # 광고

                place_name = store_info.select('.head_item > .tit_name > .link_name')[0].text
                place_address = store_info.select('.info_item > .addr > p')[0].text
                place_hour = store_info.select('.info_item > .openhour > p > a')[0].text
                place_tel = store_info.select('.info_item > .contact > span')[0].text

                # 홈페이지url 수집
                homepage = p.find_element('css selector', 'div.info_item > div.contact > a.homepage')
                place_url = ""
                try:
                    url = homepage.get_attribute('href')
                    if url == "#none":
                        place_url = ""
                    else:
                        place_url = url
                except:
                    place_url = ""

                # 사진url 수집
                detail = p.find_element('css selector', 'div.info_item > div.contact > a.moreview')
                detail.send_keys(Keys.ENTER)

                driver.switch_to.window(driver.window_handles[-1])

                place_photo = ""
                try:
                    photo = driver.find_element('css selector', 'span.bg_present')
                    photo_url = photo.get_attribute('style')
                    m = re.search('"(.+?)"', photo_url)
                    if m:
                        place_photo = m.group(1)
                    else:
                        place_photo = ""
                except:
                    place_photo = ""

                # 카카오맵 url 수집
                place_map = ""
                try: 
                  select_map = driver.find_element('css selector', 'a.link_place')
                  map_url = select_map.get_attribute('href')
                  if map_url == "#none":
                      place_map = ""
                  else:
                      place_map = map_url
                except:
                    place_map = ""
                driver.close()
                driver.switch_to.window(driver.window_handles[0])

                print(place_name, place_map)

                file.write(place_name + "|" + place_address + "|" + place_hour + "|" + place_tel + "|" + place_photo + "|" + place_url + "|" + place_map + "\n")
            print(i, ' of', ' [ ' , Page, ' ] ')
        next_btn = driver.find_element("id", "info.search.page.next")
        has_next = "disabled" not in next_btn.get_attribute("class").split(" ")
        if not has_next:
            print('Arrow is Disabled')
            driver.close()
            file.close()
            break # 다음 페이지 없으니까 종료
        else: # 다음 페이지 있으면
            Page += 1
            next_btn.send_keys(Keys.ENTER)
    print("End of Crawl")
