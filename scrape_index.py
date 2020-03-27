# -*- coding: utf-8 -*-
import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtWebKit import *
from lxml import html
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
import time, os
from datetime import datetime, timedelta
import shutil

#Take this class for granted.Just use result of rendering.
class Render(QWebPage):
  def __init__(self, url):
    self.app = QApplication(sys.argv)
    QWebPage.__init__(self)
    self.loadFinished.connect(self._loadFinished)
    self.mainFrame().load(QUrl(url))
    self.app.exec_()

  def _loadFinished(self, result):
    self.frame = self.mainFrame()
    self.app.quit()

# Funnction to return weekday in Chinese
def WeekdayInChinese(Engday):
    weekday = Engday.upper()
    if weekday == 'MON':
        Chiday = '一'
    elif weekday == 'TUE':
        Chiday = '二'
    elif weekday == 'WED':
        Chiday = '三'
    elif weekday == 'THU':
        Chiday = '四'
    elif weekday == 'FRI':
        Chiday = '五'
    elif weekday == 'SAT':
        Chiday = '六'
    else:
        Chiday = '日'
    return '星期' + Chiday

# Function to print message with system time
def Log(mesg):
    print(datetime.now().strftime('%H:%M:%S') + ' ' + mesg)
    return

Log('Apple Daily: scrape_index starts...')

# Program begins
if len(sys.argv)<2:
    print('Error: Missing <Topic ID>!')
    print('Usage: python scrape_index.py <Topic ID>')
    quit()  # Exit program

# Validate the parameter
topicID = sys.argv[1]
if (topicID != '1' and topicID != '2' and topicID != '3' and topicID != '4' and topicID != '5'):
  print('Error: Wrong <Topic ID>!')
  quit()
else:
  print('<Topic ID>: '+topicID)
	
# Define project home path
#project_path = '.'  # for Windows or RPi interactive
project_path = '/home/pi/Projects/appledaily'  # for RPi cron job
tmp_path = project_path+'/tmp'  # for RPi cron job

#domain = 'https://hk.news.appledaily.com'
if topicID == '1':
  oncc_index_url = 'https://hk.news.appledaily.com/daily/local/'
  indexTmpFile = tmp_path+'/main_index.txt'
  html_file = 'main_index.html'
elif topicID == '2':
  oncc_index_url = 'https://hk.finance.appledaily.com/daily/finance/'
  indexTmpFile = tmp_path+'/finance_index.txt'
  html_file = 'finance_index.html'
elif topicID == '3':
  oncc_index_url = 'https://hk.lifestyle.appledaily.com/'
  indexTmpFile = tmp_path+'/lifestyle_index.txt'
  html_file = 'lifestyle_index.html'
elif topicID == '4':
  oncc_index_url = 'https://hk.entertainment.appledaily.com/daily/entertainment'
  indexTmpFile = tmp_path+'/entertainment_index.txt'
  html_file = 'entertainment_index.html'
elif topicID == '5':
  oncc_index_url = 'https://hk.news.appledaily.com/daily/international/'
  indexTmpFile = tmp_path+'/international_index.txt'
  html_file = 'international_index.html'

  
#Commented on 17.11.2017
#Fail to use lxml in crontab mode to render webpage.
#lxml works fine in interactive mode.
#Instead, use PhantomJS in crontab mode.
# Render web page by lxml
#r = Render(domain)
#Log('Saving web page using phantomjs...')
#cmd = 'phantomjs '+project_path+'/saveWebPage.js '+oncc_index_url+' > '+indexTmpFile
Log('Saving web page using curl...')
cmd = 'curl '+oncc_index_url+' > '+indexTmpFile
os.system(cmd)
# Program will wait for phantomjs to finish, so no need to sleep
#Log('Sleep 10 secs...')
#time.sleep(10)

# Parsing data by Beautiful Soup
#soup = BeautifulSoup(r.frame.toHtml(), 'html.parser') #for lxml method
soup = BeautifulSoup(open(indexTmpFile, encoding='utf-8'), 'html.parser') #for PhantomJS
#print (soup.encode('utf-8'))

# Get cover image
#head_img = soup.find('img', class_='headline')
#head_img_url = domain + head_img['src']

# Get all items from the Drop Down List
article_list = soup.find('select', id='article_ddl')
article_type=[]
article_title=[]
article_href=[]
article_oncc_href=[]
#for optgroup in article_list.findAll('optgroup'):
optgroup = article_list.find('optgroup')
#print('inside optgroup')
#print(optgroup.encode('utf-8'))
# Add group label to the lists
article_type.append('G')  # group label
article_title.append(optgroup['label'])
article_href.append('')
article_oncc_href.append('')
for option in optgroup.findAll('option'):
        # Add oncc link for each article for later use of scrape_article
        oncc_href = option['value']
        article_oncc_href.append(oncc_href)
        # Add article to the list variables
        article_type.append('A')  # article
        article_title.append(option.text)
        i = option['value'].rfind('/')  # Search last '/' char to get the article Id
        article_href.append(option['value'][i+1:] + ".html")

# Create output folder <yymmdd>
folder = project_path + '/' + time.strftime('%Y%m%d')
if not os.path.exists(folder):
    os.makedirs(folder)
    Log('Folder ' + folder + ' created.')

# Using jinja to create html page from extracted data
templateLoader = FileSystemLoader( searchpath=project_path)
env = Environment( loader=templateLoader )
env.globals.update(zip=zip)  #to use zip which can iterate 2 lists
TEMPLATE_FILE = 'tmpl_index.html'
template = env.get_template( TEMPLATE_FILE )
newsdate = time.strftime('%d-%m-%Y') + ' ~ ' + WeekdayInChinese(time.strftime('%a'))
#output = template.render(newsdate=newsdate, types=article_type, titles=article_title, hrefs=article_href, head_img_url=head_img_url)
# Changed on 15.4.2019
# Since, Apple Daily requires user to login to see the article,
# when the article link in the index page is clicked, go to the Apple Daily page. 
#output = template.render(newsdate=newsdate, types=article_type, titles=article_title, hrefs=article_href)
output = template.render(newsdate=newsdate, types=article_type, titles=article_title, hrefs=article_oncc_href)
#print(output.encode('utf-8'))
filename = os.path.join(folder, html_file)
with open(filename, 'w', encoding='utf-8') as f:
    f.write(output)
    Log(filename + ' saved.')
f.close()

# Delete yesterday folder <yymmdd - 1>
yday = datetime.today() - timedelta(days=1)
yfolder = project_path + '/' + yday.strftime('%Y%m%d')
if os.path.exists(yfolder):
    shutil.rmtree(yfolder, ignore_errors=True)
    Log('Folder ' + yfolder + ' deleted.')
else:
    Log('Folder ' + yfolder + ' not exists.')

# Commented on 12.4.2019: Need login Apple Daily to see each article
# Loop to scrape each article
#for t, h in zip(article_type, article_oncc_href):
#    if t == 'A':
#        print(h)
        # Call scrape_article.py
#        cmd = 'python scrape_article.py ' + h  # for windows
#        cmd = 'python3 ' + project_path + '/scrape_article.py ' + h  # for RPi
#        os.system(cmd)

Log('End of scrape_index.')
