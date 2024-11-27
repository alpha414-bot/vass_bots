import queue
import threading
from settings import emblem, settings
from utils.views import PrepData
import time
from logger import logger

# Thread-safe queue
task_queue = queue.Queue()


# Task Worker Function
def bot_task(task_id):
    logger.success(f"0.0 Task with TID: {task_id} started.")
    # Simulate the bot's work (replace with your automation logic)
    PrepData(task_id=task_id).get_botid()
    time.sleep(5)  # Task duration
    logger.success(f"0.1 Task with TID: {task_id} completed.")


# Worker Thread Function
def worker():
    while True:
        task_id = task_queue.get()
        if task_id is None:  # Stop signal
            break
        logger.success(
            f"Worker service with TID: {task_id} initialize | Telegram Usage: {settings.USE_TG_BOT} | Proxy: {settings.PROXY}"
        )
        try:
            bot_task(task_id)
        except:
            task_queue.task_done()


# Main function running bot
def main():
    max_concurrent_tasks = 7
    task_count = 0
    workers = []

    # Start Worer Threads
    for _ in range(max_concurrent_tasks):
        t = threading.Thread(target=worker)
        t.daemon = True  # Daemon thread stops when the main program exists
        t.start()
        workers.append(t)
    try:
        # Schedule Tasks
        while True:
            task_count += 1
            task_queue.put(task_count)
            time.sleep(10)  # wait 1 second before adding a new task
    except KeyboardInterrupt:
        print("Shutting bot down")
    finally:
        # Signal works to exit
        for _ in workers:
            task_queue.put(None)
        for t in workers:
            t.join()


if __name__ == "__main__":
    print(emblem)
    main()
