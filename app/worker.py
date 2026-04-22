from rq import Worker, Queue, Connection
from redis import Redis

# Connection setup
redis_conn = Redis(host='localhost', port=6379)

if __name__ == '__main__':
    with Connection(redis_conn):
        worker = Worker(['repo_analysis'])
        worker.work()
