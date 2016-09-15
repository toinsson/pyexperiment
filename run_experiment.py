"""Runs an experiment.
"""
import time
import numpy as np
import h5py

# from sys import path
# path.insert(1,'/home/antoine/Documents/owndev/sqlexperiment')
# import pseudo, extract

import comm
import experiment
import clientserver as cs

import datetime
datetime_format = "%Y-%m-%d_%H:%M:%S"
def datetime_now():
    return datetime.datetime.now().strftime(datetime_format)

dataFolder = '/media/antoine/9E38F4BA38F4928F/data/modeling/pointing'
logFilename = dataFolder+'/'+'random.db'

## user
is_new_user = experiment.query_yes_no('new user?')

# if is_new_user: user = pseudo.get_pseudo()
# else: user = raw_input('enter name')
# session_now = user+'_'+datetime_now()
# raw_input('[User] :'+ user)
# raw_input('[Enter] to start')

with experiment.Experiment(logFilename, ntp_sync=False) as exp:

    # ## sensors and feedback
    # touchStream = comm.TouchStream(exp.l, local=False)
    # sensors = [touchStream]
    # exp.attach_sensors(sensors)
    # exp.start_sensors()

    feedback = comm.Feedback()
    exp.attach_feedback(feedback)


    for i in range(50):
        exp.feedback.send()
        time.sleep(0.1)

    time.sleep(3)

    # if is_new_user:
    #     exp.l.create("USER", name=user, data={"leftright":"right"})

    # # new session
    # exp.l.create('SESSION', session_now, stype='exprun')

    # ## bind session and user
    # exp.l.enter('touch', session = session_now)
    # exp.l.bind("USER", user)

    # meta = extract.meta_dataframe(exp.l.cursor)

    # raw_input('start recording')


    # for repet in xrange(nrepet):

    #     for indice, row in meta['SESSION'].iterrows():
    #         if row['type'] == 'line':
    #             condition = row['name']
    #             msg = 'TARGET ['+str(cnt)+'/'+str(nline*nrepet)+']: ' + condition
    #             raw_input(msg)
    #             exp.non_blocking_repetition_with_random_target(condition, validation=True)
    #             cnt += 1
