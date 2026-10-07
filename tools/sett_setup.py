#!/usr/bin/env python3
"""Legacy import compatibility for workspace_setup."""

from workspace_setup import *  # noqa: F401,F403
from workspace_setup import (  # noqa: F401
    contains_workspace_root as contains_sett_root,
    first_workspace_ancestor as first_sett_ancestor,
)
