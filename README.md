# pyeasycron

## Brief Intro

An easy way to make function run as cron.

## Installation

``` bash
pip3 install pyeasycron
```

## Usage

### Use as decorator

1. use `easycron.cron` as decorator

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

2. use `easycron.every` as decorator

    ``` python
    import easycron
    from datetime import datetime

    # Expected run every 15 minutes
    @easycron.every(minutes=15)
    def func1():
        print(f"in func1: {datetime.now()}")

    # Expected run every 4 hours
    @easycron.every(hours=4)
    def func2():
        print(f"in func2: {datetime.now()}")

    # Expected run every 2 days
    @easycron.every(days=2)
    def func3():
        print(f"in func3: {datetime.now()}")

    if __name__ == '__main__':
        easycron.run()
    ```

3. use `easycron.every` and `easycron.cron` mixed and stacked

    ``` python
    import easycron
    from datetime import datetime

    # Expected run when '*/3 * * * *' is satisfied
    # **OR** when '*/2 * * * *' is satisfied
    # only run **ONCE** when '*/6 * * * *'
    @easycron.cron('*/3 * * * *')
    @easycron.cron('*/2 * * * *')
    def func3():
        print(f"in func3: {datetime.now()}")


    # Expected run when '*/5 * * * *' is satisfied
    # **OR** every 2 minutes
    # only run **ONCE** when '*/10 * * * *'
    @easycron.every(minutes=2)
    @easycron.cron('*/5 * * * *')
    def func2():
        print(f"in func2: {datetime.now()}")

    # Expected run every 5 minutes
    # OR every 7 minutes
    # only run **ONCE** when meeting every 5*7=35 minutes
    @easycron.every(minutes=5)
    @easycron.every(minutes=7)
    def func1():
        print(f"in func1: {datetime.now()}")

    if __name__ == '__main__':
        easycron.run()
    ```

### Use with concurrency

As default, `easycron.run()` run multi functions in serial way \
(if several functions are triggered at the same time).

If you want to run in concurrency way, just use `concurrency=False` parameter.

``` python
import easycron
from datetime import datetime

@easycron.cron('*/2 * * * *')
def func1():
    print(f"in func1: {datetime.now()}")

if __name__ == '__main__':
    easycron.run(concurrency=False)
```

### Use without block

As default, `easycron.run()` blocks currenct process.

If you want to run in unblock way, just use `block=False` parameter.

``` python
import easycron
from datetime import datetime

@easycron.cron('*/2 * * * *')
def func1():
    print(f"in func1: {datetime.now()}")

if __name__ == '__main__':
    easycron.run(block=False)

    # do other things
    ...
```

### Use register and cancel in a common way

``` python
import easycron
from datetime import timedelta

def func1():
    print(f"in func1: {datetime.now()}")

def func2():
    print(f"in func2: {datetime.now()}")

if __name__ == '__main__':
    easycron.register(func1, interval=timedelta(minutes=3))
    easycron.register(func2, cron_expr='*/2 * * * *')

    easycron.run(block=False)
    # do other things
    ...

    easycron.cancel(func2)
    # do other things
    ...
```
