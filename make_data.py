from urllib.request import urlopen
from bs4 import BeautifulSoup
from selenium.webdriver.support.select import Select
from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import pandas as pd
import time

from set_code_list import make_areacode_list

chrome_options = webdriver.ChromeOptions()  # webdriver의 크롬 옵션 객체 생성
chrome_options.add_argument("--incognito")  # 크롬 옵션에 시크릿 모드 추가
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-features=NetworkService")
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument("--disable-features=VizDisplayCompositor")
driver = webdriver.Chrome('./chromedriver.exe', options=chrome_options) # 위에서 만든 크롬 옵션을 적용하여 크롬창 생성]
chrome_options.add_argument('--proxy-server=socks5://127.0.0.1:9050')   # tor로 proxy server로 바뀐 아이피로 크롤링.

chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.75 Safari/537.36")
chrome_options.add_argument("app-version=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.75 Safari/537.36")

driver.implicitly_wait(3)

#웹페이지 불러오기
driver.get('https://rt.molit.go.kr/srh/srh.do?menuGubun=A&srhType=LOC&houseType=1&gubunCode=LAND')

driver.find_element_by_xpath("//a[@onclick='javascript:fnSubmit(); return false;']").click()


#시 설정
def setCity(cityvalue):   
    city = driver.find_element_by_xpath("//option[@value='" + str(cityvalue) + "']")
    city.click()
    time.sleep(5)

def setCityName(cityvalue):
    city = driver.find_element_by_xpath("//option[@value='" + str(cityvalue) + "']")
    cityname = city.text
    return cityname

def settown_real():
    dongcode_list, citycode, gucode, dongcode = make_areacode_list()
  
    table_df1 = pd.DataFrame() 
    table_df2 = pd.DataFrame() 

    for areanumber in range(0, len(dongcode_list)) :  # 구/군 설정
        try:
            cityname = setCityName(citycode[areanumber])
            city = driver.find_element_by_xpath("//option[@value='" + citycode[areanumber] + "']")
            city.click()
            time.sleep(3)

            gu = driver.find_element_by_xpath("//option[@value='" + citycode[areanumber] + gucode[areanumber] + "']")
            print(citycode[areanumber] + gucode[areanumber])
            gu.click()
            time.sleep(3)
            guname = gu.text
            print(guname)

            
            print("try는 들어옴")
            town = driver.find_element_by_xpath("//option[@value='" + citycode[areanumber] + gucode[areanumber] + dongcode[areanumber] + "']")
            print(citycode[areanumber] + gucode[areanumber] + dongcode[areanumber])
            town.click()
            townname = town.text
            print(townname)
            print("시/도 : " + cityname + " | 구/군 : " + guname + " | 읍/면/리 : " + townname)
            time.sleep(3)
            print("제출버튼 누르기 전에 딜레이 완료!!!!!!!!!!!!!!!!!!!!!!!!!!")
            driver.find_element_by_xpath("//a[@onclick='javascript:fnSubmit(); return false;']").click()
            print("제출버튼 누름")
            
            print("파싱함수 실행됨")
            time.sleep(3)
            print(" 파싱 태그 찾기전에 로드 기다리기 완료!!!!!!!!!!!!!!!!!!!!!!!!!!")
            firstbody = " "
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            print("여기까진 온거야?")
            
            table = soup.find("table",{'class' : 'list_basic'}) 
            td = table.td
            
            firstbody = str(td.get_text())
            print(firstbody)

            print("입력 완료")

            ###################     새로운 시도     #####################

            # 현재 페이지에서 table 태그 모두 선택하기
            # tables = soup.select("table",{'class' : 'list_basic'})

            # 하나의 테이블 태그 선택하기
            # tabled = tables[0]

            # 테이블 html 정보를 문자열로 변경하기
            # table_html = str(tabled)
            table_html = str(table)

            # 판다스의 read_html 로 테이블 정보 읽기
            table_df_list = pd.read_html(table_html)
            print("여긴 오긴 하는거야? 1")

            # 데이터프레임 선택하기
            if table_df2.empty :
                print("여긴 오긴 하는거야? 2")
                table_df2 = table_df_list[0]
                table_df2["도시 이름"] = cityname
                table_df2["구 이름"] = guname
                table_df2["동 이름"] = townname
                table_df2["법정동코드"] = citycode[areanumber] + gucode[areanumber] + dongcode[areanumber]

            else:
                print("여긴 오긴 하는거야? 3")
                table_df1 = table_df_list[0]
                table_df1["도시 이름"] = cityname
                table_df1["구 이름"] = guname
                table_df1["동 이름"] = townname
                table_df1["법정동코드"] = citycode[areanumber] + gucode[areanumber] + dongcode[areanumber]

            print("table_df1 : ")
            print(table_df1)
            print("table_df2 :")
            print(table_df2)

            # table_df2 = pd.concat([table_df2, table_df]) 
            if table_df1.empty == False :
                table_df2 = table_df2.append(table_df1)

            
            ##########데이터 프레임 출력############
            print(table_df2)

            # 매개 변수로 저장할 파일 이름을 전달합니다.
            table_df2.to_excel('./data_files/property_data.xlsx') 

            ############################################################################
            
            print("시/도 : " + cityname + " | 구/군 : " + guname + " | 읍/면/리 : " + townname)
            # except:
            
        except Exception as e:    # 모든 예외의 에러 메시지를 출력할 때는 Exception을 사용
                print('예외가 발생했습니다.', e)
                print(citycode[areanumber] + gucode[areanumber] + dongcode[areanumber])

