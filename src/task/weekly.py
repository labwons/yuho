try:
    from ..fetch.fng.generic import Stat
except ImportError:
    from dev.module.fng.generic import Stat


runStat = Stat()
runStat.dataUpdate()
runStat.dump()