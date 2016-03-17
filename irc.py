# IRC Crawler
# Jimmy Trimer

import socket
import time
import datetime
import threading
from crawler import Crawler
from result import *
from crawlerconfig import * 

class IRC(Crawler):
    def __init__(self, config):
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = config.get_location()
        self.nickname = config.options["nickname"]
        self.mins_interval = config.options["mins_interval"]
        self.total_mins = config.options["total_mins"]
        self.connect()
        self.channels = self.getChannels()
        self.run()

    def connect(self):
        print("Connecting to server... %s" % self.server)
        self.irc.connect((self.server, 6667))
        self.irc.send("USER " + self.nickname + " " + self.nickname + " " + self.nickname + " :" + self.nickname
                      + " \n")
        self.irc.send("NICK " + self.nickname + "\n")
        while(True):
            temp = self.irc.recv(2048)
            if(temp == "" or temp == None or temp == "-1"):
                break
            if("End of /MOTD" in temp):
                break  
        print("Connected to %s!" % self.server)
        return 

    # join an irc channel
    # must be connected to server first    
    def joinChannel(self, channel):
        self.channel = channel
        self.irc.send("JOIN " + self.channel + "\n")
        return 

    # Recv data from irc server 
    def get_text(self):
        text = self.irc.recv(2048)

        if text.find('PING') != -1:
            self.irc.send('PONG ' + text.split()[1] + "\r\n")
            return ""
        return text

    # return list of channels from server
    def getChannels(self):
        print("Getting Channels..."),
        self.irc.send("LIST\n")
        data = ""
        while(True):
            d = self.irc.recv(2048)
            data += d 
            if(d == "" or d == None or d == "-1"):
                break
            if("End of /LIST" in d):
                break

        channels = []
        data_split = data.split("\n")
        for line in data_split:
              if "322" in line:
                channel = line.split(" ")[3]
                channels.append(channel)
        return channels
        
    # def doCrawl(self, mins_interval, total_mins, crawler_config, channel):
     def doCrawl(self, channel):
        session_text = ""
        finished = False
        i = 0

        self.joinChannel(channel) 
        print("Starting to listen... %s" % channel)
        start_time_total = time.time()
        start_time = time.time()
        cur_time = time.time() 
        while(not finished):
            #print("cur_time: %d total_time: %d"  % ((cur_time - start_time), (cur_time - start_time_total)))
            text = self.get_text()
            if text != "": 
                #print(session_text)
                session_text += (text+"\n")
            cur_time = time.time()
            if((cur_time - start_time) >= self.mins_interval*60):
                #print("="*80)
                #print(session_text)
                utc_start_time = datetime.datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
                utc_cur_time = datetime.datetime.fromtimestamp(cur_time).strftime('%Y-%m-%d %H:%M:%S')
                print("Start time: %s End time: %s %s" % (utc_start_time, utc_cur_time, channel))
                result = Results(self.config, utc_start_time, utc_cur_time, (self.server, channel), "", session_text)
                self.send_result(result)
                session_text = ""
                start_time = time.time()
                if((cur_time - start_time_total) >= self.total_mins*60):
                    finished = True
        return 

        # run each crawl in a thread
        def run(self, num_threads):
            for i in range(0, num_threads):
                t = threading.Thread(target=self.doCrawl, args=(self.channels[i], ))
                t.start()
            return
        
if __name__ == "__main__":
    options = { nickname: "tnasty1",
                mins_interval: 1,
                total_mins: 2,    
    }
    #CrawlerConfig = location, protocol, speed(interval), maxDepth(duration), name
    config = CrawlerConfig("irc.freenode.net", "IRC", "", "","", options)
    #channel = "#linux" # where does channel fit into CrawlerConfig?
    #source = (config.get_location(), channel)
    #nickname = "tnasty1"
    #mins_interval = config.get_speed() # how often to get data
    #total_mins = config.get_maxDepth() # how long to run (total time)

    irc = IRC(source[0], nickname)
    #irc.connect()
    #channels = irc.getChannels()
    #print(channels)
    #print(len(channels))


    # results_list = listen(irc, mins_interval, total_mins, config, cha)
    print("Done")


