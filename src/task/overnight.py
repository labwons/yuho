try:
    from ..common.logger import Log
    from ..common.calendar import Calendar
    from ..module.wise.generic import Groups
    from .macro.generic import Macro
except ImportError:
    from dev.common.calendar import Calendar
    from dev.common.logger import Log
    from dev.module.wise.generic import Groups
    from dev.task.macro.generic import Macro


Log.set_title(f"[L￦][LOG] OVERNIGHT UPDATE @{Calendar}")
runGroup = Groups(offline=False).dump()
macro = Macro()
macro.dump()
Log.send()