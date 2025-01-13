import multiprocessing as mp

def function_continent(continent= 'Asia'):
    print('The name of continent is : ', continent)
    exit(0)

if __name__ == '__main__':
    continent_list = ['America', 'Europe', 'Africa']
    processes = [mp.Process(target= function_continent, args= (continent, )) for continent in continent_list]
    processes.append(mp.Process(target= function_continent)) # with default parameter
    for p in processes:
        p.start()
    for p in processes:
        p.join()