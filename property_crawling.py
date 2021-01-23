from urllib.request import urlopen
from bs4 import BeautifulSoup
from selenium.webdriver.support.select import Select
from selenium import webdriver
from bs4 import BeautifulSoup
from pprint import pprint
import requests
import codecs
import os

import pandas as pd

import time
# time.sleep(second)

# html = urlopen("https://rt.molit.go.kr/srh/srh.do?menuGubun=A&srhType=LOC&houseType=1&gubunCode=LAND")
# bsObject = BeautifulSoup(html, "html.parser")

##############################  connect.py  #############################

from selenium import webdriver

#ChromeDriver로 접속, 자원 로딩시간 3초

# driver = webdriver.Chrome('E:/chromedriver/chromedriver_win32/chromedriver')
driver = webdriver.Chrome('chromedriver',options=options)
driver.implicitly_wait(3)

#웹페이지 불러오기
# driver.get('http://www.nfds.go.kr/fr_base_0001.jsf')
driver.get('https://rt.molit.go.kr/srh/srh.do?menuGubun=A&srhType=LOC&houseType=1&gubunCode=LAND')

##############################  date.py  #############################

#날짜 설정
def setDate(startdate, enddate):
    #기준 년도 설정
    alert = driver.switch_to.alert
    alert.accept()
    start = driver.find_element_by_name('srhYear')
    # start.clear()
    start.send_keys(startdate)
    
    #분기 설정
    end = driver.find_element_by_name('srhPeriod')
    # end.clear()
    end.send_keys(enddate)


##############################  parsing.py  #############################

from bs4 import BeautifulSoup

#날짜 파싱
def dateparsing(startdate,enddate):
    
    # f = open("/content/property_crawling.xls", 'a')
    # f.write(startdate)
    # f.write(';')
    # f.write(enddate)
    # f.write(';')
    # f.write('\n')
    pass

#읍,면,동 파싱    
def townguparsing(cityname, guname, townname):
    print("파싱함수 실행됨")
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')



    # table = soup.find('table', class="list_basic")
    table = soup.find("table",{'class' : 'list_basic'}) 
    tbody = table.tbody
    # tr = tbody.find_elements_by_tag_name("td")
    firstbody = str(tbody.get_text())
    # firstbody = str(tr.get_text())
    print(firstbody)

    tmp = firstbody.replace('\n', ';')
    cigutown = str('\n;;' + '삭제탭' +';'+ cityname +';'+ guname +';' + townname + ';')
    tmp2 = tmp.replace(';;;', cigutown)
    # f.write(tmp2)
    # f.write('\n')
    print(cigutown)
    print("입력 완료")

##############################  table_to_2d.py  ################################

from itertools import product

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
            rowspan = rowspans[col] = int(cell.get('rowspan', 1)) or len(rows) - row
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

##############################  city.py  #############################

#시 설정
def setCity(cityvalue):   
    city = driver.find_element_by_xpath("//option[@value='" + str(cityvalue) + "']")
    city.click()
    time.sleep(5)
    
def setCityName(cityvalue):
    city = driver.find_element_by_xpath("//option[@value='" + str(cityvalue) + "']")
    cityname = city.text
    return cityname

##############################  click.py  #############################
# <a href="#" onclick="javascript:fnSubmit(); return false;"><img src="/images/search_btn.gif" alt="검색" style="cursor:pointer;" id="searchBtn" title="검색"></a>
#조회 버튼 클릭
driver.find_element_by_xpath("//a[@onclick='javascript:fnSubmit(); return false;']").click()

##############################  gu.py  #############################

def setTown(cityvalue):
    
    cityname = setCityName(cityvalue)
    # //a[number(substring-after(@href,'/'))

    # table_df2 = pd.DataFrame(columns=range(12))
    # table_df2 = None
    table_df2 = pd.DataFrame() 
    table_df1 = pd.DataFrame() 
    table_df3 = pd.DataFrame() 
    table_df4 = pd.DataFrame() 
    table_df5 = pd.DataFrame() 
    table_df6 = pd.DataFrame() 
    print(table_df2)

    for citynum in range(405, 1000):  # 구/군 설정
        try:
          gu = driver.find_element_by_xpath("//option[@value='" + str(cityvalue) + str(citynum).rjust(3, '0') + "']")
          print(str(cityvalue) + str(citynum).rjust(3, '0'))
          gu.click()
          time.sleep(5)
          guname = gu.text
          print(guname)
          # driver.find_element_by_xpath("//a[@onclick='javascript:fnSubmit(); return false;']").click()
          for townnum in range(100,400): # 읍/면/리 설정
            try:
              print("try는 들어옴")
              town = driver.find_element_by_xpath("//option[@value='" + str(cityvalue) + str(citynum).rjust(3, '0') + str(townnum)+ '00' + "']")
              print(str(cityvalue) + str(citynum).rjust(3, '0') + str(townnum)+ '00')
              town.click()
              # driver.implicitly_wait(30) # 결과 뜰때까지 대기 걸어주기
              townname = town.text
              print(townname)
              print("시/도 : " + cityname + " | 구/군 : " + guname + " | 읍/면/리 : " + townname)
              time.sleep(5)
              print("제출버튼 누르기 전에 딜레이 완료!!!!!!!!!!!!!!!!!!!!!!!!!!")
              driver.find_element_by_xpath("//a[@onclick='javascript:fnSubmit(); return false;']").click()
              print("제출버튼 누름")
              # driver.implicitly_wait(30) # 결과 뜰때까지 대기 걸어주기
              # print("대기 완료")
              # townguparsing(cityname, guname, townname)
              ############################################################################
              print("파싱함수 실행됨")
              time.sleep(5)
              print(" 파싱 태그 찾기전에 로드 기다리기 완료!!!!!!!!!!!!!!!!!!!!!!!!!!")
              firstbody = " "
              html = driver.page_source
              soup = BeautifulSoup(html, 'html.parser')
              print("여기까진 온거야?")
              
              table = soup.find("table",{'class' : 'list_basic'}) 
              # tbody = table.tbody
              td = table.td
              # tr = tbody.find_elements_by_tag_name("td")
              # firstbody = str(tbody.get_text())
              firstbody = str(td.get_text())
              print(firstbody)

              # f = open("/content/property_crawling.xls", 'a')
              # f.write(';;' + '삭제탭' +';')
              # f.write(cityname)
              # f.write(';')
              # f.write(guname)
              # f.write(';')
              # f.write(townname)

              tmp = firstbody.replace('\n', ';')
              cigutown = str('\n;;' + '삭제탭' +';'+ cityname +';'+ guname +';' + townname + ';')
              tmp2 = tmp.replace(';;;', cigutown)
              # f.write(tmp2)
              # f.write('\n')
              print(cigutown)
              print("입력 완료")

              ########################################
              # driver.find_element_by_xpath("//a[@onclick='javascript:fnSubmit(); return false;']").click()
              # time.sleep(5)

              print("pandas시도 시작")

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
              else:
                print("여긴 오긴 하는거야? 3")
                table_df1 = table_df_list[0]

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
              # table_df.to_excel('/content/property_crawling.xls')
              # table_df2.to_excel('drive/My Drive/property_crawling/property_crawling.xlsx') 

              ###################     새로운 시도     #####################

              print("\n\n new try \n\n")

              url2 = "https://rt.molit.go.kr/srh/srh.do?menuGubun=A&srhType=LOC&houseType=1&gubunCode=LAND"

              fullTable2 = '<table class="list_basic">'

              # rPage2 = requests.get(url2)
              # soup2 = BeautifulSoup(rPage2.content, "html")

              rPage2 = driver.page_source
              soup2 = BeautifulSoup(rPage2, 'html.parser')

              
              table2 = soup2.find("table", {"class": "list_basic"})

              rows2 = table2.findAll('tr')

              row_lengths2 = [len(r.findAll(['th', 'td'])) for r in rows2]

              ncols2 = max(row_lengths2)
              nrows2 = len(rows2)

              # rows and cols convert list of list
              for i in range(len(rows2)):
                  rows2[i]=rows2[i].findAll(['th', 'td'])


              # Header - colspan check in Header
              for i in range(len(rows2[0])):
                  col = rows2[0][i]
                  if (col.get('colspan')):
                      cSpanLen = int(col.get('colspan'))
                      del col['colspan']
                      for k in range(1, cSpanLen):
                          rows2[0].insert(i,col)


              # rowspan check in full table
              for i in range(len(rows2)):
                  row = rows2[i]
                  for j in range(len(row)):
                      col = row[j]
                      del col['style']
                      if (col.get('rowspan')):
                          rSpanLen = int(col.get('rowspan'))
                          del col['rowspan']
                          for k in range(1, rSpanLen):
                              rows2[i+k].insert(j,col)


              # create table again
              for i in range(len(rows2)):
                  row = rows2[i]
                  fullTable2 += '<tr>'
                  for j in range(len(row)):
                      col = row[j]
                      rowStr=str(col)
                      fullTable2 += rowStr
                  fullTable2 += '</tr>'

              fullTable2 += '</table>'
              # table links changed
              fullTable2 = fullTable2.replace('/srh/', 'https://rt.molit.go.kr/srh/')
              fullTable2 = fullTable2.replace('\n', '')
              fullTable2 = fullTable2.replace('<br/>', '')
              print(fullTable2)

              table_df_list2 = pd.read_html(fullTable2)

              # 데이터프레임 선택하기
              if table_df4.empty :
                table_df4 = table_df_list2[0]
              else:
                table_df3 = table_df_list2[0]

              print("table_df3 : ")
              print(table_df3)
              print("table_df4 :")
              print(table_df4)

              # table_df2 = pd.concat([table_df2, table_df]) 
              if table_df3.empty == False :
                table_df4 = table_df4.append(table_df3)

              
              table_df4.to_excel('drive/My Drive/property_crawling/property_crawling.xlsx') 
              
              # save file as a name of url
              page2=os.path.split(url2)[1]
              fname2='outuput_{}.html'.format(page2)
              singleTable2 = codecs.open(fname2, 'w', 'utf-8')
              singleTable2.write(fullTable2)



              # here we can start scraping in this table there rowspan and colspan table changed to simple table
              soupTable2 = BeautifulSoup(fullTable2, "lxml")
              urlLinks2 = soupTable2.findAll('a');
              print(urlLinks2)

              ############################################################################
              ############################# new try2  ####################################

              print("\n\n new try 2 \n\n")
              table_html3 = table_to_2d(table2)
              # pprint(table_to_2d(table2), width=30) 

              # table_html = str(table)

              # 판다스의 read_html 로 테이블 정보 읽기
              table_df_list = pd.DataFrame(table_html3)
              print("여긴 오긴 하는거야? 1")

              # 데이터프레임 선택하기
              if table_df6.empty :
                print("여긴 오긴 하는거야? 2")
                table_df6 = table_df_list
              else:
                print("여긴 오긴 하는거야? 3")
                table_df5 = table_df_list

              print("table_df5 : ")
              print(table_df5)
              print("table_df6 :")
              print(table_df6)

              # table_df2 = pd.concat([table_df2, table_df]) 
              if table_df5.empty == False :
                table_df6 = table_df2.append(table_df5)

              
              ##########데이터 프레임 출력############
              print(table_df6)



              #############################################################################
              print("시/도 : " + cityname + " | 구/군 : " + guname + " | 읍/면/리 : " + townname)
            # except:
            except Exception as e:    # 모든 예외의 에러 메시지를 출력할 때는 Exception을 사용
              print('예외가 발생했습니다.', e)
              print(str(cityvalue) + "|" + str(citynum).rjust(3, '0') + "|" + str(townnum)+ '00')
              if(townnum%10000 == 0):
                print("city value : " + cityvalue + " index 다섯자리 : " + str(townnum)+ '00')
        except:
          # print(str(cityvalue) + "|" + str(citynum).rjust(3, '0') + "|" + str(townnum)+ '00')
          # if(citynum%100 == 0):
          print("city num 세자리 : " + str(citynum).rjust(3, '0'))
            


##############################  main.py  #############################

if __name__ == "__main__" :

  startyear = "2020"  #2020년
  startperiod = "1"   #1분기


  # 시 option value 리스트
  city_option_value = [11, 26, 27, 28, 29, 30, 31, 36, 41, 42, 43, 44, 45, 46, 47, 48, 50]

  # 날짜 설정
  setDate(startyear, startperiod)

  # 시, 동 설정
for index in city_option_value:
  dateparsing(startyear, startperiod)
  setCity(index)
  # setGu(index)
  setTown(index)

