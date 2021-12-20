import time
import queue
import datetime
import logging

import petfeedd

from worker import Worker
from models.Feed import Feed
from models.FeedEvent import FeedEvent
from subprocess import call

class TimeWorker(Worker):
    def __init__(self, feed_queue, *args, **kwargs):
        self.feed_queue = feed_queue
        super().__init__(*args, **kwargs)

    def run(self):
        logging.getLogger('petfeedd').info("Starting time worker.")

        while True:
            if self.stopped():
                logging.getLogger('petfeedd').info("Stopping time worker.")
                return

            if petfeedd.feeding_semaphore:
                time_query = time.strftime("%H:%M:%S")
                for feed in Feed.select().where(Feed.time==time_query):
                    logging.getLogger('petfeedd').info("Found feed " + feed.name + " at " + time_query)
                    feed_event = FeedEvent.create(size=feed.size, name=feed.name)
                    self.feed_queue.put(feed_event)
                    self.removeOldFeeds()
                    feed.last_feed = feed_event.date_updated
                    feed.feed_count = feed.feed_count + 1
                    feed.save()

            time.sleep(1)

    def removeOldFeeds(self):
        feed_events = []
        count = 0
        for feed_event in FeedEvent.select().order_by(FeedEvent.date_created.desc()):
            if count >= 10:
                data = "./delete-video.sh feed_" + str(feed_event.id)
                call([data], shell=True, cwd='/home/pi/hungry-cat/src/static/videos')
                feed_event.delete_instance()
            count += 1