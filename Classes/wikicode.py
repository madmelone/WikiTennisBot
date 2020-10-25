# Name:     Wiki code creator
# Author:   Mad_melone (https://w.wiki/gDR)
# Date:     17-10-2020
# Content:  Prepares the wiki code for various Wikipedia languages and Wikidata

# External imports
import mwparserfromhell
from datetime import datetime
import locale
import pywikibot

# Internal imports
from Classes.templatesinfobox import *

class Infobox(object):
    # Object that provides wiki code for info boxes in Wikipedia and Wikidata
    # Public methods: getLanguage, getSite, createTemplate

    def __init__(self, infolist, wdinfo, language="de", site="wikipedia"):
        # Self method
        # infolist  = dictionary of player information, includes firstname, lastname, countrycode, website,
        #             birthday, turnedpro, weight, height, birthplace, residence, playhand, backhand, coach [as list],
        #             updated, singlesranking, doublesranking, highsinglesranking, highdoublesranking,
        #             highsinglesrankingdate, highdoublesrankingdate, singlesrecord, doublesrecord, singlestitles,
        #             doublestitles, prizemoney
        # wdinfo    = dictionary of player information from Wikidata includes item, sitelink, sitelabel
        # language  = wikipedia language code for the site to be edited
        # site      = wikipedia site to be edit, includes wikipedia, wikidata
        self.__infolist = infolist
        self.__wdinfo = wdinfo
        self.__language = language
        self.__site = site

    def getLanguage(self):
        # Method that returns the private language as public
        return self.__language

    def getSite(self):
        # Method that returns the private site as public
        return self.__site

    def createInfobox(self):
        # Method that returns a "fresh" infobox template based on the infolist values
        if self.__language == "de" and self.__site == "wikipedia":
            locale.setlocale(locale.LC_ALL, 'de_DE.utf8')
            template = infobox_dewp
            infobox = mwparserfromhell.parse(template).filter_templates()[0]
            infobox.add("Nationalität", " {{" + self.__infolist["countrycode"] + "}}")
            birthday = datetime.strptime(self.__infolist["birthday"], "%Y-%m-%d")
            infobox.add("Geburtstag", " " + str(birthday.strftime("%#d. %B %Y")) + "<br />({{Alter|" +
                        str(birthday.strftime("%Y")) + "|" + str(birthday.strftime("%#m")) + "|" +
                        str(birthday.strftime("%#d")) + "}} Jahre)")
            infobox.add("Größe", " " + self.__infolist["height"])
            infobox.add("Gewicht", " " + self.__infolist["weight"])
            infobox.add("ErsteProfisaison", " " + self.__infolist["turnedpro"])
            infobox.add("Trainer", " " + ", ".join(self.__infolist["coach"]))
            infobox.add("Preisgeld", " " + str(locale.currency(self.__infolist["prizemoney"], grouping=True)[:-5]))
            infobox.add("EinzelBilanz", " " + self.__infolist["singlesrecord"].replace("-", ":"))
            infobox.add("AnzahlEinzelTitel", " " + self.__infolist["singlestitles"])
            highsinglesrankingdate = datetime.strptime(self.__infolist["highsinglesrankingdate"], "%Y-%m-%d")
            if self.__infolist["highsinglesranking"] == "1":
                infobox.add("HoechsteEinzelPlatzierung", " [[Liste der Weltranglistenersten im Herrentennis (Einzel)|" +
                            self.__infolist["highsinglesranking"] + "]] (" +
                            str(highsinglesrankingdate.strftime("%#d. %B %Y")) + ")")
            else:
                infobox.add("HoechsteEinzelPlatzierung", " " + self.__infolist["highsinglesranking"] + " (" +
                            str(highsinglesrankingdate.strftime("%#d. %B %Y")) + ")")
            infobox.add("AktuelleEinzelPlatzierung", " " + self.__infolist["singlesranking"])
            infobox.add("DoppelBilanz", " " + self.__infolist["doublesrecord"].replace("-", ":"))
            infobox.add("AnzahlDoppelTitel", " " + self.__infolist["doublestitles"])
            highdoublesrankingdate = datetime.strptime(self.__infolist["highdoublesrankingdate"], "%Y-%m-%d")
            if self.__infolist["highdoublesranking"] == "1":
                infobox.add("HoechsteDoppelPlatzierung", " [[Liste der Weltranglistenersten im Herrentennis (Doppel)|" +
                            self.__infolist["highdoublesranking"] + "]] (" +
                            str(highdoublesrankingdate.strftime("%#d. %B %Y")) + ")")
            else:
                infobox.add("HoechsteDoppelPlatzierung", " " + self.__infolist["highdoublesranking"] + " (" +
                            str(highdoublesrankingdate.strftime("%#d. %B %Y")) + ")")
            infobox.add("AktuelleDoppelPlatzierung", " " + self.__infolist["doublesranking"])
            updated = datetime.strptime(self.__infolist["updated"], "%Y-%m-%d")
            infobox.add("Updated", " " + str(updated.strftime("%#d. %B %Y")))
        return infobox

    def updateInfobox(self):
        # Method that returns an updated infobox based on current values
        site = pywikibot.Site(self.__language, self.__site)
        page = pywikibot.Page(site, self.__wdinfo["sitelink"])
        text = mwparserfromhell.parse(page.get())
        # Select template and setlocal based on language
        if self.__language == "de" and self.__site == "wikipedia":
            locale.setlocale(locale.LC_ALL, 'de_DE.utf8')
            template = infobox_dewp
            for infobox in text.filter_templates():
                if infobox.name.matches(mwparserfromhell.parse(template).filter_templates()[0].name):
                    infobox.add("Preisgeld", str(locale.currency(self.__infolist["prizemoney"], grouping=True)[:-5]))
                    infobox.add("EinzelBilanz", self.__infolist["singlesrecord"].replace("-", ":"))
                    infobox.add("AnzahlEinzelTitel", self.__infolist["singlestitles"])
                    highsinglesrankingdate = datetime.strptime(self.__infolist["highsinglesrankingdate"], "%Y-%m-%d")
                    if self.__infolist["highsinglesranking"] == "1":
                        infobox.add("HoechsteEinzelPlatzierung",
                                    "[[Liste der Weltranglistenersten im Herrentennis (Einzel)|" +
                                    self.__infolist["highsinglesranking"] + "]] (" +
                                    str(highsinglesrankingdate.strftime("%#d. %B %Y")) + ")")
                    else:
                        infobox.add("HoechsteEinzelPlatzierung", self.__infolist["highsinglesranking"] + " (" +
                                    str(highsinglesrankingdate.strftime("%#d. %B %Y")) + ")")
                    infobox.add("AktuelleEinzelPlatzierung", self.__infolist["singlesranking"])
                    infobox.add("DoppelBilanz", self.__infolist["doublesrecord"].replace("-", ":"))
                    infobox.add("AnzahlDoppelTitel", self.__infolist["doublestitles"])
                    highdoublesrankingdate = datetime.strptime(self.__infolist["highdoublesrankingdate"], "%Y-%m-%d")
                    if self.__infolist["highdoublesranking"] == "1":
                        infobox.add("HoechsteDoppelPlatzierung",
                                    "[[Liste der Weltranglistenersten im Herrentennis (Doppel)|" +
                                    self.__infolist["highdoublesranking"] + "]] (" +
                                    str(highdoublesrankingdate.strftime("%#d. %B %Y")) + ")")
                    else:
                        infobox.add("HoechsteDoppelPlatzierung", self.__infolist["highdoublesranking"] + " (" +
                                    str(highdoublesrankingdate.strftime("%#d. %B %Y")) + ")")
                    infobox.add("AktuelleDoppelPlatzierung", self.__infolist["doublesranking"])
                    updated = datetime.strptime(self.__infolist["updated"], "%Y-%m-%d")
                    infobox.add("Updated", str(updated.strftime("%#d. %B %Y")))
                    infoboxreturn = infobox
        return infoboxreturn

    # Access of private variables
    language = property(getLanguage)
    site = property(getSite)

# Testing environment
if __name__ == '__main__':
    infolist = {'firstname': 'Rafael', 'lastname': 'Nadal', 'countrycode': 'ESP', 'website': 'http://www.rafaelnadal.com', 'birthday': '1986-06-03', 'turnedpro': '2001', 'weight': '85', 'height': '185', 'birthplace': 'Manacor, Mallorca, Spain', 'residence': 'Manacor, Mallorca, Spain', 'playhand': 'Left-Handed', 'backhand': 'Two-Handed Backhand', 'coach': ['Carlos Moya', 'Francisco Roig'], 'updated': '2020-10-12', 'singlesranking': '2', 'doublesranking': '453', 'highsinglesranking': '1', 'highdoublesranking': '26', 'highsinglesrankingdate': '2008-08-18', 'highdoublesrankingdate': '2005-08-08', 'singlesrecord': '999-201', 'doublesrecord': '137-74', 'singlestitles': '86', 'doublestitles': '11', 'prizemoney': 122905214}
    wdinfo = {"item": "Q10132", "sitelink": "Rafael Nadal", "sitelabel": "Rafael Nadal"}
    a = Infobox(infolist=infolist, wdinfo=wdinfo, language="de", site="wikipedia")
    print(a.updateInfobox())