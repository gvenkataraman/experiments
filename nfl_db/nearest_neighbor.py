"""
Given a game, find the nearest games and print
"""
from __future__ import unicode_literals

import argparse
import datetime
from dateutil import parser
from sqlalchemy import between, or_

from nfl import db, Game


def _collect_past_game_diff(game_day, max_games, team, all_games):

    score_diffs = list()
    for game in all_games:
        if game_day < game.game_day:
            continue
        if team in (game.home_team, game.visitor):
            diff = game.home_points - game.visitor_points
            if game.home_team != team:
                diff = -diff
            score_diffs.append(diff)
            if len(score_diffs) >= max_games:
                break
    return score_diffs


def dist(v1, v2):

    d = 0
    for index, value in enumerate(v1):
        diff = value - v2[index]
        d += diff*diff
    return d

def compute_spread(host, visitor, date):
    date = parser.parse(date)
    max_games = 5 
    max_games_to_analyze = 10000
    # loop through all games and find closest
    tmax = date - datetime.timedelta(days = 1)
    tmin = date - datetime.timedelta(days = 10*365)
    all_games = (db.session.query(Game)
                 .filter(between(Game.game_day, tmin, tmax))
                 .order_by(Game.game_day.desc())
                 .limit(max_games_to_analyze)).all()
    host_vector = _collect_past_game_diff(date.date(), max_games, host, all_games)
    visitor_vector = _collect_past_game_diff(date.date(), max_games, visitor, all_games)
    print host_vector
    print visitor_vector
    games_score = list()

    for index, game in enumerate(all_games):
        current_host_vector = _collect_past_game_diff(game.game_day, max_games,
                                                     game.home_team, all_games)
        current_visitor_vector = _collect_past_game_diff(game.game_day, max_games,
                                                     game.visitor, all_games)
        if not current_host_vector:
            continue
        if not current_visitor_vector:
            continue
        min_length = min(len(current_host_vector), len(current_visitor_vector))
        if min_length != max_games:
            continue
        current_dist = dist(current_host_vector, host_vector)
        current_dist += dist(current_visitor_vector, visitor_vector)
        games_score.append((current_dist, game))

    games_score.sort(key=lambda tup:tup[0])

    spread = list()
    for game in games_score[:max_games]:
        print game[0], game[1]
        spread.append(game[1].actual_spread)

    total = sum(spread)
    computed_line = total / len(spread)
    actual_game = (db.session.query(Game)
                   .filter(Game.game_day == date.date())
                   .filter(Game.home_team == host)
                   .filter(Game.visitor == visitor)).first()
    print 'computed line ', computed_line
    if actual_game:
        print 'spread: %d actual spread: %d computed: %f' % (actual_game.spread, actual_game.actual_spread, computed_line)
    return computed_line


def execute(args):
    from pprint import pprint
    pprint(args.__dict__)
    return compute_spread(args.host, args.visitor, args.date)


def run_test(args):
    start_date = parser.parse(args.start_date)
    end_date = parser.parse(args.end_date)
    all_games = (db.session.query(Game)
                 .filter(between(Game.game_day, start_date, end_date))).all()

    numb_success = 0
    numb_failed = 0

    for game in all_games:
        computed_spread = compute_spread(
            host=game.home_team,
            visitor=game.visitor,
            date=str(game.game_day),
        )
        if abs(computed_spread - game.spread) <= 3:
            continue
        actual_spread = game.actual_spread
        success = False
        if computed_spread < game.spread and actual_spread < game.spread:
            success = True
        elif computed_spread > game.spread and actual_spread > game.spread:
            success = True
        if success:
            numb_success += 1
        else:
            numb_failed += 1
        print game
        print computed_spread, game.spread, actual_spread, success

    print 'total games ', len(all_games)
    print numb_success, numb_failed


def main():
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument('--date', action='store', 
                            dest='date')
    arg_parser.add_argument('--host', action='store', 
                            dest='host')
    arg_parser.add_argument('--visitor', action='store', 
                            dest='visitor')
    arg_parser.add_argument('--test', action='store_true', 
                            dest='test')
    arg_parser.add_argument('--start_date', action='store', 
                            dest='start_date')
    arg_parser.add_argument('--end_date', action='store', 
                            dest='end_date')
    args = arg_parser.parse_args()
    if args.test:
        run_test(args) 
    else:
        execute(args)


if __name__ == '__main__':
    main()
