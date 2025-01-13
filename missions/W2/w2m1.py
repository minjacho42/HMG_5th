import time
import os
from multiprocessing import Pool

def work_log(process_name, wait_time):
    # print(f'{os.getpid()}')
    print(f'{process_name} waiting {wait_time} seconds')
    time.sleep(wait_time)
    print(f'{process_name} Finished.')
#
# def work_log(args):
#     process_name, wait_time = args
#     print(f'{process_name} waiting {wait_time} seconds')
#     time.sleep(wait_time)
#     print(f'{process_name} Finished.')

if __name__ == '__main__':
    work = [
        ('A', 5),
        ('B', 2),
        ('C', 1),
        ('D', 3),
    ]
    with Pool(processes=2) as pool:
        pool.starmap(work_log, work)
        # pool.map(work_log, work)

# 첫번째 프로세스는 5 하나만 실행하게 되며, 두번째 프로세스가 B,C,D를 실행하여, 총 6초가 걸린다.