#pip install apscheduler
apscheduler.triggers.cron¶
API¶

Parameters
year (int|str) – 4-digit year

month (int|str) – month (1-12)

day (int|str) – day of month (1-31)

week (int|str) – ISO week (1-53)

day_of_week (int|str) – number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun)

hour (int|str) – hour (0-23)

minute (int|str) – minute (0-59)

second (int|str) – second (0-59)

start_date (datetime|str) – earliest possible date/time to trigger on (inclusive)

end_date (datetime|str) – latest possible date/time to trigger on (inclusive)

timezone (datetime.tzinfo|str) – time zone to use for the date/time calculations (defaults to scheduler timezone)

jitter (int|None) – delay the job execution by jitter seconds at most


from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()


@sched.scheduled_job('interval', minutes=3)
def timed_job():
    print('This job is run every three minutes.')

@sched.scheduled_job('cron', day_of_week='mon-fri', hour=17)
def scheduled_job():
    print('This job is run every weekday at 5pm.')

sched.start()


Examples¶
Run job_function every 2 hours, but only on Saturdays and Sundays:

from apscheduler.triggers.combining import AndTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger


trigger = AndTrigger([IntervalTrigger(hours=2),
                      CronTrigger(day_of_week='sat,sun')])
scheduler.add_job(job_function, trigger)
Run job_function every Monday at 2am and every Tuesday at 3pm:

trigger = OrTrigger([CronTrigger(day_of_week='mon', hour=2),
                     CronTrigger(day_of_week='tue', hour=15)])
scheduler.add_job(job_function, trigger)