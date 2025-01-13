import multiprocessing as mp
import queue
import time

def process_task(tasks_to_accomplish, tasks_that_are_done, proc_id):
    while True:
        try:
            task = tasks_to_accomplish.get_nowait()
            print(f'Task no {task}')
            time.sleep(0.5)
            tasks_that_are_done.put_nowait((task, proc_id))
        except queue.Empty:
            exit(0)
        except queue.Full:
            print('Queue is full')
            exit(1)


if __name__ == '__main__':
    tasks_to_accomplish = mp.Queue()
    tasks_that_are_done = mp.Queue()
    processes = [mp.Process(target=process_task, args=(tasks_to_accomplish, tasks_that_are_done, idx + 1)) for idx in range(4)]
    for task in range(10):
        try:
            tasks_to_accomplish.put_nowait(task)
        except queue.Full as e:
            print(f'Queue Error {e}')
    for p in processes:
        p.start()
    for p in processes:
        p.join()
    while not tasks_that_are_done.empty():
        task_no, proc_id = tasks_that_are_done.get_nowait()
        print(f'Task no {task_no} is done by Process-{proc_id}')