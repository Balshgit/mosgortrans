from typing import Any

from app.core.bot import TransportBot
from app.core.utils import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler

bot_cron_jobs = {
    'morning_home->work_bus': {
        'job': TransportBot.morning_bus_mailing,
        'cron': [
            {
                'trigger': 'cron',
                'day_of_week': 'mon-fri',
                'hour': 8,
                'minute': 59,
                'second': 0,
            },
            {
                'trigger': 'cron',
                'day_of_week': 'mon-fri',
                'hour': 9,
                'minute': 4,
                'second': 0,
            },
            {
                'trigger': 'cron',
                'day_of_week': 'mon-fri',
                'hour': 9,
                'minute': 9,
                'second': 0,
            },
        ],
        'func_kwargs': {
            'chat_ids': [
                417070387,  # me
                # 431571617,  # Lenok
            ]
        },
    }
}


class BotScheduler:
    def __init__(
        self,
        cron_jobs: dict[str, dict[str, Any]],
    ):
        self.cron_jobs = cron_jobs
        self.scheduler = AsyncIOScheduler()

    def add_scheduler_jobs(self, jobs_name: str) -> None:
        cron_jobs = self.cron_jobs.get(jobs_name)
        if not cron_jobs:
            return None
        for cron in cron_jobs['cron']:
            self.scheduler.add_job(
                cron_jobs['job'], kwargs=cron_jobs.get('func_kwargs'), **cron
            )
            logger.info(f'Added scheduled job: {cron_jobs["job"].__name__} {cron}')

    def start(self) -> None:
        self.scheduler.start()
        logger.info('Scheduler started')


bot_scheduler = BotScheduler(cron_jobs=bot_cron_jobs)
bot_scheduler.add_scheduler_jobs(jobs_name='morning_home->work_bus')
