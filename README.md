# pyeasycron

## Brief Intro

An easy way to make function run as cron.

## Installation

``` bash
pip3 install pyeasycron
```

## Usage

``` python
import easycron
from datetime import datetime

# Expected run when '*/2 * * * *' is satisfied
@easycron.cron('*/2 * * * *')
def func1():
    print(f"in func1: {datetime.now()}")

# Expected run when one of ['*/5 8 * * *', '7,14,21 9 * * *'] is satisfied
@easycron.cron(['*/5 8 * * *', '7,14,21 9 * * *'])
def func2():
    print(f"in func2: {datetime.now()}")

if __name__ == '__main__':
    easycron.run()
```
