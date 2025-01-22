#!/opt/homebrew/bin/python3.11

from bs4 import BeautifulSoup
import urllib.request as hyperlink

link = hyperlink.urlopen('http://plugins.svn.wordpress.org/')
wordPressSoup = BeautifulSoup(link,'lxml')
with open('wordpresPlugins-all.txt', 'wt', encoding='utf8') as file:
        file.write(wordPressSoup.text)
