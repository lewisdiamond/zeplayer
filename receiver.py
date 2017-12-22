import json
import boto3
import sys
from subprocess import Popen

current_song = None
sqs = boto3.resource('sqs')
queue = sqs.get_queue_by_name(QueueName='zePlayer')

db = None

def init():
    global db
    with open('db.json', ro) as x:
        db = json.load(x)


def play(song):
    global current_song
    if current_song is not None:
        current_song.terminate()
        current_song = None
    actual_song = db.get(song)
    if actual_song is not None:
        current_song = Popen(['afplay', db.get(song)])

def stop(*x):
    global current_song
    if current_song is not None:
        current_song.terminate()


def get_from_sqs():
    print ('Getting messages')
    d = None
    for message in queue.receive_messages(WaitTimeSeconds=20):
        d = json.loads(message.body)
        message.delete()
    return d

def purge_queue():
    for message in queue.receive_messages():
        message.delete()


try:
    purge_queue()
    init()
    while True:
        c = get_from_sqs()
        if c is not None:
            saywut = lambda *x: print('Say wut mate?')
            {
                'exit': lambda *x: sys.exit(0),
                'play': play,
                'stop': stop
            }.get(
                c.get('command', saywut),
                saywut
            )(c.get('params'))
except SystemExit:
    print('Sure mate!')
except:
    import traceback
    tb = traceback.format_exc()
    print('Ugh, something borked', tb)
