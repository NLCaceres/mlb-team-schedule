from . import db
from .models import BaseballGame

from flask import Blueprint, abort, jsonify, redirect, request, url_for
from calendar import monthrange
from datetime import date

bp = Blueprint("api", __name__, url_prefix="/api")


#? Python Map to help with datetime conversions
MONTH_SWITCH = {
    "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10
}


#? All routes prepended with '/api' thanks to prefix param in Blueprint constructor
@bp.route("/fullSchedule")
def apiFullSchedule():
    if len(request.accept_mimetypes) > 1 or not request.accept_mimetypes.accept_json:
        return redirect(url_for("home"))

    allGames = db.session.scalars(db.select(BaseballGame))
    return jsonify([game.asDict for game in allGames])


@bp.route("/<string:month>")
def apiSingleMonthSchedule(month):
    if len(request.accept_mimetypes) > 1 or not request.accept_mimetypes.accept_json:
        return redirect(url_for("home"))

    monthNum = 0
    try:
        monthNum = MONTH_SWITCH[month]
    except KeyError:
        abort(404, "Invalid month")

    year = date.today().year
    start = date(year=year, month=monthNum, day=1)
    end = date(year=year, month=monthNum+1, day=1)

    # COULDN'T get game on month's last day, so `end` must = next month's 1st day
    baseballGames = db.session.scalars(
        db.select(BaseballGame).where(BaseballGame.readableDateTime < end) \
            .where(BaseballGame.readableDateTime >= start)
    )
    return jsonify([game.asDict for game in baseballGames])


@bp.route("/<string:month>/<int:day>")
def apiSingleDaySchedule(month, day):
    if len(request.accept_mimetypes) > 1 or not request.accept_mimetypes.accept_json:
        return redirect(url_for("home"))

    monthNum = 0
    try:
        monthNum = MONTH_SWITCH[month]
    except KeyError:
        abort(404, "Invalid month")

    year = date.today().year
    #? Using `monthrange` to grab a tuple with the first and last day of a given month
    lastDayOfMonth = monthrange(year=year, month=MONTH_SWITCH[month])[1]
    if (day <= 0 or day > lastDayOfMonth):
        abort(404, "Invalid day of the month")

    start = date(year=year, month=monthNum, day=day)
    endMonth = monthNum if (day != lastDayOfMonth) else monthNum + 1
    endDay = day + 1 if (day != lastDayOfMonth) else 1
    end = date(year=year, month=endMonth, day=endDay)

    baseballGames = db.session.scalars( #? `scalars()` returns an iterable `ScalarResult`
        db.select(BaseballGame).where(BaseballGame.readableDateTime < end) \
            .where(BaseballGame.readableDateTime >= start)
    ) #? SO if a basic List is needed, add the suffix `.all()`
    return jsonify([game.asDict for game in baseballGames])


#? Flask Exceptions generally subclass the Werkzeug base Exception for ease of use
# @bp.errorhandler(HTTPException) #? BUT like `except Exception`, this MIGHT overcatch
# def genericExceptionHandler(e: HTTPException):
    #? Returning either a tuple of (response, statusCode) OR (response, headers)
    #? `response` gets input into `make_response` & jsonified if a dict or list is found
    #? KeyArgs in `jsonify()` become `k:v` pairs in the response JSON body
    # return jsonify(error=str(e)), e.code

    # return str(e), 404

    #? Flask sending a redirect to the client STILL sends a template, so must do this:
    # response = make_response(jsonify(navTo='/fullSchedule'))
    # response.status_code = 302
    # return response

#? No matter order declared, the MOST SPECIFIC error handler Flask registered is used
#? Ex: IF abort(404) is run, THEN this handler catches it, NOT the above generic handler,
#? ANY OTHER EXCEPTIONS slip through, and Flask runs its default `abort(500)` instead
@bp.errorhandler(404)
def notFound(e):
    return jsonify(error=str(e)), 404

