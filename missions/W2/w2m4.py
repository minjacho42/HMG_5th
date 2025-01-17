import multiprocessing as mp
import queue
import time

def process_task(tasks_to_accomplish, tasks_that_are_done, proc_id):
    """
    완벽히 try except를 분리하기 위해서는 nested try가 발생하기에
    코드의 가독성을 위해서 아래와 같이 작성.
    """
    while not tasks_to_accomplish.empty():
        try:
            task = tasks_to_accomplish.get_nowait()
            print(f'Task no {task}')
            time.sleep(0.5)
            tasks_that_are_done.put_nowait((task, proc_id))
        except queue.Empty:
            continue
        except queue.Full:
            print('Queue is full')
            exit(1)


if __name__ == '__main__':
    tasks_to_accomplish = mp.Queue()
    tasks_that_are_done = mp.Queue()
    for task in range(10):
        try:
            tasks_to_accomplish.put_nowait(task)
        except queue.Full as e:
            print(f'Queue Error {e}')
    # 프로세스를 늦게 만들어서 자원 부담을 줄인다.
    processes = [mp.Process(target=process_task, args=(tasks_to_accomplish, tasks_that_are_done, idx + 1)) for idx in range(4)]
    for p in processes:
        p.start()
    for p in processes:
        p.join()
    # while not tasks_that_are_done.empty():
    #     task_no, proc_id = tasks_that_are_done.get_nowait()
    #     print(f'Task no {task_no} is done by Process-{proc_id}')
    while not tasks_that_are_done.empty():
        try:
            task_no, proc_id = tasks_that_are_done.get_nowait()
        except queue.Empty:
            continue
        else:
            print(f'Task no {task_no} is done by Process-{proc_id}')