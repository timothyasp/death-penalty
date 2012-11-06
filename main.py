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

def cleanTitle(title):
    return re.sub(r'&[^\s]*;', '', title)

def downloadImage(subdir, imgdir, url):
    filename = re.search(r"""[^/]+$""", str(url)).group(0)
    print "Downloading " + filename + "....."

    req = urllib2.Request(baseurl + url)
    req.add_header('Referer', baseurl)

    response = urllib2.urlopen(req)

    directory = download_dir + subdir 
    if not os.path.exists(directory):
        os.makedirs(directory)

    imgdir = directory + '/' + re.sub(' ', '-', imgdir)
    if not os.path.exists(imgdir):
        os.makedirs(imgdir)

    filepath = imgdir + '/' + filename
    if not os.path.isfile(filepath):
        print "Saving to " + filepath
        output = open(filepath, 'wb')
        output.write(response.read())
        output.close()
    else:
        print "Already downloaded, skipping"

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
        obj[str(p.string).strip()] = p.find_next_sibling().string

    return obj

def main():

    data = []

    soup = BeautifulSoup(urllib2.urlopen(buildPageUrl(basepage)))

    rows = soup.find(id="body").find_all('tr')

    columns = [ "Execution", "Offender", "Last Statement", "Last Name", "First Name", "TDCJ Number", "41", "Date", "Race", "County" ]
    
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

        jsondata = json.dumps(datacol)
        data.append(jsondata)

    print data

if __name__ == '__main__':
    main()
