import socket, re
import sys
from urlparse import urlparse


#Checking for script arguments
sarg_length = len(sys.argv)
if(sarg_length != 3):
	print "Error: Either very few or more parameter supplied!"
	exit()
else:
	user = sys.argv[1]
	passw = sys.argv[2]

#user = "001284143"
#passw = "F667U2PW"

#Initialzing variables
csrftoken_id = ""
session_id = ""
flag_count = 0
visited = [""]
book_pages = []
global link
link = "http://cs5700f16.ccs.neu.edu/accounts/login/?next=/fakebook/"

def connect_server():
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect(("cs5700f16.ccs.neu.edu", 80))
	return sock

def get_session_csrftoken_id():
	global session_id, csrftoken_id, link
	#Creating socket and connecting to the server
	sock = connect_server()
	parsed_url = urlparse(link)
	path = parsed_url.path
	httpHeader = "GET " + str(link) + " HTTP/1.0\r\n" + "Host: cs5700sp16.ccs.neu.edu\r\n" + "Connection: keep-alive\r\n\r\n"
	sock.send(httpHeader)
	get_out = sock.recv(2048)
	sock.close()
	data = get_out.splitlines()
	status_code = data[0].split()[1]
	
	if(status_code == "200"):
		#Extracting csrtoken id and session id from output
		csrftoken_id = data[7].split(";")[0].split(":")[1][11 :]
		session_id = data[8].split(";")[0].split(":")[1][11 :]
	else:
		print "Error: Unexpected status code " + str(status_code) + " Error: Wrong credentials entered, Check your Credentials and try again"
		exit()
		
	

def login(user, passw):
	global session_id, csrftoken_id, link
	location_redirect = ""
	
	#Creating socket and connecting to the server
	sock = connect_server()
	
	parsed_url = urlparse(link)
	path = parsed_url.path
	query = parsed_url.query
	
	data = "csrfmiddlewaretoken=" + csrftoken_id + "&username=" + user + "&password=" + passw + "&" + query
	content_len = len(data)
	post_httpmsg = "POST "+ path +" HTTP/1.1\r\n"
	post_httpmsg += "Host: cs5700f16.ccs.neu.edu\r\n"
	post_httpmsg += "User-Agent: Mozilla/5.0\r\n"
	post_httpmsg += "Content-Length: " + str(content_len) + "\r\n"
	post_httpmsg += "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\n"
	post_httpmsg += "Origin: http://cs5700sp15.ccs.neu.edu\r\n"
	post_httpmsg += "Referer: " + link + "\r\n"
	post_httpmsg += "Content-Type: application/x-www-form-urlencoded\n"
	post_httpmsg += "Cookie: csrftoken=" + csrftoken_id + "; sessionid=" + session_id + "\r\n"
	post_httpmsg += "Connection: keep-alive\r\n\r\n" + data + "\r\n"
	sock.send(post_httpmsg)
	post_out = sock.recv(2048)
	data1 = post_out.splitlines()
	status_code = data1[0].split()[1]
	
	if(status_code == "302"):
		session_id = data1[7].split(";")[0].split(":")[1][11 :]
		location_redirect = data1[9].split()[1]
		return location_redirect
	else:
		print "Error: Wrong credentials entered, Check your Credentials and try again"
		exit()

def raw_crawler(url):
	global session_id, csrftoken_id, flag_count, visited, book_pages
	if(flag_count == 5):
		exit()
		
	#Creating socket and connecting to the server
	sock = connect_server()
	
	get_httpmsg = "GET "+ url +" HTTP/1.1\r\n"
	get_httpmsg += "Host: cs5700f16.ccs.neu.edu\r\n"
	get_httpmsg += "Connection: keep-alive\r\n"
	get_httpmsg += "Cache-Control: max-age=0"
	get_httpmsg += "User-Agent: Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.101 Safari/537.36\r\n"
	get_httpmsg += "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\n"
	get_httpmsg += "Cookie: csrftoken="+csrftoken_id+"; sessionid=" + session_id + "\r\n"
	get_httpmsg += "Referer: http://cs5700f16.ccs.neu.edu/accounts/login/?next=/fakebook/\n\n"
	sock.send(get_httpmsg)
	page = sock.recv(2048)
	sock.close()
	
	data = page.splitlines()
	status_code = data[0].split()[1]
	
	if status_code != "200":
		if status_code == "301" :
			error_301 = page.splitlines()
			new_url = error_301[5].split()[1]
			visited.append(url)
			if new_url not in visited:
				raw_crawler(new_url)  
			else:
				return 0
		elif status_code == "403" or status_code == "404":
			visited.append(url)
			return 0
		elif status_code == "500":
			raw_crawler(url)
		else:
			return 0
	else :
		url_pattern = '/fakebook/(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
		url_found = re.findall(url_pattern, page)
		book_pages = book_pages + url_found
	
		secret_pattern = """<h2 class='secret_flag' style="color:red">FLAG: ([0-9A-Za-z]*)</h2>"""
		secret_flag = re.findall(secret_pattern, page)
		if secret_flag:
			flag_count += 1
			print secret_flag[0]
	
		visited.append(url)
	


get_session_csrftoken_id()
fakebook_homepage = login(user, passw)
parsed_homepage = urlparse(fakebook_homepage)
raw_crawler(parsed_homepage.path)

while flag_count < 5:
	for url_link in book_pages:
		if url_link not in visited:
			raw_crawler(url_link)