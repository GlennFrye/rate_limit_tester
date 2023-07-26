#!/usr/bin/env python3

"""
rate_limit_test.py
A simple tool to test rate limiting of a WAF (web application firewall).
"""

import argparse
import threading
import pprint
import requests

FINAL_REQUEST_COUNT = 0

UNEXPECTED_RESP_CODE_RECEIVED = False
UNEXPECTED_RESP_CODE_LOCK = threading.Lock()

RESP_CODE_TRACKER = dict()
TRACKER_LOCK = threading.Lock()


def do_request(url: str):
    """
    Sends an HTTP request and tracks the response code.
    """
    global FINAL_REQUEST_COUNT
    global UNEXPECTED_RESP_CODE_RECEIVED
    global RESP_CODE_TRACKER

    # TODO - default to HEAD request to alleviate overhead of large responses; make it configurable
    resp = requests.get(url)

    # TODO - let expected response code be configurable
    if resp.status_code == 200:
        print(".", end='')
    else:
        print("!", end='')
        with UNEXPECTED_RESP_CODE_LOCK:
            if not UNEXPECTED_RESP_CODE_RECEIVED:
                print(resp.status_code)
                UNEXPECTED_RESP_CODE_RECEIVED = True

    with TRACKER_LOCK:
        if resp.status_code in RESP_CODE_TRACKER:
            RESP_CODE_TRACKER[resp.status_code] += 1
        else:
            RESP_CODE_TRACKER[resp.status_code] = 1

    FINAL_REQUEST_COUNT += 1  # increments are thread-safe


def test_rate_limit(url: str, tries: int):
    threads = []
    for _ in range(0, tries):
        thread = threading.Thread(target=do_request, args=(url,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    print()


def configure_args() -> argparse.ArgumentParser:
    """ Centralize the command line arguments configuration to this method """
    arg_parser = argparse.ArgumentParser(
        description='A handy script to test rate limiting on your web application firewall.'
    )
    arg_parser.add_argument('-u',
                            '--url',
                            required=True,
                            help='destination URL to be tested, must be HTTP or HTTPS')
    arg_parser.add_argument('-a',
                            '--attempts',
                            required=True,
                            type=int,
                            help='total number of requests to be sent, must be evenly divisible by batch size')
    arg_parser.add_argument('-b',
                            '--batch-size',
                            required=False,
                            default=100,
                            type=int,
                            help='default 100, specifies maximum concurrent requests for multithreading, must be '
                                 'less than or equal to attempts, and must be a factor of attempts')
    return arg_parser


def parse_args(args: argparse.ArgumentParser) -> argparse.Namespace:
    return args.parse_args()


def validate_args(args: dict) -> dict:
    attempts = args['attempts']
    batch_size = args['batch_size']

    if attempts < 1 or batch_size < 1 or attempts < batch_size:
        msg = """
        Invalid argument:
            Attempts and batch size must be greater than zero.
            Attempts must be greater than or equal to batch size."""
        raise argparse.ArgumentTypeError(msg)

    # TODO - allow more flexibility here, rather than requiring batch_size to be a factor of attempts
    if attempts % batch_size != 0:
        msg = """
        Invalid argument:
            Batch size must be a factor of attempts.
            example: attempts=10 and batch_size=5 is acceptable,
                     but attempts=10 and batch_size=6 is not."""
        raise argparse.ArgumentTypeError(msg)

    return args


def main(url: str, attempts: int, batch_size: int) -> None:
    print("\n"
          "Note: '.'=200 response, and '!'=non-200 response.\n"
          "      The script will print the response code of the first non-200 response.\n")
    print(f"number of requests to generate: {attempts}")
    print(f"target: {url}\n")

    loops = attempts // batch_size

    for _ in range(0, loops):
        test_rate_limit(url, batch_size)

    print("\n"
          "Done\n"
          f"    initial number of requests configured: {attempts}\n"
          f"    total number of requests generated: {FINAL_REQUEST_COUNT}\n"
          "\n"
          "Request breakdown:")
    pprint.PrettyPrinter(indent=4).pprint(RESP_CODE_TRACKER)


if __name__ == '__main__':
    configured_args = configure_args()
    parsed_args = parse_args(configured_args)
    validated_args = validate_args(vars(parsed_args))
    main(validated_args['url'],
         validated_args['attempts'],
         validated_args['batch_size'])
