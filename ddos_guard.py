"""
Based on https://git.gay/a/ddos-guard-bypass/src/branch/master/index.js
"""

import logging
import re
import urllib.parse
from http import HTTPStatus

from aiohttp import ClientSession


async def bypass(url: str, cookies=None, *, session: ClientSession):
    if cookies is None:
        headers_1 = {
            "Accept": "text/html",
            "Accept-Language": "en-US",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "TE": "trailers",
            "DNT": "1",
        }
        async with session.get(url, headers=headers_1) as response_1:
            if response_1.status not in (HTTPStatus.OK, HTTPStatus.FORBIDDEN):
                return
            cookies = response_1.cookies

    logging.info("[ddos_guard.bypass] Parsed cookies from %r: %r", url, cookies or None)

    headers_2 = {
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Referer": url,
        "Sec-Fetch-Dest": "script",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "cross-site"
    }
    async with session.get("https://check.ddos-guard.net/check.js", cookies=cookies, headers=headers_2) as response_2:
        text = await response_2.text()

    match = re.search(r"'(?P<path>/.well-known/ddos-guard/id/\S+)'", text)
    if not match:
        return

    path = match.groupdict()["path"]
    logging.info("[ddos_guard.bypass] Retrieved path from ddos-guard's check.js: %r", path)
    url_split = list(urllib.parse.urlsplit(url))
    url_split[2] = path
    ddos_guard_url = urllib.parse.urlunsplit(url_split)

    headers_3 = {
        "Accept": "image/webp,*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Cache-Control": "no-cache",
        "Referer": url,
        "Sec-Fetch-Dest": "script",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "cross-site"
    }

    async with session.get(ddos_guard_url, cookies=cookies, headers=headers_3) as response_3:
        ddos_guard_cookies = response_3.cookies

    logging.info("[ddos_guard.bypass] Retrieved final cookies from %r: %r", ddos_guard_url, ddos_guard_cookies)
    return ddos_guard_cookies
