# property_crawling

## If you use google colab, you need to do...

!pip install selenium

!wget https://chromedriver.storage.googleapis.com/2.42/chromedriver_linux64.zip  && unzip chromedriver_linux64

# install chromium, its driver, and selenium
!apt-get update
!apt install chromium-chromedriver
!cp /usr/lib/chromium-browser/chromedriver /usr/bin
!pip install selenium
# set options to be headless, ..
from selenium import webdriver
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
# open it, go to a website, and get results
wd = webdriver.Chrome('chromedriver',options=options)
wd.get("https://www.website.com")
print(wd.page_source)  # results

# -----------------------아래는 사전에 찐으로 해줘야하는 작업-------------------------------
1. pip install selenium

2. 다음 webdriver를 다운로드하여야 합니다. 저는 Chrome을 주로 사용하기 때문에 ChomreDriver를 다운로드한다.

    ChromeDriver Download link : https://chromedriver.chromium.org/downloads

    위 사이트를 들어가서 본인의 크롬 버전에 맞는 ChromeDriver를 다운로드 해야한다.
    본인의 크롬 버전을 확인하려면 아래 주소를 브라우저 URL에 넣으면 된다.

    chrome://version

    ※ 오른쪽 상단의 옵션 메뉴 중 도움말(E)> Chrome 정보(G) 페이지를 통해서도 확인할 수 있다.

    예 ) Chrome	87.0.4280.141 (공식 빌드) (64비트) (cohort: 88_96_win)

3. 다운로드한 압축파일을 해제하면 chromedriver.exe 파일이 있는데 해당 파일을 본인이 접근이 쉬운 폴더로 이동시켜 준다. 
    해당 코드에서는 readme.md와 같은 위치에 옮겨주면 된다. 

4. C:\Python\Python{version}\Scripts(파이썬 설치 경로 안에 Scripts 폴더 //  위치 확인은 cmd에서 python을 실행시켜 
import sys
sys.executable
을 입력하면 확인할 수 있다.
ex) "C:\\Users\\HyunjuLee\\AppData\\Local\\Programs\\Python\\Python39\\"
) 로 이동 후 
    pip install beautifulsoup4 
    pip install selenium
    pip install requests
    pip install pandas
    pip install numpy
    pip install xlrd
    pip install openpyxl
    pip install lxml

    설치 

    또는
    https://studyhard24.tistory.com/234 -> beautifulsoup 설치 링크 참고

5. 매크로 봇 탐지를 피하기 위한 세팅하기
    1. random ip로 크롤링. tor 설치(링크 : https://www.torproject.org/download/)

5. python main.py