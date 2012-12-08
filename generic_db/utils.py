from __future__ import unicode_literals

import datetime
from flask import Flask, redirect, render_template, request, url_for
from flask.ext.sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_pyfile('settings.py')

db = SQLAlchemy(app)


class Game(db.Model):

    game_id = db.Column(db.Integer, primary_key=True)
    home_team = db.Column(db.Text)
    visitor = db.Column(db.Text)
    game_day = db.Column(db.Date)
    home_points = db.Column(db.Integer)
    visitor_points = db.Column(db.Integer)
    spread = db.Column(db.Integer)

    def __init__(self, 
                 game_id,
                 home_team,
                 visitor,
                 game_day,
                 home_points,
                 visitor_points,
                 spread):
        self.game_id = game_id
        self.home_team = home_team
        self.visitor = visitor
        self.visitor_points = visitor_points
        self.home_points = home_points
        self.spread = spread
        self.game_day = game_day
