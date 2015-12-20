import threading
import os


def startclient():
    os.system('python ../p2psearch/file.py')
    return

while True:
    try:
        clientNumber = int(raw_input("How many clients shell be started?: "))
        break
    except ValueError:
        print 'Please type in a number!'
        continue


threads = []
for i in range(clientNumber):

    t = threading.Thread(target=startclient)
    threads.append(t)
    t.start()
