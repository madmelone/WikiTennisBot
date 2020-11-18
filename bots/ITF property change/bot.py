#!/usr/bin/env python3
# Name:     ITF property change
# Author:   Mad_melone (https://w.wiki/gDR)
# Date:     07-11-2020
# Content:  Changes the ITF profile information from the old url  (P599) to the new url  (P|8618) in Wikidata

# Imports
import pywikibot
from SPARQLWrapper import SPARQLWrapper, JSON
from selenium import webdriver
import json
from datetime import datetime
import os

class ITFProperty(object):
    # Object that contains and edits ITF player information
    def __init__(self, action="test"):
        # Self method
        self.__action = action
        self.__itemlist = {}
        self.__endpoint_url = "https://query.wikidata.org/sparql"
        self.__useragent = "wikitennisbot/0.1 (https://wikitennisbot.toolforge.org)"
        self.__now = str(datetime.now().strftime("%Y%d%m_%H-%M-%S"))

    def getItems(self):
        # Method that returns all players with a value in P599 that needs to be updated
        # Query Wikidata SPARQL (no Limit if live, Limit = 3 for tests)
        if self.__action == "live":
            query = """SELECT
                      ?item ?itemLabel ?itf_old ?itf_new
                    WHERE 
                    {
                      ?item wdt:P599 ?itf_old
                      SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
                      OPTIONAL { ?item wdt: P8618 ?itf_new.}
                    
                    }"""
        else:
            query = """SELECT
                      ?item ?itemLabel ?itf_old ?itf_new
                    WHERE 
                    {
                      ?item wdt:P599 ?itf_old
                      SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
                      OPTIONAL { ?item wdt: P8618 ?itf_new.}
                    }
                    LIMIT 3"""
        sparql = SPARQLWrapper(self.__endpoint_url, self.__useragent)
        sparql.setMethod('POST')
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        dic = results["results"]["bindings"]
        # Initiate Selenium a
        driver = webdriver.Chrome()
        driver.get("https://www.itftennis.com/")
        # Iterate over SPARQL results and create result dictionary
        for i in range(len(dic)):
            item = dic[i]["item"]["value"].split('entity/')[1]
            itemlabel = dic[i]["itemLabel"]["value"]
            itf_old = dic[i]["itf_old"]["value"]
            url = "https://www.itftennis.com/procircuit/players/player/profile.aspx?playerid=" + itf_old
            driver.get(url)
            itf_new = driver.current_url.split("players/")[1][:-15]
            self.__itemlist[i] = {"item": item, "itemlabel": itemlabel, "itf_old": itf_old, "itf_new": itf_new}
            # Print progress to console
            print(str(i+1) + "/" + str(len(dic)))
        driver.quit()
        # Write into file and create backup if already exists
        if os.path.exists("items.txt"):
            os.rename("items.txt", "items_backup_" + self.__now + ".txt")
        with open("items.txt", "w") as outfile:
            json.dump(self.__itemlist, outfile)
        return self.__itemlist
    
    def cleanItems(self):
        # Method that cleans up the items for errorneous IDs and creates a error.txt
        error_data = {}
        driver = webdriver.Chrome()
        driver.get("https://www.itftennis.com/")
        # Identify errors and write to
        with open("items.txt") as item_file:
            item_data = json.load(item_file)
            for p in item_data:
                if "aspx?" in item_data[p]["itf_new"]:
                    itf_new = ""
                    url = "https://www.itftennis.com/procircuit/players/player/profile.aspx?playerid=" + \
                          item_data[p]["itf_old"]
                    driver.get(url)
                    itf_new = driver.current_url.split("players/")[1][:-15]
                    # If "aspx?" is in the url this means an errorneous itf_old
                    if "aspx?" in itf_new:
                        error_data[p] = item_data[p]
                    else:
                        item_data[p]["itf_new"] = itf_new
        # Delete errorneous IDs from items
        item_set = set(item_data)
        error_set = set(error_data)
        error_items = item_set.intersection(error_set)
        for item in error_items:
            del item_data[item]
        # Write updated items.txt after backup and new error.txt
        if os.path.exists("items.txt"):
            os.rename("items.txt", "items_backup_" + self.__now + ".txt")
        with open("items.txt", "w") as item_file:
            json.dump(item_data, item_file)
        with open("error.txt", "w") as error_file:
            json.dump(error_data, error_file)

    def updateWikidata(self):
        # Method that updates the wikidata items
        # Login bot to Wikidata
        log = []
        if self.__action == "live":
            wiki = pywikibot.Site("wikidata", "wikidata")
        else:
            wiki = pywikibot.Site("test", "wikidata")
        wiki.login()
        repo = wiki.data_repository()
        # Get item information
        with open("items.txt") as item_file:
            item_data = json.load(item_file)
            for i in item_data:
                print(i + " - " + item_data[i]["item"])
                item = pywikibot.ItemPage(repo, item_data[i]["item"])
                item.get()
                # Bug fix: remove trailing "/"
                if item_data[i]["itf_new"][-1:] == "/":
                    item_data[i]["itf_new"] = item_data[i]["itf_new"][:-1]
                if item.claims:
                    #if "P599" in item.claims:
                    #    if item_data[i]["itf_old"] == item.claims["P599"][0].getTarget():
                    #        # Set P599 statement deprecated if not already
                    #        claim = pywikibot.Claim(repo, "P599")
                    #        if not claim.getRank() == "deprecated":
                    #            print(claim.getRank())
                    #            claim.changeRank("deprecated")
                    #            log.append("{{Q|" + item_data[i]["item"][1:] + "}} - deprecate P599")
                    #        else:
                    #            log.append("{{Q|" + item_data[i]["item"][1:] + "}} - no deprecate P599")
                    if not "P8618" in item.claims:
                        # Add new P8618 statement if not already available
                        claim = pywikibot.Claim(repo, "P8618")
                        target = item_data[i]["itf_new"]
                        claim.setTarget(target)
                        item.addClaim(claim, summary="Add ITF Player ID 2020 (P8618)")
                        log.append("{{Q|" + item_data[i]["item"][1:] + "}} - add P8618")
                    else:
                        if item.claims["P8618"][0].getTarget() != item_data[i]["itf_new"]:
                            # Update P8618 statement if not the same as from web scraping
                            # 1) Delete existing statements 2) Add new statement
                            for claim in item.claims["P8618"]:
                                item.removeClaims(claim, summary="Removing incorrect ITF Player ID 2020 (P8618)")
                            claim = pywikibot.Claim(repo, "P8618")
                            target = item_data[i]["itf_new"]
                            claim.setTarget(target)
                            item.addClaim(claim, summary="Update ITF Player ID 2020 (P8618)")
                            log.append("{{Q|" + item_data[i]["item"][1:] + "}} - update P8618")
                        else:
                            pass
                            #log.append("{{Q|" + item_data[i]["item"][1:] + "}} - no update P8618")
        # Write log
        self.__botuser = "User:" + wiki.user()
        instance = str(self.__now) + " ITF Property Change"
        page = pywikibot.Page(wiki, self.__botuser + "/log/" + instance)
        heading = "== Log for bot run on " + str(self.__now) + " ==\n\n\n* "
        content = "\n* ".join(log)
        page.text = heading + content
        page.save("Log update by " + wiki.user())

        overviewurl = "User:WikiTennisBot/log"
        page = pywikibot.Page(wiki, overviewurl)
        text = "* [[User:WikiTennisBot/log/" + instance + "]] \n" + page.get()
        page.text = str(text)
        page.save("Log update by " + wiki.user())

    # Access of private variables
    itemlist = property(getItems)

# Testing environment
if __name__ == '__main__':
    update = ITFProperty(action="live")
    #update.getItems()
    #update.cleanItems()
    update.updateWikidata()
