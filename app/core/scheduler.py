from app.core.bot import morning_bus_mailing

cron_jobs = [
    {'trigger': 'cron', 'day_of_week': 'mon-fri', 'hour': 8, 'minute': 59, 'second': 0},
    {'trigger': 'cron', 'day_of_week': 'mon-fri', 'hour': 9, 'minute': 4, 'second': 0},
    {'trigger': 'cron', 'day_of_week': 'mon-fri', 'hour': 9, 'minute': 9, 'second': 0},
]

user_chat_ids = {
    'chat_ids': [
        417070387,  # me
        431571617,  # Lenok
    ]
}


def asyncio_schedule() -> None:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler

    scheduler = AsyncIOScheduler()
    for cron in cron_jobs:
        scheduler.add_job(morning_bus_mailing, kwargs=user_chat_ids, **cron)
    scheduler.start()
