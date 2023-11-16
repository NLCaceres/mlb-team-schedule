from flask import Blueprint, abort, jsonify, request, redirect, url_for
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
        abort(404, 'Invalid month')

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
        abort(404, 'Invalid month')

    year = date.today().year
    lastDayOfMonth = monthrange(year=year, month=MONTH_SWITCH[month])[1] #? Returns tuple (firstDay, lastDay)
    if (day <= 0 or day > lastDayOfMonth):
        abort(404, 'Invalid day of the month')

    start = date(year=year, month=monthNum, day=day)
    endMonth = monthNum if (day != lastDayOfMonth) else monthNum + 1
    endDay = day + 1 if (day != lastDayOfMonth) else 1
    end = date(year=year, month=endMonth, day=endDay)

    baseballGames = db.session.scalars(
        db.select(BaseballGame).where(BaseballGame.readableDateTime < end).where(BaseballGame.readableDateTime >= start)
    ) #? Since scalars() returns an iterable ScalarResult, only need to suffix .all() if a basic List is explicitly needed
    return jsonify([game.asDict for game in baseballGames])


#? Flask Exceptions generally descend from this Werkzeug base Exception so it's super easy for simple cases to use
# @bp.errorhandler(HTTPException) #? BUT, of course, this is like catching Exception, you MIGHT catch more than expected
# def genericExceptionHandler(e: HTTPException):
    #? Returning a tuple means sending (response, status_code) OR (response, headers) depending on types used
    #? The response will have make_response called on it which ONLY calls jsonify() if a dict or list is found
    # return jsonify(error=str(e)), e.code #? KeyArgs in jsonify() become key:val pairs in the response's JSON Body

    # return str(e), 404 #? In this case, Javascript calls to response.json() will fail, so use response.text() instead

    #? Sending a redirect to the API from the Flask backend sends back a Template! So better to craft a response like below
    # response = make_response(jsonify(navTo='/fullSchedule'))
    # response.status_code = 302
    # return response

#? Regardless of order declared, the MOST SPECIFIC error handler Flask has registered will be used
#? Ex: IF abort(404) is run, THEN this handler catches it, NOT the above generic handler,
#? BUT IF any other exceptions were raised, THEN they'd slip through, and Flask would run `abort(500)` by default instead
@bp.errorhandler(404)
def notFound(e):
    return jsonify(error=str(e)), 404
