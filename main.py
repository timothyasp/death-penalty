import re, sys, os, errno
import imghdr
import pprint
import simplejson as json
import urllib2
import jsontemplate
from bs4 import BeautifulSoup

download_dir = "/Users/tasp/Dropbox/Personal/Data/TexasDeathPenalty/"

baseurl = "http://www.tdcj.state.tx.us/death_row"
pagetype = ".html"
basepage = "/dr_executed_offenders"+pagetype

def buildPageUrl(page):
    return baseurl + page

def buildOffenderInfo(link):
    obj= {}

    linksoup = BeautifulSoup(urllib2.urlopen(link))

    if linksoup != None:
        tags = linksoup.find('body').find_all('tr')

        if tags != None:
            for tag in tags:
                cols = tag.find_all('td')
                obj[str(cols[-2].string)] = str(cols[-1].string).strip()

            extra_data_cols = linksoup.select('span.text_bold')
            for edcol in extra_data_cols:
                # Grab the value for each of these extra fields describing the execution
                value = edcol.parent.contents[-1].strip()
                obj[edcol.string.strip()] = value

    return obj

def buildStatementData(link):
    linksoup = BeautifulSoup(urllib2.urlopen(link))
    if linksoup != None:
        obj = {}
        for p in linksoup.find_all('p', { 'class' : 'text_bold' }):
            key_name = str(p.string).strip()
            key = key_name.replace(":", "")
            value = p.next_sibling.next_element.string
            obj[key] = value

    return obj

def downloadImage(subdir, url):
    # Grab filename from path
    filename = re.search(r"""[^/]+$""", str(url)).group(0)

    image_url = buildPageUrl(url)

    req = urllib2.Request(image_url)
    req.add_header('Referer', baseurl)

    response = urllib2.urlopen(req)

    directory = download_dir + subdir 
    if not os.path.exists(directory):
        os.makedirs(directory)

    filepath = directory + '/' + filename
    if not os.path.isfile(filepath):
        output = open(filepath, 'wb')
        output.write(response.read())
        output.close()

def grabImageFromUrl(link):
    obj = {}
    obj['filename'] = re.search(r"""[^/]+$""", str(link)).group(0)

    downloadImage('offender_info', link) 

    return obj

def main():

    saved = sys.stdout
    f = file(download_dir + 'texas_executions.json', 'wb')
    fmin = file(download_dir + 'texas_executions.min.json', 'w')
    sys.stdout = f

    data = {"executions": []} 

    soup = BeautifulSoup(urllib2.urlopen(buildPageUrl(basepage)))

    columns = [ "id", "offender_extended_information", "last_statement", "last_name", "first_name", "tdcj_number", "age", "date", "race", "county" ]
    rows = soup.find(id="body").find_all('tr')
    
    for row in rows[1:]:
        datacol = {} 
        i = 0
        for col in row.find_all('td'):
            if col.string == None or col.string == 'Offender Information' or col.string == 'Last Statement':
                link_text = str(col.a.string).strip()
                if link_text == 'Offender Information':
                    href = col.a['href']

                    rel_url = "/" + href
                    if href.endswith(".html"):
                        link = buildPageUrl(rel_url)
                        datacol[columns[i]] = buildOffenderInfo(link)
                    else:
                        datacol[columns[i]] = grabImageFromUrl(rel_url)

                elif link_text == 'Last Statement':
                    link = buildPageUrl("/"+str(col.a['href']))
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
