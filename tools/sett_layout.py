#!/usr/bin/env python3
"""Legacy import compatibility; new code uses workspace_layout."""

from workspace_layout import MEMBERS, NOT_A_WORKSPACE, WorkspaceLayout, refuse_unknown

NOT_A_SETT = NOT_A_WORKSPACE


class SettLayout(WorkspaceLayout):
    """Preserve the legacy layout class and its root predicate."""

    @property
    def is_sett_root(self):
        return self.is_workspace_root
