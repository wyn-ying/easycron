from typing import List, Dict, Set, Callable, Union
from dataclasses import dataclass, field
from croniter import croniter
from datetime import datetime, timedelta
import threading
import copy
import time


@dataclass
class CronInfo:
    cron_expr: str
    funcs: List[Callable] = field(default_factory=list)
    iter: croniter = None
    nextdt: datetime = None

    def __repr__(self) -> str:
        reprs = [f'cron_expr: {self.cron_expr}', f'iter: {self.iter}',
                 f'nextdt: {self.nextdt}', f'funcs:{[f for f in self.funcs]}']
        return f'CronInfo: {{{", ".join(reprs)}}}'


@dataclass
class IntvInfo:
    interval: timedelta
    funcs: List[Callable] = field(default_factory=list)
    nextdt: datetime = None

    def __repr__(self) -> str:
        reprs = [f'interval(seconds): {self.interval.seconds}',
                 f'nextdt: {self.nextdt}', f'funcs: {[f for f in self.funcs]}']
        return f'IntvInfo: {{{", ".join(reprs)}}}'


_crons: Dict[str, CronInfo] = {}
_func2expr: Dict[Callable, List[str]] = {}
CRON = croniter('* * * * *')
_intvs: Dict[timedelta, IntvInfo] = {}
_func2tmdt: Dict[Callable, List[timedelta]] = {}


def register(func: Callable,
             cron_expr: Union[str, None] = None,
             interval: Union[timedelta, None] = None) -> None:
    if cron_expr is None and interval is None:
        raise ValueError('One of ("cron_expr", "interval") should be set')
    if cron_expr is not None and interval is not None:
        raise ValueError('("cron_expr", "interval") should be set only one')
    if cron_expr is not None:
        global _crons, _func2expr
        if cron_expr not in _crons.keys():
            cron_info = CronInfo(cron_expr, [])
            cron_info.iter = croniter(cron_expr, datetime.now())
            cron_info.nextdt = cron_info.iter.get_next(datetime)
            _crons[cron_expr] = cron_info
        if func not in _crons[cron_expr].funcs:
            _crons[cron_expr].funcs.append(func)
        if func not in _func2expr.keys():
            _func2expr[func] = []
        if cron_expr not in _func2expr[func]:
            _func2expr[func].append(cron_expr)
    if interval is not None:
        global _intvs, _func2tmdt
        if interval not in _intvs.keys():
            intv_info = IntvInfo(interval, [])
            now = datetime.now().replace(second=0, microsecond=0)
            intv_info.nextdt = now + interval
            _intvs[interval] = intv_info
        if func not in _intvs[interval].funcs:
            _intvs[interval].funcs.append(func)
        if func not in _func2tmdt.keys():
            _func2tmdt[func] = []
        if interval not in _func2tmdt[func]:
            _func2tmdt[func].append(interval)


def cancel(func: Callable) -> None:
    global _func2expr, _crons, _intvs, _func2tmdt
    todrop = []
    tocancel = _func2expr.pop(func, [])
    for cron_expr in tocancel:
        cron_info = _crons[cron_expr]
        funclist = cron_info.funcs
        funclist.remove(func)
        if len(funclist) == 0:
            todrop.append(cron_expr)
    for drop_cron in todrop:
        _crons.pop(drop_cron, None)

    todrop = []
    tocancel = _func2tmdt.pop(func, [])
    for interval in tocancel:
        intv_info = _intvs[interval]
        funclist = intv_info.funcs
        funclist.remove(func)
        if len(funclist) == 0:
            todrop.append(intv_info)
    for drop_intv in todrop:
        _intvs.pop(drop_intv, None)


def cron(cron_expr: Union[str, List[str]]) -> None:
    def wrapper_func(func: Callable) -> Callable:
        global CRON
        if isinstance(cron_expr, str):
            if not CRON.is_valid(cron_expr):
                raise ValueError(f'cron expression {cron_expr} not valid')
            register(func, cron_expr=cron_expr)
        elif isinstance(cron_expr, list):
            for cron_expr_ in cron_expr:
                if not CRON.is_valid(cron_expr_):
                    raise ValueError(f'cron expression {cron_expr_} not valid')
                register(func, cron_expr=cron_expr_)
        return func

    return wrapper_func


def every(days: Union[int, None] = None,
          hours: Union[int, None] = None,
          minutes: Union[int, None] = None) -> None:
    if sum([1 if p is not None else 0 for p in (days, hours, minutes)]) != 1:
        raise ValueError('("days", "hours", "minutes") should be set only one')

    def wrapper_func(func: Callable) -> Callable:
        if days is not None:
            interval = timedelta(days=days)
        elif hours is not None:
            interval = timedelta(hours=hours)
        elif minutes is not None:
            interval = timedelta(minutes=minutes)
        register(func, interval=interval)
        return func

    return wrapper_func


def get_croninfo() -> Dict[str, CronInfo]:
    global _crons
    crons = copy.deepcopy(_crons)
    return crons


def get_func2expr() -> Dict[Callable, List[str]]:
    global _func2expr
    func2expr = copy.deepcopy(_func2expr)
    return func2expr


def get_intvinfo() -> Dict[timedelta, IntvInfo]:
    global _intvs
    intvs = copy.deepcopy(_intvs)
    return intvs


def get_func2tmdt() -> Dict[Callable, List[timedelta]]:
    global _func2tmdt
    func2tmdt = copy.deepcopy(_func2tmdt)
    return func2tmdt


def _run(concurrency: bool):
    global _crons, _intvs
    while True:
        now = datetime.now()
        trigger_funcs: Set[Callable] = set()
        for _, cron_info in _crons.items():
            if now >= cron_info.nextdt:
                cron_info.nextdt = cron_info.iter.get_next(datetime)
                for func in cron_info.funcs:
                    trigger_funcs.add(func)
        for _, intv_info in _intvs.items():
            if now >= intv_info.nextdt:
                new_nextdt = intv_info.nextdt + intv_info.interval
                intv_info.nextdt = new_nextdt.replace(second=0, microsecond=0)
                for func in intv_info.funcs:
                    trigger_funcs.add(func)
        if not concurrency:
            for func in trigger_funcs:
                func()
        else:
            threads: List[threading.Thread] = []
            for func in trigger_funcs:
                thread = threading.Thread(target=func)
                threads.append(thread)
                thread.start()
            for thread in threads:
                thread.join()

        if (datetime.now() - now).seconds < 1:
            time.sleep(1)


def run(block: bool = True, concurrency: bool = False):
    if block:
        _run(concurrency)
    else:
        thread = threading.Thread(target=_run, args=(concurrency,))
        thread.setDaemon(True)
        thread.start()
