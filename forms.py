from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired

class FormPlayerInfobox(FlaskForm):
    action = SelectField("Action", choices=[("createInfobox", "Create new Infobox"), ("updateInfobox", "Update Infobox")])
    playerid = StringField("Player ID", validators=[DataRequired()])
    org = SelectField('Tennis Organisation', choices=[('atp', 'ATP')])
    language = SelectField('Wikipedia Language', choices=[('de', 'de')])
    site = SelectField('Wikipedia Site', choices=[('wikipedia', 'Wikipedia')])
    submit = SubmitField('Request')
