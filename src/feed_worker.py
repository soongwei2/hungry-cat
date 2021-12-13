import os
import time
import queue
import datetime
import logging

from worker import Worker
from events.Notification import Notification
from subprocess import call

# Let's try to identify what hardware we're on.
is_gpio_capable = False
if os.path.isfile("/sys/firmware/devicetree/base/model"):
    with open("/sys/firmware/devicetree/base/model", 'r') as stat_file:
        data=stat_file.read()
        if data[0:9] == "Raspberry":
            is_gpio_capable = True

else:
    if not os.environ.get('PIGPIO_ADDR') == None:
        is_gpio_capable = True

if not is_gpio_capable:
    logging.getLogger('petfeedd').warning("This is not a Raspberry Pi and PIGPIO_ADDR for remote GPIO has not \
been defined. Disabling GPIO.")

# If this device is not GPIO capable, we need to just disable it all. We'll
# simulate feeds.
if is_gpio_capable:
    from gpiozero import Servo

class FeedWorker(Worker):
    def __init__(self, feed_queue, config, notification_queue, *args, **kwargs):
        self.feed_queue = feed_queue
        self.config = config
        self.notification_queue = notification_queue
        super().__init__(*args, **kwargs)

    def run(self):
        logging.getLogger('petfeedd').info("Starting feed worker.")

        while True:
            if self.stopped():
                logging.getLogger('petfeedd').info("Stopping feed worker.")
                return

            try:
                feed_event = self.feed_queue.get(timeout=1)
                if feed_event:
                    logging.getLogger('petfeedd').info("Found a feed event. Dispensing " + str(feed_event.size) + " feeds.")
                    self.feed(feed_event.size)
                    self.recordVideo(feed_event.date_created)
                    note = Notification()
                    note.text = self.config["general"]["name"] + " dispensed " + \
                        str(feed_event.size) + " feeds at " + \
                        datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")

                    self.notification_queue.put(note)

                self.feed_queue.task_done()
            except queue.Empty:
                pass

    def feed(self, feed_size):
        for _ in range(int(feed_size)):
            call(["node", "/home/pi/hungry-cat-servo/index.js", "true"])
            time.sleep(2)

    def recordVideo(self, id):
        print("id: ", id)
        data = "record-video.sh " + str(id)
        print("data: ", data )
        call([data], shell=True, cwd='/home/pi')