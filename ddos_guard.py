"""
Based on https://git.gay/a/ddos-guard-bypass/src/branch/master/index.js
"""

import logging
import urllib.parse
from http import HTTPStatus
from http.cookies import SimpleCookie

from aiohttp import ClientSession


async def bypass(url: str, cookies=None, *, session: ClientSession, ignore_response: bool):
    cookies = cookies or {}
    logging.debug('[ddos_guard.bypass] Started for %s', url)

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

    # sometimes DDosGuard returns only part of the cookies - bug? So, need to ask for several times for id to be there.
    i = 0
    while not (cookies and cookies.get("__ddgid")) and i < 5:
        async with session.get(url, headers=headers_1) as response_1:
            cookies.update(response_1.cookies)
        i += 1

    logging.debug("[ddos_guard.bypass] Parsed cookies from %r: %r", url, cookies or None)

    headers_2 = {
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Referer": url,
        "Sec-Fetch-Dest": "script",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "cross-site"
    }
    async with session.get("https://check.ddos-guard.net/check.js", headers=headers_2) as response_2:
        cookies_2 = response_2.cookies

    logging.debug("[ddos_guard.bypass] Parsed cookies from check.js: %r", cookies_2)

    domain = urllib.parse.urlparse(url).netloc
    for c in cookies_2:
        cookies_2[c]["domain"] = domain

    ddos_guard_cookies = SimpleCookie()
    ddos_guard_cookies.update(cookies)
    ddos_guard_cookies.update(cookies_2)

    logging.debug("[ddos_guard.bypass] Retrieved final cookies for %r: %r", url, ddos_guard_cookies)

    async with session.get(url, cookies=ddos_guard_cookies, headers=headers_1) as response_3:
        if response_3.status == HTTPStatus.OK:
            logging.info("[ddos_guard.bypass] Protection was bypassed for %r: %r", url, ddos_guard_cookies)
            if not ignore_response:
                await response_3.text()
        if response_3.status != HTTPStatus.OK:
            logging.warning("[ddos_guard.bypass] Protection was NOT bypassed for %r: %r", url, ddos_guard_cookies)

    return ddos_guard_cookies, response_3
