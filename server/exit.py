import signal

should_exit = False

def handler(signum, frame):
	print 'signal caught!'
	global should_exit
	should_exit = True

print 'setting up signals'
signal.signal(signal.SIGTERM, handler)
signal.signal(signal.SIGINT, handler)
print 'ok'

def should_shutdown():
	global should_exit
	return should_exit