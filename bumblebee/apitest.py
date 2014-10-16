from bumblebee import botqueueapi
from bumblebee import hive


class APITest():
    def __init__(self):
        hive.loadLogger()
        self.api = botqueueapi.BotQueueAPI()
        self.config = hive.config.get()

    def main(self):
        print "Starting up"

        try:
            # jobs = self.api.createJobFromJob(50)
            # self.printJobs(jobs)

            # jobs = self.api.createJobFromURL('http://www.thingiverse.com/download:91915',
            #                                 name="test name",
            #                                 queue_id=470)
            # print jobs

            # jobs = self.api.createJobFromFile("test.stl")
            # self.printJobs(jobs)

            bots = self.api.getMyBots()
            for bot in bots['data']:
                print bot['driver_config']

        except KeyboardInterrupt:
            pass

    def printJobs(self, jobs):
        for job in jobs["data"]:
            print "Added: %s" % job["name"]


if __name__ == '__main__':
    a = APITest()
    a.main()
