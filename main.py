# -*- coding: utf-8 -*-
import sys
import time, os
from jinja2 import Environment, FileSystemLoader
from datetime import datetime, timedelta
import shutil

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

Log('Apple Daily: main starts...')

# Define project home path
#project_path = '.'  # for Windows or RPi interactive
project_path = '/home/pi/Projects/appledaily'  # for RPi cron job

# Create output folder <yymmdd>
folder = project_path + '/' + time.strftime('%Y%m%d')
if not os.path.exists(folder):
    os.makedirs(folder)
    Log('Folder ' + folder + ' created.')


# Using jinja to create main html page
topic_id=['2', '1']
index_title=['要聞港聞', '財經地產']
index_href=['main_index.html', 'finance_index.html']
templateLoader = FileSystemLoader( searchpath=project_path )
env = Environment( loader=templateLoader )
env.globals.update(zip=zip)  #to use zip which can iterate 2 lists
TEMPLATE_FILE = 'tmpl_main.html'
template = env.get_template( TEMPLATE_FILE )
newsdate = time.strftime('%d-%m-%Y') + ' ~ ' + WeekdayInChinese(time.strftime('%a'))
#output = template.render(newsdate=newsdate, types=article_type, titles=article_title, hrefs=article_href, head_img_url=head_img_url)
output = template.render(newsdate=newsdate, titles=index_title, hrefs=index_href)
#print(output)
filename = os.path.join(folder, 'index.html')
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

# Loop to scrape each topic ID
for id in topic_id:
  print('topic_id='+id)
#  cmd = 'python scrape_index.py ' + id  # for windows
  cmd = 'python3 ' + project_path + '/scrape_index.py ' + id  # for RPi
  os.system(cmd)

Log('End of main.')
