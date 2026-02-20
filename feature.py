# feature_extraction.py

import re
import urllib.request
from bs4 import BeautifulSoup
from googlesearch import search
import whois
from datetime import date
from urllib.parse import urlparse

class FeatureExtraction:
    def __init__(self, url):
        self.url = url
        self.domain = ""
        self.whois_response = None
        self.urlparse_obj = None
        self.response = None
        self.soup = None

        # fetch page + parse
        try:
            import requests
            self.response = requests.get(url, timeout=10)
            self.soup = BeautifulSoup(self.response.text, 'html.parser')
        except:
            pass

        # parse domain
        try:
            self.urlparse_obj = urlparse(url)
            self.domain = self.urlparse_obj.netloc
        except:
            pass

        # whois lookup
        try:
            self.whois_response = whois.whois(self.domain)
        except:
            pass

    def prefixSuffix(self):
        try: return -1 if '-' in self.domain else 1
        except: return -1

    def SubDomains(self):
        c = self.domain.count('.')
        return 1 if c==1 else 0 if c==2 else -1

    def HTTPS(self):
        """
        Returns:
          1  if the site is reachable **and** uses HTTPS
         -1  if the site is unreachable **or** does not use HTTPS
        """
        try:
            # First, reject non-HTTPS URLs outright
            if self.urlparse_obj.scheme != 'https':
                return -1

            # Then verify the site actually responds with a 2xx status
            import requests
            resp = requests.get(self.url, timeout=10)
            return 1 if 200 <= resp.status_code < 300 else -1

        except Exception:
            return -1

    def DomainRegLen(self):
        try:
            exp, crt = self.whois_response.expiration_date, self.whois_response.creation_date
            if isinstance(exp, list): exp=exp[0]
            if isinstance(crt, list): crt=crt[0]
            m = (exp.year-crt.year)*12 + (exp.month-crt.month)
            return 1 if m>=12 else -1
        except: return -1

    def AnchorURL(self):
        try:
            total=unsafe=0
            for a in self.soup.find_all('a', href=True):
                h=a['href'].lower()
                cond = ('#' in h or 'javascript' in h or 'mailto' in h or 
                        not (self.url in h or self.domain in h))
                unsafe += cond
                total += 1
            p = unsafe/total*100 if total else 0
            return 1 if p<20 else 0 if p<40 else -1
        except: return -1

    def LinksInScriptTags(self):
        try:
            tot=succ=0
            for tag in self.soup.find_all(['link','script'], href=True, src=True):
                src = tag.get('src') or tag.get('href')
                succ += (self.url in src or self.domain in src or src.count('.')==1)
                tot += 1
            p=succ/tot*100 if tot else 0
            return 1 if p<17 else 0 if p<81 else -1
        except: return -1

    def ServerFormHandler(self):
        try:
            forms=self.soup.find_all('form', action=True)
            if not forms: return 1
            for f in forms:
                a=f['action']
                if a in ("","about:blank"): return -1
                if self.url not in a and self.domain not in a: return 0
            return 1
        except: return -1

    def WebsiteTraffic(self):
        try:
            xml = urllib.request.urlopen(
                "http://data.alexa.com/data?cli=10&dat=s&url="+self.url
            ).read()
            r=int(BeautifulSoup(xml,"xml").find("REACH")['RANK'])
            return 1 if r<100000 else 0
        except: return -1

    def GoogleIndex(self):
        try: return 1 if list(search(self.url, num_results=5)) else -1
        except: return 1

    def LinksPointingToPage(self):
        try:
            cnt=len(re.findall(r"<a href=", self.response.text or ""))
            return 1 if cnt==0 else 0 if cnt<=2 else -1
        except: return -1

    def getFeaturesList(self):
        return [
            self.prefixSuffix(), self.SubDomains(), self.HTTPS(),  # Updated method name
            self.DomainRegLen(), self.AnchorURL(), self.LinksInScriptTags(),
            self.ServerFormHandler(), self.WebsiteTraffic(),
            self.GoogleIndex(), self.LinksPointingToPage()
        ]