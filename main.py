#EmailScraper
#Written: 18.04.2018
#Author: My. Ozerov
import re
import codecs
import requests
import xml.etree.cElementTree as ET
from xml.dom import minidom

from bs4 import BeautifulSoup

def xml_parser(input):
    url_set = set()
    tree = ET.parse(input)
    root = tree.getroot()
    for site in root.findall('site'):
        url_set.add(site.find('url').text)
    return url_set

def get_emails(string):
    match = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', string)
    return set(match)

def write_to_file(output, emails):
    data = ET.Element('data')
    for email in emails:
        item = ET.SubElement(data, 'email')
        item.text = email
    xmlstr = minidom.parseString(ET.tostring(data)).toprettyxml(indent="   ")
    with codecs.open(output, 'w', 'utf-8') as f:
        f.write(xmlstr)

def html_parser(url_set, emails, n, depth):
    if (n >= depth):
        return
    links = set()
    for url in url_set:
        curr_links = set()
        curr_emails = set()
        print('Working with', url)
        try:
            html_doc = requests.get(url)
            soup = BeautifulSoup(html_doc.content, 'html.parser')
            for link in soup.findAll('a', {'href': re.compile("^http://")}):
                curr_links.add(link.get('href'))
            print('Links list:', curr_links)
            curr_emails = get_emails(soup.prettify())
            print('Emails list:', curr_emails)
            emails.update(curr_emails)
            links.update(curr_links)
        except requests.exceptions.RequestException as e:
            print(e)
    html_parser(links, emails, n + 1, depth)

emails = set()
depth = 2
xml_input = 'input.xml'
xml_output = 'output.xml'
url_set = xml_parser(xml_input)

html_parser(url_set, emails, 0, depth)
print(len(emails), 'total emails found\n', emails)

write_to_file(xml_output, emails)