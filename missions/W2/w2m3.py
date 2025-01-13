import multiprocessing as mp
import queue

def put_item(q):
    items = ['red', 'green', 'blue', 'black']
    for idx, item in enumerate(items):
        print(f'item no: {idx + 1} {item}')
        q.put_nowait(item)

def pop_item(q):
    idx = 0
    while True:
        try:
            item = q.get_nowait()
            print(f'item no: {idx} {item}')
            idx += 1
        except queue.Empty:
            break

if __name__ == '__main__':
    que = mp.Queue()
    print('pushing items to queue:')
    p = mp.Process(target=put_item, args=(que,))
    p.start()
    p.join()
    print('popping items from queue:')
    p2 = mp.Process(target=pop_item, args=(que,))
    p2.start()
    p2.join()
    #
    # for i, color in enumerate(['red', 'green', 'blue', 'black']):
    #     print(f'item no: {i} {color}')
    #     que.put_nowait(color)
    # print('fst')
    # while not que.empty():
    #     item = que.get_nowait()
    #     print(f'item no: {item}')
    # print('snd')
    # while not que.empty():
    #     item = que.get_nowait()
    #     print(f'item no: {item}')