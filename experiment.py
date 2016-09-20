
class Experiment(object):
    """docstring for Experiment"""
    def __init__(self, feedback=None):
        super(Experiment, self).__init__()
        self.feedback = feedback


    def repetition(self):

        ## send start
        self.feedback.send('add_target')

        ## wait for 
        res = self.feedback.wait_for_end()
        # pass

        print 'received msg: ', res
