import asyncio
import shlex
from typing import Tuple

from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError

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
    Heroku-safe Git handler.

    The repository is already deployed by Heroku,
    so do not perform runtime fetch/pull operations.
    """

    try:
        repo = Repo()

        LOGGER(__name__).info(
            "Git repository detected. Runtime Git update skipped."
        )

        return True

    except InvalidGitRepositoryError:
        LOGGER(__name__).warning(
            "Git repository not found. Runtime Git update skipped."
        )
        return False

    except GitCommandError as e:
        LOGGER(__name__).warning(
            f"Git command error: {e}. Runtime Git update skipped."
        )
        return False

    except Exception as e:
        LOGGER(__name__).warning(
            f"Git check failed: {e}. Runtime Git update skipped."
        )
        return False

