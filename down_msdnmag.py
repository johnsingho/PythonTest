"""
@author: johnsing
@time:2019/09/29
@File: down_msdnmag.py
"""
import sys
import re
import time
import os
import shutil
from datetime import datetime

import bs4
from bs4 import BeautifulSoup

# urllib2
# https://stackoverflow.com/questions/2792650/import-error-no-module-name-urllib2
# 基本就是将urllib2.xxx修改为urllib.request.xxx
from urllib.request import urlopen



######################################

def make_dir(sdir):
    dirname = os.path.dirname(__file__)
    longdir = os.path.join(dirname, sdir)
    if not os.path.exists(longdir):
        os.makedirs(longdir)

def make_filename(sdir, sfn):
    dirname = os.path.dirname(__file__)
    longdir = os.path.join(dirname, sdir, sfn)
    return longdir

def download_file(sdir, slink):
    sfn='unknown'
    rmat = re.search(r"/([^/]+(?:pdf|chm))$", slink, re.I)
    if rmat:
        sfn = rmat.groups()[0]
    fpath = make_filename(sdir, sfn)
    #print('filepath: ' + fpath)
    #check before download
    if os.path.exists(fpath):
        return
    try:
        with urlopen(slink) as response, open(fpath, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)   
        print('Finish: '+sfn)
    except OSError as err:
        print("OS error: {0}".format(err))
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise

# decode html, down file
def do_down(surl):
    html=urlopen(surl).read()
    content = BeautifulSoup(html, 'html.parser')

    #this year    
    sYear=datetime.now().strftime('%Y')
    print('Year: ' + sYear)
    make_dir(sYear)
    for mag_link in content.select('div.issueBlock div.issueTxt p>a[href]'):
        slink = mag_link.get('href') 
        if re.search('\.pdf$|\.chm$', slink, re.I):
            download_file(sYear, slink)
    print('Handle ' + sYear + 'ok')


    #用于之前年份
    divMags = content.find(name='div',attrs={'class':'MagazineStyle mag'})
    #2009~
    divOld = divMags.find(name='div',attrs={'class':'row bottomspace'})
    for divc in divOld.children:
        #跳过NavigableString结点
        if not isinstance(divc, bs4.element.Tag):
            continue
        divYear = divc.select('h2 > a')
        sYear = divYear[0].string
        print('Year: ' + sYear)
        make_dir(sYear)
        for mag_link in divc.select('li > a[href]'):
            slink = mag_link.get('href') 
            if re.search('\.pdf$|\.chm$', slink, re.I):
                download_file(sYear, slink)
    print('Handle 2009~ ok')

    #~2009
    divOld2009 = divMags.find(name='div',attrs={'class':'aside'})
    #根据页面结构，aside的下一个就是    
    while divOld2009:
        divOld2009 = divOld2009.next_sibling
        if isinstance(divOld2009, bs4.element.Tag):
            break

    #print(type(divOld2009))
    for divc in divOld2009.children:
        #跳过NavigableString结点
        if not isinstance(divc, bs4.element.Tag):
            continue
        divYear = divc.select('h2 > a')
        sYear = divYear[0].string
        print('Year: ' + sYear)
        make_dir(sYear)
        for mag_link in divc.select('div > a[href]'):
            slink = mag_link.get('href') 
            if re.search('\.pdf$|\.chm$', slink, re.I):
                download_file(sYear, slink)
    print('Handle ~2009 ok')
            

##
if __name__ == '__main__':
    surl = 'https://msdn.microsoft.com/en-us/magazine/msdn-magazine-issues.aspx'
    do_down(surl)
    print('done.')



