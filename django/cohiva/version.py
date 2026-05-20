import os

__version__ = "1.4.4"

git_tag = os.getenv("COHIVA_GIT_TAG", None)
git_commit = os.getenv("COHIVA_GIT_COMMIT", None)
