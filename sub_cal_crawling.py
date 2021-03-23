from urllib.request import urlopen
from bs4 import BeautifulSoup
from selenium.webdriver.support.select import Select
from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import pandas as pd
import time
from itertools import product
import pprint
import csv
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import firestore


# Firebase database 인증 및 앱 초기화
# cred = credentials.Certificate(
#     'ziptalk-chatbot-firebase-adminsdk-kz477-4cadf62941.json')
# firebase_admin.initialize_app(cred, {
#     'databaseURL': 'https://ziptalk-chatbot-default-rtdb.firebaseio.com/'
# })
cred = credentials.Certificate(
    'ziptalk-chatbot-firebase-adminsdk-kz477-4cadf62941.json')
firebase_admin.initialize_app(cred, {
    'projectId': 'ziptalk-chatbot',
})

db = firestore.client()

doc_ref = db.collection(u'subscription_info').document()
doc_ref.set({
    'realtime_info':   {'date': '2021-03-22',
                    'apt_info':  {'apt_name': '김천더테라스휴',
                                    'address': '경상북도 김천시 어모면 중왕리 686-1번지',
                                    'sup_size': '176세대',
                                    'tel': '054-436-0888'},
                    'sub_sch':    {'ann_date': '2021-02-19',
                                    'sub_rec':    [{'class_name': '특별공급',
                                                    'local_date': '2021-03-02',
                                                    'other_date': '2021-03-03',
                                                    'recept_place': '인터넷'},
                                                    {'class_name': '1순위',
                                                    'local_date': '2021-03-02',
                                                    'other_date': '2021-03-03',
                                                    'recept_place': '인터넷'},
                                                    {'class_name': '2순위',
                                                    'local_date': '2021-03-02',
                                                    'other_date': '2021-03-03',
                                                    'recept_place': '인터넷'}],
                                    'winner_date': '2021-03-10',
                                    'contract_date': '2021-03-22 ~ 2021-03-24'}}
})

# dir = db.reference()  # 기본 위치 지정
# dir.update({'청약정보': []})

# dir = db.reference('청약정보')
# dir.push({'실시간정보': [{'날짜': '2021-03-22'},
#                         {'아파트정보':  [{'아파트명': '김천더테라스휴'},
#                                         {'공급위치': '경상북도 김천시 어모면 중왕리 686-1번지'},
#                                         {'공급규모': '176세대'},
#                                         {'문의처': '054-436-0888'}]},
#                         {'청약일정':    [{'모집공고일': '2021-02-19'},
#                                         {'청약접수':    [{'구분명':'특별공급'},
#                                                         {'해당지역 접수일':'2021-03-02'},
#                                                         {'기타지역 접수일': '2021-03-03'},
#                                                         {'접수장소':'인터넷'}]},
#                                         {'당첨자 발표일': '2021-03-10'},
#                                         {'계약일': '2021-03-22 ~ 2021-03-24'}]}]})

# dir = db.reference('청약정보/실시간정보/날짜')
# dir.update({'date': '2021-03-22'})
# dir = db.reference('청약정보/아파트정보')
# dir.update({'아파트명': '김천더테라스휴'})
# dir.update({'공급규모': '176세대'})
# dir.update({'문의처': '054-436-0888'})


chrome_options = webdriver.ChromeOptions()  # webdriver의 크롬 옵션 객체 생성
chrome_options.add_argument("--incognito")  # 크롬 옵션에 시크릿 모드 추가
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-features=NetworkService")
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument("--disable-features=VizDisplayCompositor")
# 위에서 만든 크롬 옵션을 적용하여 크롬창 생성]
driver = webdriver.Chrome('./chromedriver.exe', options=chrome_options)
# tor로 proxy server로 바뀐 아이피로 크롤링.
chrome_options.add_argument('--proxy-server=socks5://127.0.0.1:9050')

chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.75 Safari/537.36")
chrome_options.add_argument(
    "app-version=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.75 Safari/537.36")

driver.implicitly_wait(3)

# 웹페이지 불러오기
driver.get('https://www.applyhome.co.kr/ai/aib/selectSubscrptCalenderView.do')


def table_to_2d(table_tag):
    rowspans = []  # track pending rowspans
    rows = table_tag.find_all('tr')

    # first scan, see how many columns we need
    colcount = 0
    for r, row in enumerate(rows):
        cells = row.find_all(['td', 'th'], recursive=False)
        # count columns (including spanned).
        # add active rowspans from preceding rows
        # we *ignore* the colspan value on the last cell, to prevent
        # creating 'phantom' columns with no actual cells, only extended
        # colspans. This is achieved by hardcoding the last cell width as 1.
        # a colspan of 0 means “fill until the end” but can really only apply
        # to the last cell; ignore it elsewhere.
        colcount = max(
            colcount,
            sum(int(c.get('colspan', 1)) or 1 for c in cells[:-1]) + len(cells[-1:]) + len(rowspans))
        # update rowspan bookkeeping; 0 is a span to the bottom.
        rowspans += [int(c.get('rowspan', 1)) or len(rows) - r for c in cells]
        rowspans = [s - 1 for s in rowspans if s > 1]

    # it doesn't matter if there are still rowspan numbers 'active'; no extra
    # rows to show in the table means the larger than 1 rowspan numbers in the
    # last table row are ignored.

    # build an empty matrix for all possible cells
    table = [[None] * colcount for row in rows]

    # fill matrix from row data
    rowspans = {}  # track pending rowspans, column number mapping to count
    for row, row_elem in enumerate(rows):
        span_offset = 0  # how many columns are skipped due to row and colspans
        for col, cell in enumerate(row_elem.find_all(['td', 'th'], recursive=False)):
            # adjust for preceding row and colspans
            col += span_offset
            while rowspans.get(col, 0):
                span_offset += 1
                col += 1

            # fill table data
            rowspan = rowspans[col] = int(
                cell.get('rowspan', 1)) or len(rows) - row
            colspan = int(cell.get('colspan', 1)) or colcount - col
            # next column is offset by the colspan
            span_offset += colspan - 1
            value = cell.get_text()
            for drow, dcol in product(range(rowspan), range(colspan)):
                try:
                    table[row + drow][col + dcol] = value
                    rowspans[col + dcol] = rowspan
                except IndexError:
                    # rowspan or colspan outside the confines of the table
                    pass

        # update rowspan bookkeeping
        rowspans = {c: s - 1 for c, s in rowspans.items() if s > 1}

    return table


if __name__ == "__main__":
    time.sleep(1)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    print("여기까진 온거야?")

    f = open(f'subscription.csv', 'a', encoding='utf-8', newline='')
    wr = csv.writer(f)

    table = soup.find("table", {'class': 'tbl_st'})
    # td = table.td
    for monthNum in range(1, 13):
        # driver.get(
        #     'https://www.applyhome.co.kr/ai/aib/selectSubscrptCalenderView.do')
        # time.sleep(1)
        # month_button = driver.find_element_by_xpath(
        #     "//*[@id='subContent']/div[1]/div[2]/ul/li["+str(monthNum)+"]/button")
        # month_button.click() 
        # time.sleep(0.5)
        # html = driver.page_source
        # soup = BeautifulSoup(html, 'html.parser')
        # table = soup.find("table", {'class': 'tbl_st'})
        for tr_num in range(1, 6): # 달력 줄 번호
            for td_num in range(1, 6): # 달력 칸 번호
                for event in range(1, 3):
                    try:
                        date = ""
                        apt_name = ""
                        address = ""
                        sup_size = ""
                        tel = ""
                        ann_date = ""
                        class_name = ["", "", ""]
                        local_date = ["", "", ""]
                        other_date = ["", "", ""]
                        recept_place = ["", "", ""]
                        winner_date = ""
                        contract_date = ""

                        driver.get(
                            'https://www.applyhome.co.kr/ai/aib/selectSubscrptCalenderView.do')
                        time.sleep(0.5)
                        month_button = driver.find_element_by_xpath(
                            "//*[@id='subContent']/div[1]/div[2]/ul/li["+str(monthNum)+"]/button")
                        month_button.click() 
                        time.sleep(0.5)
                        html = driver.page_source
                        soup = BeautifulSoup(html, 'html.parser')
                        table = soup.find("table", {'class': 'tbl_st'})

                        # date = table.find("td", {'data-ids': str(dateNum)})
                        # print(str(date.get_text()))
                        date = driver.find_element_by_xpath("//*[@id='calTable']/tbody/tr["+str(tr_num)+"]/td["+str(td_num)+"]/a[1]/b")
                        print(date)

                        # popup = driver.find_element_by_xpath(
                        #     "//*[@id='calTable']/tbody/tr[1]/td["+str(dateNum)+"]/a["+str(event)+"]")
                        popup = driver.find_element_by_xpath(
                            "//*[@id='calTable']/tbody/tr["+str(tr_num)+"]/td["+str(td_num)+"]/a["+str(event)+"]")
                        print("a태그 찾음")
                        print(popup)
                        popup.click()
                        print("클릭함")
                        time.sleep(2)
                        print("2초 지남")
                        html = driver.page_source
                        print("html 불러옴")
                        soup = BeautifulSoup(html, 'html.parser')
                        iframe = driver.find_elements_by_tag_name('iframe')[0]
                        driver.switch_to.frame(iframe)

                        html = driver.page_source
                        soup = BeautifulSoup(html, 'html.parser')
                        # iframe = soup.find("iframe")
                        basic_table = soup.find(
                            "table", {'class': 'tbl_st tbl_normal tbl_center'})

                        table_list = soup.find_all('table')

                        table_name_list = [['<<기본정보>>'], ['<<청약일정>>'], ['<<공급대상>>'], [
                            '<<특별공급 공급대상>>'], ['<<공급금액, 2순위 청약금 및 입주예정월>>'], ['<<기타사항>>']]
                        # pprint.pprint(table_to_2d(basic_table), width=30)
                        ## 기본정보 ##
                        print("기본정보")
                        print(table_to_2d(basic_table))

                        ## 청약일정 ##
                        print("청약일정")
                        schedule_table = soup.find(
                            "table", {'class': 'tbl_st tbl_row tbl_col tbl_center'})
                        print(table_to_2d(schedule_table))

                        ## 공급대상 ##
                        print("공급대상")
                        target_table = table_list[2]
                        print(table_to_2d(target_table))

                        ## 특별공급 공급대상 ##
                        print("특별공급 공급대상")
                        special_target_table = table_list[3]
                        print(table_to_2d(special_target_table))

                        ## 공급금액, 2순위 청약금 및 입주예정월 ##
                        print("공급금액, 2순위 청약금 및 입주예정월")
                        cost_table = table_list[4]
                        print(table_to_2d(cost_table))

                        ## 기타사항 ##
                        etc_table = table_list[5]
                        print("기타사항")
                        print(table_to_2d(etc_table))
                        print(table_to_2d(etc_table)[0])
                        print(len(table_to_2d(etc_table)))
                        table_order = [basic_table, schedule_table, target_table,
                                    special_target_table, cost_table, etc_table]

                        # wr.writerow(table_to_2d(basic_table))
                        # wr.writerow(table_to_2d(schedule_table))
                        # wr.writerow(table_to_2d(target_table))
                        # wr.writerow(table_to_2d(special_target_table))
                        # wr.writerow(table_to_2d(cost_table))
                        # wr.writerow(table_to_2d(etc_table))
                        for order in range(0, 6):
                            # print(table_name_list[order])
                            wr.writerow(table_name_list[order], )
                            for i in range(0, len(table_to_2d(table_order[order]))):
                                # print((table_to_2d(table_order[order]))[i])
                                # print((table_to_2d(table_order[order]))[i][0])
                                
                                if("공급위치" in (table_to_2d(table_order[order]))[i][0]):
                                    print((table_to_2d(table_order[order]))[i][1])
                                
                                elif("공급규모" in (table_to_2d(table_order[order]))[i][0]):
                                    print((table_to_2d(table_order[order]))[i][1])
                            
                                elif("문의처" in (table_to_2d(table_order[order]))[i][0]):
                                    print((table_to_2d(table_order[order]))[i][1])
                                
                                elif("모집공고일" in (table_to_2d(table_order[order]))[i][0]):
                                    print((table_to_2d(table_order[order]))[i][1])
                                
                                elif("청약접수" in (table_to_2d(table_order[order]))[i][0]):
                                    if("구분" in (table_to_2d(table_order[order]))[i][1]):
                                        if("특별공급" in (table_to_2d(table_order[order]))[i+1][1]):
                                            print((table_to_2d(table_order[order]))[i+1][1])
                                            print((table_to_2d(table_order[order]))[i+1][2])
                                            print((table_to_2d(table_order[order]))[i+1][3])
                                            print((table_to_2d(table_order[order]))[i+1][4])
                                        if("1순위" in (table_to_2d(table_order[order]))[i+2][1]):
                                            print((table_to_2d(table_order[order]))[i+2][1])
                                            print((table_to_2d(table_order[order]))[i+2][2])
                                            print((table_to_2d(table_order[order]))[i+2][3])
                                            print((table_to_2d(table_order[order]))[i+2][4])
                                        if("2순위" in (table_to_2d(table_order[order]))[i+3][1]):
                                            print((table_to_2d(table_order[order]))[i+3][1])
                                            print((table_to_2d(table_order[order]))[i+3][2])
                                            print((table_to_2d(table_order[order]))[i+3][3])
                                            print((table_to_2d(table_order[order]))[i+3][4])
                                            
                                    # else:
                                        # print((table_to_2d(table_order[order]))[i][1])

                                
                                elif((table_to_2d(table_order[order]))[i][0] == "당첨자 발표일"):
                                    print((table_to_2d(table_order[order]))[i][1])
                                    
                                elif((table_to_2d(table_order[order]))[i][0] == "계약일"):
                                    print((table_to_2d(table_order[order]))[i][1])
                                

                                wr.writerow(table_to_2d(table_order[order])[i])

                    except Exception as e:    # 모든 예외의 에러 메시지를 출력할 때는 Exception을 사용
                        print('예외가 발생했습니다.', e)
                        pass

    # firstbody = str(table.get_text())
    # print(firstbody)
