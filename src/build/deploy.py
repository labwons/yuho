try:
    from ..render.config import minify
    from ..render import (
        bubble,
        macro,
        marketmap
    )
except ImportError:
    from src.render.config import minify
    from src.render import (
        bubble,
        macro,
        marketmap
    )


if __name__ == "__main__":

    TESTMODE = True

    minify.css()
    minify.js()

    bubble.render(test_mode=TESTMODE)
    macro.render(test_mode=TESTMODE)
    marketmap.render(test_mode=TESTMODE)