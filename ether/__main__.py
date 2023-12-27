import asyncio
import functools
import signal
import sys
from argparse import Namespace

import discord
import nest_asyncio

from ether.core.bot import Ether

nest_asyncio.apply()

from ether.api.server import ServerThread
from ether.core.config import config
from ether.core.constants import ExitCodes
from ether.core.logging import log

threads = []
subprocesses = []


#
#               Æther - Discord Bot
#
#              Made by  Atomic Junky
#


# Thanks to Cog-Creators/Red-DiscordBot, I reuse a lot of code from there


async def run_bot(ether: Ether, cli_flags: Namespace | None = None):
    token = config.bot.get("token")

    try:
        await ether.start(token)
    except discord.LoginFailure:
        log.critical("This token doesn't seem to be valid.")
        sys.exit(ExitCodes.CONFIGURATION_ERROR)
    except discord.PrivilegedIntentsRequired:
        log.critical("Ether requires Privileged Intents to be enabled.\n")
        sys.exit(ExitCodes.CONFIGURATION_ERROR)

    return None


async def shutdown_handler(ether, signal_type=None, exit_code=None):
    if signal_type:
        log.info("%s received. Quitting...", signal_type.name)
    elif exit_code is None:
        log.info("Shutting down from unhandled exception")

    try:
        if not ether.is_closed():
            await ether.close()
    finally:
        # Then cancels all outstanding tasks other than ourselves
        pending = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        [task.cancel() for task in pending]
        await asyncio.gather(*pending, return_exceptions=True)

        # Kill all threads
        for thread in threads:
            thread.kill()

    sys.exit(ExitCodes.SHUTDOWN)


def global_exception_handler(ether, loop, context):
    """
    Logs unhandled exceptions in other tasks
    """
    exc = context.get("exception")
    # These will get handled later when it *also* kills loop.run_forever
    if exc is not None and isinstance(exc, (KeyboardInterrupt, SystemExit)):
        return

    loop.default_exception_handler(context)


def ether_exception_handler(ether, ether_task: asyncio.Future):
    try:
        ether_task.result()
    except (SystemExit, KeyboardInterrupt, asyncio.CancelledError):
        pass
    except discord.errors.HTTPException as e:
        log.critical(f"An HTTP request failed with the status {e.status}.")
        log.critical(f"Code: {e.code}")
        log.critical(e.text)

        log.warning("Attempting to die as gracefully as possible...")
        asyncio.create_task(shutdown_handler(ether))
    except Exception as e:
        log.critical(
            "The main bot task didn't handle an exception and has crashed", exc_info=e
        )
        log.warning("Attempting to die as gracefully as possible...")
        asyncio.create_task(shutdown_handler(ether))


def main():
    ether = Ether(description="Ether V1", dm_help=True)

    try:
        server_thread = ServerThread(port=config.server.get("port"), bot=ether)
        threads.append(server_thread)
        server_thread.start()

        loop = asyncio.new_event_loop()

        exc_handler = functools.partial(global_exception_handler, ether)
        loop.set_exception_handler(exc_handler)

        fut = loop.create_task(run_bot(ether))
        e_exc_handler = functools.partial(ether_exception_handler, ether)
        fut.add_done_callback(e_exc_handler)
        loop.run_forever()
    except KeyboardInterrupt:
        log.warning(
            "Please do not use Ctrl+C to Shutdown Æther! (attempting to die gracefully...)"
        )
        log.error("Received KeyboardInterrupt, treating as interrupt")
        if ether is not None:
            loop.run_until_complete(shutdown_handler(ether, signal.SIGINT))
    except SystemExit as exc:
        exit_code = int(exc.code)
        try:
            exit_code_name = ExitCodes(exit_code).name
        except ValueError:
            exit_code_name = "UNKNOWN"
        log.info("Shutting down with exit code: %s (%s)", exit_code, exit_code_name)
        if ether is not None:
            loop.run_until_complete(shutdown_handler(ether, None, exc.code))
    except Exception as exc:  # Non standard case.
        log.exception("Unexpected exception (%s): ", type(exc), exc_info=exc)
        if ether is not None:
            loop.run_until_complete(shutdown_handler(ether, None, ExitCodes.CRITICAL))
    finally:
        # Kill all threads
        log.info("killing all threads")
        for thread in threads:
            thread.kill()

        loop.run_until_complete(loop.shutdown_asyncgens())

        log.info("Please wait, cleaning up a bit more")
        loop.run_until_complete(asyncio.sleep(2))
        asyncio.set_event_loop(None)
        loop.stop()
        loop.close()

    sys.exit(ExitCodes.SHUTDOWN)


if __name__ == "__main__":
    main()
