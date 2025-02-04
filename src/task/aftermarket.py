try:
    from ..common.calendar import Calendar
    from ..common.logger import Log
    from .basis.generic import Basis
    from .treemap.generic import MarketMap
    from .bubble.generic import Bubble
except ImportError:
    from dev.common.calendar import Calendar
    from dev.common.logger import Log
    from dev.task.basis.generic import Basis
    from dev.task.treemap.generic import MarketMap
    from dev.task.bubble.generic import Bubble

Log.set_title(f"[L￦][LOG] AFTERMARKET UPDATE @{Calendar}")
basis = Basis(offline=False)
basis.dump()

marketMap = MarketMap(basis)
marketMap.dump()

bubble = Bubble(basis)
bubble.dump()
Log.send()