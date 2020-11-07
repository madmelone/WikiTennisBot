# Name:     Wiki editor
# Author:   Mad_melone (https://w.wiki/gDR)
# Date:     24-10-2020
# Content:  Edits wiki code in various Wikipedia languages and Wikidata

# External imports
import pywikibot
# Internal imports
from Classes.webscrape import Playerinfo
from Classes.wikicode import Infobox


class Wikicode(object):
    # Object that edits wiki code in Wikipedia and Wikidata
    # Public methods: getLanguage, getSite, editWiki

    def __init__(self, action, playerid, org="atp", language="de", site="wikipedia"):
        # Self method
        # action    = action used to edit, includes createInfoxbox, updateInfobox
        # playerid  = identifier used by the respective org on their website to identify players
        # org       = professional tennis organisation, includes atp, wta, itf
        # language  = wikipedia language code for the site to be edited
        # site      = wikipedia site to be edit, includes wikipedia, wikidata
        self.__action = action
        self.__playerid = playerid
        self.__org = org
        self.__language = language
        self.__site = site

    def getPlayerID(self):
        # Method that returns the private playerid as public
        return self.__playerid

    def getOrg(self):
        # Method that returns the private org as public
        return self.__org

    def getLanguage(self):
        # Method that returns the private language as public
        return self.__language

    def getSite(self):
        # Method that returns the private site as public
        return self.__site

    def createWiki(self):
        # Method that selects whether Wikipedia or Wikidata is to be edited
        if self.__action == "createInfobox":
            self.__savedurl = self.createInfobox()
        elif self.__action == "updateInfobox":
            self.__savedurl = self.updateInfobox()
        else:
            self.__savedurl = "error"
        return self.__savedurl

    def createInfobox(self):
        # Method that creates a new infobox and saves it to the bot userspace in the chosen Wikipedia
        # Build info for bot
        self.__infolist = Playerinfo(playerid=self.__playerid, org=self.__org).infolist
        self.__wdinfo = Playerinfo(playerid=self.__playerid, org=self.__org).wdinfo
        self.__infobox = Infobox(infolist=self.__infolist, wdinfo=self.__wdinfo, language=self.__language,
                                 site=self.site).createInfobox()
        # Login bot to Wikipedia
        wiki = pywikibot.Site(code=self.__language, fam=self.__site)
        wiki.login()
        # Prepare bot edit
        if self.__language == "de":
            self.__botuser = "Benutzer:" + wiki.user()
        elif self.__language == "en":
            self.__botuser = "User:" + wiki.user()
        else:
            pass
        self.__savedurl = self.__botuser + "/PlayerInfobox/(create) " + self.__infolist["updated"] + " " + self.__wdinfo["sitelabel"]
        # Edit page
        page = pywikibot.Page(wiki, self.__savedurl)
        page.text = self.__infobox
        page.save("(Manual test edit) New site by " + wiki.user())
        # Include in overview page
        overviewurl = self.__botuser + "/PlayerInfobox"
        page = pywikibot.Page(wiki, overviewurl)
        text = "* [[" + self.__savedurl + "|(create) " + self.__infolist["updated"] + " " + self.__wdinfo["sitelabel"] + "]] \n" + page.get()
        page.text = str(text)
        page.save("(Manual test edit) Add Infobox (create) " + self.__infolist["updated"] + " " + self.__wdinfo["sitelabel"] + "by" + wiki.user())
        self.__savedurl = "https://" + self.__language + ".wikipedia.org/wiki/" + self.__savedurl
        return self.__savedurl

    def updateInfobox(self):
        # Method that creates a new infobox and saves it to the bot userspace in the chosen Wikipedia
        # Build info for bot
        self.__infolist = Playerinfo(playerid=self.__playerid, org=self.__org).infolist
        self.__wdinfo = Playerinfo(playerid=self.__playerid, org=self.__org).wdinfo
        self.__infobox = Infobox(infolist=self.__infolist, wdinfo=self.__wdinfo, language=self.__language,
                                 site=self.site).updateInfobox()
        # Login bot to Wikipedia
        wiki = pywikibot.Site(code=self.__language, fam=self.__site)
        wiki.login()
        # Prepare bot edit
        if self.__language == "de":
            self.__botuser = "Benutzer:" + wiki.user()
        elif self.__language == "en":
            self.__botuser = "User:" + wiki.user()
        else:
            pass
        self.__savedurl = self.__botuser + "/PlayerInfobox/(update) " + self.__infolist["updated"] + " " + self.__wdinfo["sitelabel"]
        # Edit page
        page = pywikibot.Page(wiki, self.__savedurl)
        page.text = self.__infobox
        page.save("(Manual test edit) New site by " + wiki.user())
        # Include in overview page
        overviewurl = self.__botuser + "/PlayerInfobox"
        page = pywikibot.Page(wiki, overviewurl)
        text = "* [[" + self.__savedurl + "|(update) " + self.__infolist["updated"] + " " + self.__wdinfo["sitelabel"] + "]] \n" + page.get()
        page.text = str(text)
        page.save("(Manual test edit) Add Infobox (update) " + self.__infolist["updated"] + " " + self.__wdinfo["sitelabel"] + "by" + wiki.user())
        self.__savedurl = "https://" + self.__language + ".wikipedia.org/wiki/" + self.__savedurl
        return self.__savedurl

    def createWD(self):
        # Method that edits Wikidata
        self.__savedurl = "wikidata"
        return self.__savedurl

    # Access of private variables
    playerid = property(getPlayerID)
    org = property(getOrg)
    language = property(getLanguage)
    site = property(getSite)
    savedurl = property(createWiki)

# Testing environment
if __name__ == '__main__':
    a = Wikicode(action="createInfobox", playerid="MC10", org="atp", language="de", site="wikipedia")
    print(a.savedurl)