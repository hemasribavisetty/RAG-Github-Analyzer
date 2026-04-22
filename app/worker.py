from redis import Redis
from rq import Worker, Queue

# Connection setup
redis_conn = Redis(host='localhost', port=6379)

if __name__ == '__main__':
    # Pass the connection directly to the Worker
    # Specify the queue names you want this worker to listen to
    worker = Worker(['repo_analysis'], connection=redis_conn)
    worker.work()
