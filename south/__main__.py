from south.fr24poller import Fr24Poller
from south.coucher import Coucher
from south.printer import printer
from south.tweeter import Tweeter
from bunch import bunchify
import argparse
import yaml
import sys
import logging

def main(args=None):
    if args is None:
        args = sys.argv[1:]

    #logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(level=logging.WARN)

    pargs = parse_arguments(args)
    config = parse_config(pargs.config) 

    poller = Fr24Poller(**config.poller)

    # register handlers
    #poller.handlers.append(printer)
    
    coucher = Coucher(**config.coucher)
    poller.handlers.append(coucher.handle)
    
    tweeter = Tweeter(**config.twitter)
    poller.handlers.append(tweeter.tweet)

    poller.start()


def parse_arguments(args):
    parser = argparse.ArgumentParser(description='Launch south')
    parser.add_argument('-c', '--config', default='config.yaml')
    return parser.parse_args(args)

def parse_config(config_file):
    f = file(config_file, 'r')
    y = yaml.safe_load(f)
    return bunchify(y['config'])

if __name__ == "__main__":
    main()
