from __future__ import unicode_literals

import datetime
from flask import Flask, redirect, render_template, request, url_for
from flask.ext.sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_pyfile('settings.py')

db = SQLAlchemy(app)


class Game(db.Model):

    @classmethod
    def max_game_id(cls):
        max_game = db.session.query(cls).order_by(cls.game_id.desc()).first()
        return max_game.game_id if max_game else None

    game_id = db.Column(db.Integer, unique=True, nullable=False)
    home_team = db.Column(db.Text, primary_key=True, nullable=False)
    visitor = db.Column(db.Text, primary_key=True, nullable=False)
    game_day = db.Column(db.Date, primary_key=True, nullable=False)
    home_points = db.Column(db.Integer, nullable=False)
    visitor_points = db.Column(db.Integer, nullable=False)
    spread = db.Column(db.Float, nullable=False)
    total_line = db.Column(db.Integer)

    def __init__(self, 
                 game_id,
                 home_team,
                 visitor,
                 game_day,
                 home_points,
                 visitor_points,
                 total_line,
                 spread):
        self.game_id = game_id
        self.home_team = home_team
        self.visitor = visitor
        self.visitor_points = visitor_points
        self.home_points = home_points
        self.spread = spread
        self.game_day = game_day
        self.total_line = total_line

    def __str__(self):
        output =  ('id: %d Date: %s Host: %s visitor: %s score (%d, %d)' % (self.game_id, self.game_day, 
                                                                self.home_team, 
                                                                self.visitor, 
                                                                self.home_points, 
                                                                self.visitor_points))
        return output

    @property
    def actual_spread(self):
        return self.home_points - self.visitor_points
