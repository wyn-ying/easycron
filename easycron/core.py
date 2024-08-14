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
CRON = croniter('* * * * *')


def register(func: Callable, cron_expr: str) -> None:
    global _crons
    if cron_expr not in _crons.keys():
        _crons[cron_expr] = CronInfo(cron_expr, [])
    _crons[cron_expr].funcs.append(func)


def cancel(func: Callable) -> None:
    global _crons
    todrop = []
    for cron_expr, cron_info in _crons.items():
        funclist = cron_info.funcs
        if func in funclist:
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


def _run():
    global _crons
    while True:
        now = datetime.now()
        trigger_funcs: Set[Callable] = set()
        for cron_expr, cron_info in _crons.items():
            if cron_info.iter is None:
                cron_info.iter = croniter(cron_expr, now)
                cron_info.nextdt = cron_info.iter.get_next(datetime)
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
