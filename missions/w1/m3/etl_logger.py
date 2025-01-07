from datetime import datetime

LOG_FILE = 'etl_project_log.txt'

# log etl step with msg
def logger(step: str, msg: str):
	with open(LOG_FILE, 'a') as file:
		now = datetime.now()
		timestamp = now.strftime("%Y-%B-%d-%H-%M-%S") #formatting the timestamp
		file.write(f'{timestamp}, [{step.upper()}] {msg}\n')

