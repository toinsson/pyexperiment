# create the experiment

import experiment
from comm import feedback

fb = feedback.Feedback()

exp = experiment.Experiment(feedback=fb)


## for repetitions in conditions:
for i in range(2):
    print 'repetition {}'.format(i)
    exp.repetition()