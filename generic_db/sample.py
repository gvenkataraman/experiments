from __future__ import unicode_literals

from utils import db, Game


def expr():
    game = Game(
        game_id=1,
        home_team='sf',
        visitor='nyg',
        game_day=datetime.datetime.utcnow(),
        home_points=17,
        visitor_points=20,
        spread=3,
    )
    db.session.add(game)
    db.session.commit()


if __name__ == '__main__':
    expr()
