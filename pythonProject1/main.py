#!/usr/bin/python
# from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from http.server import BaseHTTPRequestHandler,HTTPServer
from socketserver import ThreadingMixIn
import json
import re
from urllib.parse import parse_qs
import cgi

PORT_NUMBER = 8023

# This class will handle any incoming request from
# a browser
class myHandler(BaseHTTPRequestHandler):


    # Handler for the GET requests
    # get으로 요청되었을때
    def do_GET(self):
        # / api / v1 / ping
        print('Get request received')
        # 입력한 path가 /api/v1/getrecord/로 시작하는것이 아닌게 아니라면
        if None != re.search('/api/v1/getrecord/*', self.path):
            # self.path = /api/v1/getrecord/?city=seoul&zipcode=08206&mobile=01012341234&nickname=cat
            # recordId는 path를 '/'로 나눈 각문자들 중 마지막 문자를 '?'로 나누어서 첫번째에 해당하는문자
            # 1번 문제는 retStr을 self.wfile.write 문장에 %s에 기존에 대응되는 self.path에 바꿔주면 됩니다.
            # html문장 response 구성할 때, 파이썬의 딕셔너리 자료는 wfile에서 호환불가하여
            # json.dump(딕셔너리 자료) 로 문자열로 변환하여 응답하면 됩니다.
            recordID = (self.path.split('/')[-2])
            print("recordID = ", recordID)
            result1 = (self.path.split('?')[-1]).split('&')
            result = (result1[0].split('='))[0]
            print(result)
            print(result1)
            result2 = {}
            # a = 0
            for i in range(len(result1)):
                result2[(result1[i].split('='))[0]] = (result1[i].split('='))[1]
            print(result2)
            if recordID == "getrecord" :
                retstr = 'city' + " : " + result2["city"] + " " + 'zipcode' + " : " + result2["zipcode"] + \
                         " " + 'mobile' + " : " + result2["mobile"] + " " + 'nickname' + " : " + result2["nickname"]
                self.send_response(200)
                # 클라이언트한테 힌트를 준다
                # 내가 text/html형태로 본문을 보낼테니깐 너가 파싱해서 적당하게 표현을 해
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                # Send the html message
                # utf8형태로 문자열 인코딩
                self.wfile.write(bytes("<html><head><title>Title goes here.</title></head>", "utf-8")) #"euc-kr"
                self.wfile.write(bytes("<body><p>This is a test.</p>", "utf-8"))
                self.wfile.write(bytes("<p>You accessed path: %s</p>" % self.path, "utf-8"))
                self.wfile.write(bytes("</body></html>", "utf-8"))
                self.wfile.write(bytes(retstr, "utf-8"))

            else:
                self.send_response(400, 'Bad Request: record does not exist')
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
        else:
            self.send_response(400, 'Bad Request: record does not exist')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()

    def do_POST(self):
        if None != re.search('/api/v1/addrecord/*', self.path):
            # cgi.parse_header: 헤더정보를 읽기 편하게 파싱해준다.
            # 파라미터(self.headers['content-type'])에 어떤 정보를 주면 왼쪽에 튜플형태로 리턴해주는 함수다
            # self.header에 key로 'content-type'을 주면 해당하는 정보를 파싱을 해서 ctype과 pdict로 넘겨준다.
            ctype, pdict = cgi.parse_header(self.headers['content-type']) # application/json;encoding=utf-8;lang=ko;loc=seoul;...
            print(ctype) # application/json
            print(pdict) # {encoding:utf-8, lang:ko, loc:seoul}

            if ctype == 'application/json':
                # Content-Length는 자동으로 계산해준다.(postman에서 request와 동시에)
                content_length = int(self.headers['Content-Length']) # 48 bytes
                # Content-Length만큼 읽어라
                post_data = self.rfile.read(content_length)
                # 읽은것을 utf-8로 디코드한다.
                receivedData = post_data.decode('utf-8')
                print(receivedData)
                # print(type(receivedData))
                # string 타입의 receivedData를 딕셔너리 타입으로 변환한다.
                tempDict = json.loads(receivedData) #  load your str into a dict
                print(tempDict)
                print(tempDict["성명"] + "님의 주소는 " + tempDict["주소"] + " 이메일은 " + tempDict["email"])
                retstr = tempDict["성명"] + "님의 주소는 " + tempDict["주소"] + " 이메일은 " + tempDict["email"]
                # print(type(tempDict))
                #print(type(tempDict)) #print(tempDict['this'])
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                # json.dumps: 딕셔너리타입의 tempDict를 string형태로 변환해주는 함수다.
                # 딕셔너리라는것은 파이썬만 알고있는 자료형이다.
                # 포스트맨이든 크롬이든 그 딕셔너리를 못알아먹는다. 알아먹을수있는건 단순 문자열
                # 그래서 문자열로 바꾸어준다.
                # json.dumps처리하지않고 tempDict를 본문에 쓰려면 에러가 발생한다.
                # self.wfile.write(bytes(json.dumps(tempDict), "utf-8"))
                self.wfile.write(bytes(retstr, "utf-8"))


            elif ctype == 'application/x-www-form-urlencoded':
                content_length = int(self.headers['content-length'])
                # trouble shooting, below code ref : https://github.com/aws/chalice/issues/355
                # parse_qs(query string) -> 오른쪽 라이브러리에 있는거 from urllib.parse import parse_qs
                # postvars도 딕셔너리다.
                postvars = parse_qs((self.rfile.read(content_length)).decode('utf-8'),keep_blank_values=True)

                #print(postvars)    #print(type(postvars)) #print(postvars.keys())

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(bytes(json.dumps(postvars) ,"utf-8"))
            else:
                self.send_response(403)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()

        else:
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()

        # ref : https://mafayyaz.wordpress.com/2013/02/08/writing-simple-http-server-in-python-with-rest-and-json/


        return


try:

    # Create a web server and define the handler to manage the
    # incoming request
    server = HTTPServer(('', PORT_NUMBER), myHandler)
    print ('Started httpserver on port ' , PORT_NUMBER)

    # Wait forever for incoming http requests
    server.serve_forever()

except:
    print ('^C received, shutting down the web server')
    print("서버 종료1!!")
    server.socket.close()
m