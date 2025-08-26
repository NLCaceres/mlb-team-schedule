from . import scheduler
from .commands.update_promotions import updateAllPromotions
from .commands.update_standings import updateAllTeamRecords

from datetime import date
#? Concrete implementation of datetime.tzinfo that uses IANA timezone names
from zoneinfo import ZoneInfo

thisYear = date.today().year

#? APScheduler scheduled_job() decorator == Flask-APScheduler's task() decorator
@scheduler.task(
    "interval",
    days=7, #? 'weeks', 'hours', 'minutes', & 'seconds' are also available and take ints
    start_date=f"{thisYear}-02-26 03:30:00",
    end_date=f"{thisYear}-11-30 03:30:00",
    timezone=ZoneInfo("America/Los_Angeles"),
    id="update team records",
    name="update team records",
    misfire_grace_time=10, #? Seconds to wait if job fails or if job didn't run
    coalesce=True #? If the same job gets scheduled multiple times, JUST RUN ONCE!
)
def updateTeamRecordTask():
    with scheduler.app.app_context():
        print("Running 'Update Team Record' Task")
        updateAllTeamRecords()
        print("'Update Team Record' Task Complete")

@scheduler.task(
    "interval",
    days=7,
    start_date=f"{thisYear}-02-26 03:35:30",
    end_date=f"{thisYear}-11-30 03:35:30",
    timezone=ZoneInfo("America/Los_Angeles"),
    id="update promotions",
    name="update promotions",
    misfire_grace_time=10,
    coalesce=True
)
def updateAllPromotionsTask():
    with scheduler.app.app_context():
        print("Running 'Update Promotion List' Task")
        updateAllPromotions()
        print("'Update Promotion List' Task Complete")

