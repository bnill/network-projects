import sys
import os
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import urllib
import urlparse
import socket

origin = ""
port = 8080
page_cache = [] #cached file directories
cache_hits = [] #cache hits
#MAX_CACHE = 10485760 #size of 10MB
MAX_CACHE = 80000
current_cache_size = 0

class Custom_Http_Handler(BaseHTTPRequestHandler):
    def do_GET(self): #map to local file
        global current_cache_size, MAX_CACHE
        file_path_name = self.path
        cache_directory = os.path.dirname(os.path.realpath(__file__))
        file_directory = cache_directory + file_path_name
        #file_flag = 1
        #for testing at localhost, a custom httpserver runs at port 8080 like below to provide service
        #self.send_response(200)
        #self.send_header('Content-type', 'text/html')
        #self.end_headers()
        #f = open(file_directory, "r") 
        #self.wfile.write(f.read())     
        if file_directory not in page_cache:#not cached pages retrieve it from origin
            try:
                url = "http://" + origin + ":8080" + file_path_name
                content = urllib.urlopen(url).read()
                if(len(content) == 0):
                    print "404 not found"
                    self.send_error(404,"Not Found: "+ file_path_name)
                #retrieving the uncached file
                else:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(content)
                #send the requested file
                if current_cache_size + sys.getsizeof(content) <= MAX_CACHE:
                    page_cache.append(file_directory)
                    tmp = file_path_name.rsplit("/", 1) 
                    filename = tmp[1]
                    #print filename
                    #print tmp
                    #separate the file directory and file_name
                    if(tmp[0] != "" and (not os.path.exists(tmp[0][1:]))):
                        os.makedirs(tmp[0][1:])
                        # if file directory doesn't exist, then create the directory
                        self.write_file(cache_directory + "/" + tmp[0], content, filename)
                    elif(tmp[0] == ""):
                        self.write_file(cache_directory, content, filename)
                    else:
                        self.write_file(cache_directory + tmp[0], content, filename)
                    page_index = page_cache.index(file_directory)
                    cache_hits.insert(page_index, 1)
                    current_cache_size += sys.getsizeof(content)
                    #print page_cache
                    #print cache_hits
                    #print current_cache_size
                else: #the cache length bigger than the Max_Size 10MB, then update the cache with LRU Algo
                    memory_needed = sys.getsizeof(content) - (MAX_CACHE - current_cache_size)
                    #needed_space minus cache_left
                    self.get_memory_LRU(memory_needed)
                    page_cache.append(file_directory)
                    #same process with above
                    tmp = file_path_name.rsplit("/", 1)
                    filename = tmp[1]
                    if(tmp[0] != "" and (not os.path.exists(tmp[0][1:]))):
                        os.makedirs(tmp[0][1:])
                        self.write_file(cache_directory + "/" + tmp[0], content, filename)
                    elif(tmp[0] == ""):
                        self.write_file(cache_directory, content, filename)
                    else:
                        self.write_file(cache_directory + tmp[0], content, filename)
                    page_index = page_cache.index(file_directory)
                    cache_hits.insert(page_index, 1)
                    current_cache_size += sys.getsizeof(content)
                    #print page_cache
                    #print cache_hits
                    #print current_cache_size
            except:
                print "not found error when caching files"
                self.send_error(404,"Not Found: "+ file_path_name)
    
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            f = open(file_directory, "r")
            self.wfile.write(f.read())
            page_index = page_cache.index(file_directory)
            hit_num = cache_hits[page_index]
            hit_num += 1
            cache_hits[page_index] = hit_num
            #print page_cache
            #print cache_hits
            #print current_cache_size

    def write_file(self, directory, content, filename):
        flag = 0
        while not flag:
            cached_filename = directory + "/" + filename
            f = open(cached_filename, "w")
            f.write(content)
            f.close()
            flag = 1
    def get_memory_LRU(self, memory_space):
        global current_cache_size
        space_cleaned = 0
        while space_cleaned < memory_space:
            min_hit = min(cache_hits)
            page_index = cache_hits.index(min_hit)
            min_directory = page_cache[page_index]
            #print min_directory
            file_size = os.path.getsize(min_directory)
            space_cleaned += file_size
            #update cache_hits, page_cache, current_cache_size
            cache_hits.pop(page_index)
            page_cache.pop(page_index)
            current_cache_size -= file_size
            os.remove(min_directory)
            
            
def server_start(server_port):
    replica_server = HTTPServer(('', server_port), Custom_Http_Handler)
    replica_server.serve_forever()

if __name__ == '__main__':
    sys_input = sys.argv
    port_num = int(sys_input[2])
    origin = sys_input[4]
    if len(sys_input) > 5:
        print "too many parameters"

    try:
        server_start(port_num)
    except:
        print "error for establishing server"
        sys.exit()
