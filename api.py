from flask import Blueprint, request, redirect, url_for, jsonify
from calendar import monthrange
from datetime import date
from .models import DodgerGame

bp = Blueprint('api', __name__, url_prefix='/api')

#? Python Map to help with datetime conversions
MONTH_SWITCH = { 'march': 3, 'april': 4, 'may': 5, 'june': 6, 'july': 7, 'august': 8, 'september': 9, 'october': 10 }

#? All routes prepended with '/api' thanks to prefix param in Blueprint constructor
@bp.route('/fullSchedule')
def apiFullDodgerSchedule():
    if len(request.accept_mimetypes) > 1 or not request.accept_mimetypes.accept_json: 
        return redirect(url_for('home'))

    allGames = DodgerGame.query.all()
    return jsonify([game.asDict for game in allGames])

@bp.route('/<string:month>')
def apiSingleMonthDodgerSchedule(month):
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
    dodgerGames = DodgerGame.query.filter(DodgerGame.readableDateTime < end).filter(DodgerGame.readableDateTime >= start)
    return jsonify([game.asDict for game in dodgerGames])
    
@bp.route('/<string:month>/<int:day>')
def apiSingleDayDodgerSchedule(month, day):
    if len(request.accept_mimetypes) > 1 or not request.accept_mimetypes.accept_json: 
        return redirect(url_for('home'))

    monthNum = 0
    try: 
        monthNum = MONTH_SWITCH[month]
    except KeyError:
        return { 'message': 'Invalid Month!' }

    year = date.today().year
    lastDayOfMonth = monthrange(year=year, month=MONTH_SWITCH[month])[1] #? Returns tuple (firstDay, lastDay)
    if (day <= 0 or day > lastDayOfMonth):
        return { 'message': 'Invalid Month!' }

    start = date(year=year, month=monthNum, day=day)
    endMonth = monthNum if (day != lastDayOfMonth) else monthNum + 1
    endDay = day + 1 if (day != lastDayOfMonth) else 1
    end = date(year=year, month=endMonth, day=endDay)

    dodgerGames = DodgerGame.query.filter(DodgerGame.readableDateTime < end).filter(DodgerGame.readableDateTime >= start)
    return jsonify([game.asDict for game in dodgerGames])
