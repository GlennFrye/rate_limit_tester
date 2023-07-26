# rate_limit_tester
A simple tool to test rate limiting on your web application firewall.

Feedback and pull requests are always welcomed!

## Installation
Assuming you already have [Python 3 installed](https://www.python.org/downloads/),
simply clone the repo and run `pip install -r requirements.txt` to install dependencies.

## Usage
```text
usage: rate_limit_tester.py [-h] -u URL -a ATTEMPTS [-b BATCH_SIZE]

A handy script to test rate limiting on your web application firewall.

options:
  -h, --help            show this help message and exit
  -u URL, --url URL     destination URL to be tested, must be HTTP or HTTPS
  -a ATTEMPTS, --attempts ATTEMPTS
                        total number of requests to be sent, must be evenly divisible by batch size
  -b BATCH_SIZE, --batch-size BATCH_SIZE
                        default 100, specifies maximum concurrent requests for multithreading, must be less than or equal to attempts, and
                        must be a factor of attempts
```

## TODOs
There are some TODOs in the code where things can be improved or made more flexible.
In addition to that, it would be nice to package this up into a macOS and/or Linux
executable so folks aren't forced to install Python, perhaps using [PyInstaller](https://pyinstaller.org/en/stable/).

## License
See LICENSE file.
