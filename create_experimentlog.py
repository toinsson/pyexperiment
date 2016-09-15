import argparse


def main(args):

    dataFolder = '/media/antoine/9E38F4BA38F4928F/data/modeling/pointing'
    runName = 'random'
    logFilename = dataFolder+'/'+runName+'.db'

    from sys import path
    path.insert(1,'/home/antoine/Documents/owndev/sqlexperiment')
    import experimentlog, pseudo
    import extract

    e = experimentlog.ExperimentLog(logFilename, ntp_sync = False)

    if e.meta.stage == "init":

        e.create("SESSION", "pointing", description="pointing experiment", data={'surface':args.s})
        e.create("STREAM", name="touch", description="A time series of x,y cursor positions")

        e.create("SESSION", '', stype='random_target')

        e.meta.title="TestSet"
        e.meta.institution="University of Glasgow"
        e.meta.funder="MoreGrasp"
        e.meta.ethics="N.A."
        e.meta.authors="Antoine Loriette"
        e.meta.description="Dataset for SCI people interacting with a tabletop."
        e.meta.short_description="Dataset tabletop."

    e.meta.stage="setup"
    e.close()

if __name__ == '__main__':
    desc = 'Create the experiment log from sqlexperiment.'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-s', help='interaction plane size, [SA][234]', required=True, type=str)
    args = parser.parse_args()

    main(args)
