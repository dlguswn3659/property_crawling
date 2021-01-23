from urllib.request import urlopen
from bs4 import BeautifulSoup
from selenium.webdriver.support.select import Select
from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import pandas as pd
import time


from make_data import settown_real

#ChromeDriver로 접속, 자원 로딩시간 3초

# 매크로 추적을 피하기 위해 창을 시크릿모드로 열어주기.(해봤는데 어림없음)

chrome_options = webdriver.ChromeOptions()  # webdriver의 크롬 옵션 객체 생성
chrome_options.add_argument("--incognito")  # 크롬 옵션에 시크릿 모드 추가
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome('./chromedriver.exe', options=chrome_options) # 위에서 만든 크롬 옵션을 적용하여 크롬창 생성]

driver.implicitly_wait(3)

#웹페이지 불러오기
driver.get('https://rt.molit.go.kr/srh/srh.do?menuGubun=A&srhType=LOC&houseType=1&gubunCode=LAND')



#날짜 설정
def setDate(startdate, enddate):
    #기준 년도 설정
    alert = driver.switch_to.alert
    alert.accept()
    start = driver.find_element_by_name('srhYear')
    start.send_keys(startdate)
    
    #분기 설정
    end = driver.find_element_by_name('srhPeriod')
    end.send_keys(enddate)
    


##############################  click.py  #############################
#조회 버튼 클릭
driver.find_element_by_xpath("//a[@onclick='javascript:fnSubmit(); return false;']").click()


##############################  main.py  #############################

if __name__ == "__main__" :

  startyear = "2020"  #2020년
  startperiod = "1"   #1분기


  # 시 option value 리스트
  city_option_value = [11, 26, 27, 28, 29, 30, 31, 36, 41, 42, 43, 44, 45, 46, 47, 48, 50]

  # 날짜 설정
  setDate(startyear, startperiod)
  settown_real()