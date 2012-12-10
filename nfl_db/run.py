from __future__ import unicode_literals

import argparse
import csv
from dateutil import parser

from nfl import db, Game


def load_db(args):
    with open(args.load_file, 'rb') as f:
        reader = csv.DictReader(f)
        current_game_id = (Game.max_game_id() or 0) + 1
        for row in reader:
            if row['Date'] == 'Date':
                continue
            spread = row['Line']
            try:
                spread = float(spread)
                home_points = int(row['Home Score'])
            except ValueError:
                continue
            try:
                game = Game(
                    game_id=current_game_id,
                    home_team=row['Home Team'],
                    visitor=row['Visitor'],
                    game_day=parser.parse(row['Date']),
                    home_points=home_points,
                    visitor_points=int(row['Visitor Score']),
                    spread=spread,
                    total_line=row['Total Line'],
                )
            except ValueError:
                continue
            db.session.add(game)
            current_game_id += 1
        db.session.commit()


def dump_spread(args):
    if not args.output_file:
        return

    with open(args.output_file, 'wb') as f:
        header = 'date,home,visitor,spread,actual_spread'
        f.write(header)
        f.write('\n')
        all_games = db.session.query(Game).all()
        for game in all_games:
            output = ('%s,%s,%s,%d,%d' % (game.game_day, 
                                          game.home_team, game.visitor, 
                                          game.spread, game.actual_spread))
            f.write(output)
            f.write('\n')


def execute(args):
    if args.load_file:
        return load_db(args)
    elif args.dump_spread:
        return dump_spread(args)


def main():
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument('--load_file', action='store', 
                            dest='load_file',)
    arg_parser.add_argument('--dump_spread', action='store_true', 
                            dest='dump_spread',)
    arg_parser.add_argument('--output_file', action='store', 
                            dest='output_file',)
    args = arg_parser.parse_args()
    execute(args)


if __name__ == '__main__':
    main()
