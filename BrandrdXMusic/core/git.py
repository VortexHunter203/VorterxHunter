import asyncio
import shlex
from typing import Tuple

from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError

import config

from ..logging import LOGGER


def install_req(cmd: str) -> Tuple[str, str, int, int]:
    async def install_requirements():
        args = shlex.split(cmd)

        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.communicate()

        return (
            stdout.decode("utf-8", "replace").strip(),
            stderr.decode("utf-8", "replace").strip(),
            process.returncode,
            process.pid,
        )

    return asyncio.get_event_loop().run_until_complete(
        install_requirements()
    )


def git():
    """
    Git updater.

    On Heroku, the application is already deployed from the repository.
    Runtime GitHub fetch/pull is disabled to prevent authentication errors
    such as:

        fatal: could not read Username for 'https://github.com'

    Git updates can still be performed manually during deployment.
    """

    try:
        repo = Repo()

        LOGGER(__name__).info(
            "Git repository detected. Runtime Git update skipped."
        )

        return

    except InvalidGitRepositoryError:
        LOGGER(__name__).warning(
            "Git repository not found. Runtime Git update skipped."
        )
        return

    except GitCommandError as e:
        LOGGER(__name__).warning(
            f"Git command error: {e}. Runtime Git update skipped."
        )
        return

    except Exception as e:
        LOGGER(__name__).warning(
            f"Git initialization check failed: {e}. "
            "Runtime Git update skipped."
        )
        return
