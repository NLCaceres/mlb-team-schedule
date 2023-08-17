from . import scheduler
from .commands import database_update
from datetime import date
from zoneinfo import ZoneInfo #? Concrete implementation of datetime.tzinfo which uses IANA timezone names

thisYear = date.today().year

#? APScheduler scheduled_job() decorator == Flask-APScheduler's task() decorator
@scheduler.task(
    "interval",
    days=7, #? 'weeks', 'hours', 'minutes', & 'seconds' are also available and take ints
    start_date=f"{thisYear}-02-26 03:30:00",
    end_date=f"{thisYear}-11-30 03:30:00",
    timezone=ZoneInfo('America/Los_Angeles'),
    id='update team records',
    name='update team records',
    misfire_grace_time=10, #? Seconds to wait if job fails or is determined to have not run
    coalesce=True #? Rather than run 2 (or 3 or 4) jobs upon fail, just run 1 to replace the failed job
)
def updateTeamRecordTask():
    with scheduler.app.app_context():
        print("Running 'Update Team Record' Task")
        database_update.updateAllTeamRecords()
        print("'Update Team Record' Task Complete")

@scheduler.task(
    "interval",
    days=7,
    start_date=f"{thisYear}-02-26 03:35:30",
    end_date=f"{thisYear}-11-30 03:35:30",
    timezone=ZoneInfo('America/Los_Angeles'),
    id='update promotions',
    name='update promotions',
    misfire_grace_time=10,
    coalesce=True
)
def updateAllPromotionsTask():
    with scheduler.app.app_context():
        print("Running 'Update Promotion List' Task")
        database_update.updateAllPromotions()
        print("'Update Promotion List' Task Complete")
