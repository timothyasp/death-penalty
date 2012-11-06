import re, sys, os, errno
import pprint
import simplejson as json
import urllib2
from bs4 import BeautifulSoup

download_dir = "/Users/tasp/Dropbox/Personal/Photos/Mars/"

baseurl = "http://www.tdcj.state.tx.us/death_row"
pagetype = ".html"
basepage = "/dr_executed_offenders"+pagetype

class Scrape:
    def __init__(self, url):
        self.url = url
        self.soup = BeautifulSoup(urllib2.urlopen(url))

def buildPageUrl(page):
    return baseurl + page

def buildOffenderInfo(link):
    linksoup = BeautifulSoup(urllib2.urlopen(link))
    tags = linksoup.find('body').find_all('tr')

    obj= {}
    for tag in tags:
        cols = tag.find_all('td')
        obj[str(cols[-2].string)] = str(cols[-1].string).strip()

    extra_data_cols = linksoup.select('span.text_bold')
    for edcol in extra_data_cols:
        # Grab the value for each of these extra fields describing the execution
        value = edcol.parent.contents[-1].strip()
        obj[str(edcol.string).strip()] = str(value)

    return obj

def buildStatementData(link):
    linksoup = BeautifulSoup(urllib2.urlopen(link))
    obj = {}
    for p in linksoup.select('p.text_bold'):
        key_name = str(p.string)
        key = key_name.replace(":", "")
        obj[key] = str(p.find_next_sibling().string).strip()

    return obj

def main():

    saved = sys.stdout
    f = file('texas_executions.json', 'wb')
    fmin = file('texas_executions.min.json', 'w')
    sys.stdout = f

    data = {"executions": []} 

    soup = BeautifulSoup(urllib2.urlopen(buildPageUrl(basepage)))

    columns = [ "id", "offender_extended_information", "last_statement", "last_name", "first_name", "tdcj_number", "age", "date", "race", "county" ]
    rows = soup.find(id="body").find_all('tr')
    
    for row in rows[1:]:
        datacol = {} 
        i = 0
        for col in row.find_all('td'):
            if col.string == None:
                if col.a.string == 'Offender Information':
                    link = buildPageUrl("/"+col.a['href'])
                    datacol[columns[i]] = buildOffenderInfo(link)
                elif col.a.string == 'Last Statement':
                    link = buildPageUrl("/"+col.a['href'])
                    datacol[columns[i]] = buildStatementData(link)

            else: 
                datacol[columns[i]] = col.string

            i+=1

        data['executions'].append(datacol)

    print json.dumps(data, sort_keys=True, indent=4)
    fmin.write(json.dumps(data))
    sys.stdout = saved
    f.close()
    fmin.close()
    print "Collection finished"

if __name__ == '__main__':
    main()
