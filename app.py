# Name:     Flask webservice
# Author:   Mad_melone (https://w.wiki/gDR)
# Date:     24-10-2020
# Content:  Provides a webservice for WikiTennisBot

# External imports
import os
from flask import Flask, render_template, request, redirect, url_for
import pywikibot

# Internal imports
from forms import FormPlayerInfobox
from Classes.wikiedit import Wikicode

#Initiate Flask with config
class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'MiKa200816'
app = Flask(__name__)
app.config.from_object(Config)

@app.route('/')
def home():
    return render_template('about.html')

@app.route('/about/')
def about():
    return render_template('about.html')

@app.route('/playerinfobox/', methods=['GET', 'POST'])
def playerinfobox():
    form = FormPlayerInfobox()
    if request.method == "POST":
        action = request.form.get("action")
        playerid = request.form.get("playerid")
        org = request.form.get("org")
        language = request.form.get("language")
        site = request.form.get("site")
        return redirect(url_for("outputplayerinfobox", action=action, playerid=playerid, org=org, language=language,
                                site=site))
    return render_template('playerinfobox.html', form=form)

@app.route('/outputplayerinfobox/', methods=['GET', 'POST'])
def outputplayerinfobox():
    # Get variables from form
    action = request.args.get("action", type = str)
    playerid = request.args.get("playerid", type = str)
    org = request.args.get("org", type = str)
    language = request.args.get("language", type = str)
    site = request.args.get("site", type = str)
    # Get saved url where the bot saved the output
    savedurl = Wikicode(action=action, playerid=playerid, org=org, language=language, site=site).savedurl
    return render_template("outputplayerinfobox.html", savedurl=savedurl)

@app.route('/playerwins/')
def playerwins():
    return render_template('playerwins.html')

@app.route('/tourneydraw/')
def tourneydraw():
    return render_template('tourneydraw.html')

if __name__ == '__main__':
    app.run(debug=True)