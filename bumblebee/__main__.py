from threading import Thread

from .bqclient import BQClient

bq_client = BQClient()

thread = Thread(target=bq_client.run)
thread.start()
thread.join()
