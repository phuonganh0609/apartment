#!/usr/bin/env python
"""Django management entry point."""

import os
import sys
import project_paths  # noqa: F401

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
