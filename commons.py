import logging
import os
import sys
from typing import List, Tuple

import requests as requests


def config_logger(verbose, log_to_stdout):
    kwargs = {}
    if not log_to_stdout:
        kwargs['filename'] = os.path.abspath(sys.argv[0]).split('.')[0] + '.log'
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="[%(asctime)s] %(levelname)s:  %(message)s",
        datefmt="%d-%m-%Y %I:%M:%S",
        **kwargs
    )


def set_limits():
    try:
        import resource
    except ImportError:
        print('Your platform does not supports setting limits for open files count', file=sys.stderr)
        print('If you see a lot of errors like "Too meny open files" pls check README.md', file=sys.stderr)
        return
    soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
    limit = hard
    while limit > soft:
        try:
            resource.setrlimit(resource.RLIMIT_NOFILE, (limit, hard))
            print(f'New limit of open files is {limit}')
            return
        except:
            limit -= ((hard - soft) / 100) or 1

    print('Can not change limit of open files, if you get a message "too many open files"')
    print(f'Current limit is: {soft}')
    print('In linux/unix/mac you should run')
    print('\t$ ulimit -n 100000')
    print('In WSL:')
    print('\t$ mylimit=10000:')
    print('\t$ sudo prlimit --nofile=$mylimit --pid $$; ulimit -n $mylimit')


def load_proxies(proxy_file: str, proxy_url: str) -> List[Tuple[str, str, int]]:
    if proxy_url:
        logging.info('Loading proxy list from %s..', proxy_url)
        proxy_data = requests.get(proxy_url).text
    elif proxy_file:
        logging.info('Loading proxy list from %s..', proxy_file)
        proxy_data = open(proxy_file).read()
    else:
        proxy_data = None
    if proxy_data:
        proxies = []
        for line in proxy_data.split():
            type_ = line.split('#')[-1]
            ip = line.split(':')[0]
            port = int(line.split(':')[-1].split('#')[0])
            proxies.append((type_, ip, port))
        logging.info('Loaded %s proxies', len(proxies))
        return proxies
    return None
