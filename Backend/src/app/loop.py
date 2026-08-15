"""A selector event loop, for running the API natively on Windows.

    uvicorn app.main:app --loop app.loop:selector_event_loop

Windows defaults to the ProactorEventLoop, which psycopg's async mode rejects. The visible
symptom is narrow and easy to miss: the API serves normally and only the LISTEN/NOTIFY backplane
dies, in a log line during startup rather than a failed request, so notifications silently stop
arriving while everything about the running app looks healthy.

**Setting the event loop policy does not fix this**, which is the non-obvious part. Since 0.36
uvicorn selects a loop through a hardcoded factory rather than the policy —
``asyncio_loop_factory`` returns ``ProactorEventLoop`` on win32 unless it is running with a
subprocess — so a ``set_event_loop_policy`` call anywhere in the application is simply ignored.
The two supported ways in are this ``--loop`` hook and ``--reload``, which sets the subprocess
flag and therefore gets a selector loop as a side effect.

Linux and macOS already use a selector loop, so this is inert there and Docker never needs it.
"""

import asyncio
import selectors
import sys


def selector_event_loop() -> asyncio.AbstractEventLoop:
    """Build the loop uvicorn will run the app on."""
    if sys.platform == "win32":
        return asyncio.SelectorEventLoop(selectors.SelectSelector())
    return asyncio.new_event_loop()
