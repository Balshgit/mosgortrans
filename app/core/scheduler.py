from typing import Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.bot import TransportBot
from app.core.utils import logger
from settings import CHAT_IDS

bot_cron_jobs = {
    'morning_home->work_bus': {
        'job': TransportBot.morning_bus_mailing,
        'cron': [
            {
                'time': {
                    'trigger': 'cron',
                    'day_of_week': 'mon-fri',
                    'hour': 8,
                    'minute': 59,
                    'second': 0,
                },
            },
            {
                'time': {
                    'trigger': 'cron',
                    'day_of_week': 'mon-fri',
                    'hour': 9,
                    'minute': 4,
                    'second': 0,
                },
            },
            {
                'time': {
                    'trigger': 'cron',
                    'day_of_week': 'mon-fri',
                    'hour': 9,
                    'minute': 9,
                    'second': 0,
                },
                'kwargs_per_job': {'show_keyboard': True},
            },
        ],
        'func_kwargs': {
            'chat_ids': CHAT_IDS,
        },
    }
}


class BotScheduler:
    scheduler = AsyncIOScheduler()

    def __init__(
        self,
        cron_jobs: dict[str, dict[str, Any]],
    ):
        self.cron_jobs = cron_jobs

    def add_scheduler_jobs(self, jobs_name: str) -> None:
        cron_jobs = self.cron_jobs.get(jobs_name)
        if not cron_jobs:
            return None
        for cron in cron_jobs['cron']:
            self.scheduler.add_job(
                cron_jobs['job'],
                kwargs=dict(
                    **cron_jobs.get('func_kwargs'), **cron.get('kwargs_per_job', {})  # type: ignore
                ),
                **cron['time'],
            )
            logger.info(f'Added scheduled job: {cron_jobs["job"].__name__} {cron}')

    def start(self) -> None:
        self.scheduler.start()
        logger.info('Scheduler started')


bot_scheduler = BotScheduler(cron_jobs=bot_cron_jobs)
bot_scheduler.add_scheduler_jobs(jobs_name='morning_home->work_bus')
