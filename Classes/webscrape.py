# Name:     Website scraper
# Author:   Mad_melone (https://w.wiki/gDR)
# Date:     18-10-2020
# Content:  Scrapes various tennis website for player information

# External imports
import urllib

from bs4 import BeautifulSoup
import cloudscraper

class Playerinfo(object):
    # Object that contains the player information scraped from the ATP website
    # Public methods: getPlayerID, getInfolist, getOrg

    def __init__(self, playerid, org="atp", language="de"):
        # Self method
        # playerid  = identifier for the relevant websites from which data is obtained, e.g. N409 for Rafael Nadal on ATP
        # org       = abbreviation of the website from which data is obtained, includes atp (possibly wta, itf)
        # language  = Wikimedia language code
        self.__playerid = playerid.upper()
        self.__org = org
        self.__language = language

    def getPlayerID(self):
        # Method that returns the private playerid as public
        return self.__playerid

    def getOrg(self):
        # Method that returns the private org as public
        return self.__org

    def getLanguage(self):
        # Method that returns the private language as public
        return self.__language

    def getInfolist(self):
        # Method that selects the website to be scraped and returns the private infolist as public
        if self.__org == "atp":
            self.__infolist = self.scrapeATPInfo()
        else:
            self.__infolist = ["1", "2", "3"]
        return self.__infolist

    def getWDinfo(self):
        # Method that returns the private wdinfo as public
        self.__wdinfo = self.scrapeWikidata()
        return self.__wdinfo

    def scrapeATPInfo(self):
        # Method that scrapes the ATP website for playerinfo and returns as an unformated list
        # Load URL
        url = "https://www.atptour.com/en/players/-/" + self.__playerid + "/overview"
        scraper = cloudscraper.create_scraper()
        html = scraper.get(url).content
        soup = BeautifulSoup(html, "html.parser")
        # Find and save playerinfo
        # Firstname [text] (and find start point for scraping)
        start = soup.find("div", {"class": "first-name"})
        firstname = start.contents[0].strip()
        # Lastname [text]
        lastname = start.findNext("div", {"class": "last-name"}).contents[0].strip()
        # Countrycode [three digit code] (as basis for different templates/variations of the country)
        countrycode = start.findNext("div", {"class": "player-flag-code"}).contents[0].strip()
        # Website [text]
        try:
            website = start.findNext("a", {"class": "official-website-link external"}).attrs['href'].strip()
        except:
            website =""
        # Birthday [date:YYYY-MM-DD]
        position = start.findNext("span", {"class": "table-birthday"})
        birthday = position.contents[0].strip().replace(".","-")[1:-1]
        # Turned pro [date:YYYY]
        turnedpro = position.findNext("div", {"class": "table-big-value"}).contents[0].strip()
        # Weight [integer] (in kg without the unit)
        weight = position.findNext("span", {"class": "table-weight-kg-wrapper"}).contents[0].strip()[1:-3]
        # Height [integer] (in cm without the unit)
        height = position.findNext("span", {"class": "table-height-cm-wrapper"}).contents[0].strip()[1:-3]
        # Birthplace [text]
        position = position.findNext("tr").findNext("div", {"class": "table-value"})
        birthplace = position.contents[0].strip()
        # Residence [text]
        position = position.findNext("div", {"class": "table-value"})
        residence = position.contents[0].strip()
        # Playhand and backhand [text]
        position = position.findNext("div", {"class": "table-value"})
        plays = position.contents[0].split(",")
        playhand = plays[0].strip()
        backhand = plays[1].strip()
        # Coach [list of text]
        position = position.findNext("div", {"class": "table-value"})
        coach = position.contents[0].strip().split(", ")
        # Updated [YYYY-MM-DD]
        position = position.findNext("h2", {"class": "module-title"})
        updated = position.contents[0].strip().replace(".","-")[-10:]
        # Current ranking positions [text]
        position = position.findNext("td", {"class": "overview-year"}).findNext("div", {"class": "stat-value"})
        singlesranking = position.attrs['data-singles'].strip()
        if singlesranking == "0":
            singlesranking = ""
        doublesranking = position.attrs['data-doubles'].strip()
        if doublesranking == "0":
            doublesranking = ""
        # All-time ranking positions [text]
        position = position.findNext("tr").findNext("div", {"class": "stat-value"})
        highsinglesranking = position.attrs['data-singles'].strip()
        highdoublesranking = position.attrs['data-doubles'].strip()
        # All-time ranking dates [YYYY-MM-DD]
        position = position.findNext("div", {"class": "label-value"})
        highsinglesrankingdate = position.attrs['data-singles-label'].strip().replace(".","-")[-10:]
        highdoublesrankingdate = position.attrs['data-doubles-label'].strip().replace(".","-")[-10:]
        # Win-loss record [text]
        position = position.findNext("div", {"class": "stat-value"})
        singlesrecord = position.attrs['data-singles'].strip()
        doublesrecord = position.attrs['data-doubles'].strip()
        # Number of titles [int]
        position = position.findNext("div", {"class": "stat-value"})
        singlestitles = position.attrs['data-singles'].strip()
        doublestitles = position.attrs['data-doubles'].strip()
        # Prize money [text in USD and US amount formatting, e.g. 1,234,567
        position = position.findNext("div", {"class": "stat-value"})
        prizemoneytext = position.attrs['data-singles'][1:].strip()
        prizemoney = int(prizemoneytext.replace(",", ""))
        # Return infolist as dictionary
        self.__infolist = {"firstname": firstname, "lastname": lastname, "countrycode":countrycode, "website":website,
                           "birthday": birthday, "turnedpro": turnedpro, "weight":weight, "height":height,
                           "birthplace": birthplace, "residence":residence, "playhand": playhand, "backhand": backhand,
                           "coach": coach, "updated": updated, "singlesranking": singlesranking,
                           "doublesranking": doublesranking, "highsinglesranking": highsinglesranking,
                           "highdoublesranking": highdoublesranking, "highsinglesrankingdate": highsinglesrankingdate,
                           "highdoublesrankingdate": highdoublesrankingdate, "singlesrecord": singlesrecord,
                           "doublesrecord": doublesrecord, "singlestitles": singlestitles,
                           "doublestitles": doublestitles, "prizemoney": prizemoney}
        return self.__infolist

    def scrapeWikidata(self):
        # Method that provides information from Wikidata (lemma, title)
        from SPARQLWrapper import SPARQLWrapper, JSON
        # Set up SPARQL query
        endpoint_url = "https://query.wikidata.org/sparql"
        q = """SELECT DISTINCT ?player ?playerLabel ?PlayerID ?playerlink ?country_code
            WHERE {
            VALUES ?PlayerID { "%s" }
            VALUES ?language_code { "%s" }
            
            # Find the player
            ?player wdt:%s ?PlayerID.
            
            # Find the Wikipedia, its language(s), and sitelink for the Wikipedia
            BIND (URI(CONCAT("https://", ?language_code, ".wikipedia.org/")) AS ?Wikipedia)
            OPTIONAL {
                ?playerlink schema:about ?player.
                ?playerlink schema:isPartOf ?Wikipedia.
            }
            
            # Find player's label in the language(s)
            OPTIONAL {
                VALUES ?language_code { "?language_code" }    # Language code for player label
                ?player rdfs:label ?playerLabel.
                FILTER (LANG(?playerLabel) = ?language_code)
            }

            # Select only statements without an end time
            ?player p:P1532 ?represents_statement.
            ?represents_statement ps:P1532 ?represents.
            FILTER NOT EXISTS { ?represents_statement pq:P582 []. }
            
            SERVICE wikibase:label {
                bd:serviceParam wikibase:language "%s", "en" .
            }
            }"""
        # Adjust query to represent respective Wikidata Property depending on organisation
        if self.__org == 'atp':
            query = q % (self.__playerid, self.__language, 'P536', self.__language)
        elif self.__org == 'wta':
            query = q % (self.__playerid, self.__language, 'P597', self.__language)
        elif self.__org == 'itf':
            query = q % (self.__playerid, self.__language, 'P599', self.__language)
        # Run SPAQRL-query with Agent accorcding to Wikimedia User Agent Policy
        sparql = SPARQLWrapper(endpoint_url,
                               agent='wikitennisbot/0.1 (https://wikitennisbot.toolforge.org)')
        sparql.setMethod('POST')
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        # Return a dictionary of SPARQL results
        dic = results["results"]["bindings"]
        if len(dic) == 0:
            item = ""
            sitelink = ""
            sitelabel =""
        else:
            item = dic[0]["player"]["value"].split('entity/')[1]
            sitelink = urllib.parse.unquote(dic[0]["playerlink"]["value"].split('wiki/')[1])
            sitelabel = dic[0]["playerLabel"]["value"]
        self.__wdinfo = {"item": item, "sitelink": sitelink, "sitelabel": sitelabel}
        return self.__wdinfo

    # Access of private variables
    playerid = property(getPlayerID)
    org = property(getOrg)
    language = property(getLanguage)
    infolist = property(getInfolist)
    wdinfo = property(getWDinfo)

# Testing environment
if __name__ == '__main__':
    a = Playerinfo('E687', "atp", "de")
    print(a.wdinfo)




