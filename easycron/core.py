from typing import List, Dict, Set, Callable, Union
from dataclasses import dataclass, field
from croniter import croniter
from datetime import datetime
import threading
import copy
import time


@dataclass
class CronInfo:
    cron_expr: str
    funcs: List[Callable] = field(default_factory=list)
    iter: croniter = None
    nextdt: datetime = None


_crons: Dict[str, CronInfo] = {}
_func2expr: Dict[Callable, List[str]] = {}
CRON = croniter('* * * * *')


def register(func: Callable, cron_expr: str) -> None:
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


def cancel(func: Callable) -> None:
    global _func2expr, _crons
    todrop = []
    tocancel = _func2expr.get(func, [])
    for cron_expr in tocancel:
        cron_info = _crons[cron_expr]
        funclist = cron_info.funcs
        funclist.remove(func)
        if len(funclist) == 0:
            todrop.append(cron_expr)
    for drop_cron in todrop:
        _crons.pop(drop_cron)


def cron(cron_expr: Union[str, List[str]]) -> None:
    def wrapper_func(func: Callable) -> Callable:
        global CRON
        if isinstance(cron_expr, str):
            if not CRON.is_valid(cron_expr):
                raise ValueError(f'cron expression {cron_expr} not valid')
            register(func, cron_expr)
        elif isinstance(cron_expr, list):
            for cron_expr_ in cron_expr:
                if not CRON.is_valid(cron_expr_):
                    raise ValueError(f'cron expression {cron_expr_} not valid')
                register(func, cron_expr_)
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


def _run():
    global _crons
    while True:
        now = datetime.now()
        trigger_funcs: Set[Callable] = set()
        for _, cron_info in _crons.items():
            if now >= cron_info.nextdt:
                cron_info.nextdt = cron_info.iter.get_next(datetime)
                for func in cron_info.funcs:
                    trigger_funcs.add(func)
        for func in trigger_funcs:
            func()
        if (datetime.now() - now).seconds < 1:
            time.sleep(1)


def run(block: bool = True):
    if block:
        _run()
    else:
        thread = threading.Thread(target=_run)
        thread.setDaemon(True)
        thread.start()
