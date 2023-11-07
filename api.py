from flask import Blueprint, request, redirect, url_for, jsonify
from calendar import monthrange
from datetime import date
from . import db
from .models import BaseballGame


bp = Blueprint('api', __name__, url_prefix='/api')


#? Python Map to help with datetime conversions
MONTH_SWITCH = { 'march': 3, 'april': 4, 'may': 5, 'june': 6, 'july': 7, 'august': 8, 'september': 9, 'october': 10 }


#? All routes prepended with '/api' thanks to prefix param in Blueprint constructor
@bp.route('/fullSchedule')
def apiFullSchedule():
    if len(request.accept_mimetypes) > 1 or not request.accept_mimetypes.accept_json:
        return redirect(url_for('home'))

    allGames = db.session.scalars(db.select(BaseballGame))
    return jsonify([game.asDict for game in allGames])


@bp.route('/<string:month>')
def apiSingleMonthSchedule(month):
    if len(request.accept_mimetypes) > 1 or not request.accept_mimetypes.accept_json:
        return redirect(url_for('home'))

    monthNum = 0
    try:
        monthNum = MONTH_SWITCH[month]
    except KeyError:
        return { 'message': 'Invalid Month!' }

    year = date.today().year
    start = date(year=year, month=monthNum, day=1)
    end = date(year=year, month=monthNum+1, day=1)

    #* Was unable to get games on last day of month, so simplest solution = set end to 1st day of next month with '<'
    baseballGames = db.session.scalars(
        db.select(BaseballGame).where(BaseballGame.readableDateTime < end).where(BaseballGame.readableDateTime >= start)
    )
    return jsonify([game.asDict for game in baseballGames])


@bp.route('/<string:month>/<int:day>')
def apiSingleDaySchedule(month, day):
    if len(request.accept_mimetypes) > 1 or not request.accept_mimetypes.accept_json:
        return redirect(url_for('home'))

    monthNum = 0
    try:
        monthNum = MONTH_SWITCH[month]
    except KeyError:
        return { 'message': 'Invalid Month!' } #TODO Return status codes!

    year = date.today().year
    lastDayOfMonth = monthrange(year=year, month=MONTH_SWITCH[month])[1] #? Returns tuple (firstDay, lastDay)
    if (day <= 0 or day > lastDayOfMonth):
        return { 'message': 'Invalid Month!' }

    start = date(year=year, month=monthNum, day=day)
    endMonth = monthNum if (day != lastDayOfMonth) else monthNum + 1
    endDay = day + 1 if (day != lastDayOfMonth) else 1
    end = date(year=year, month=endMonth, day=endDay)

    baseballGames = db.session.scalars(
        db.select(BaseballGame).where(BaseballGame.readableDateTime < end).where(BaseballGame.readableDateTime >= start)
    ) #? Since scalars() returns an iterable ScalarResult, only need to suffix .all() if a basic List is explicitly needed
    return jsonify([game.asDict for game in baseballGames])
