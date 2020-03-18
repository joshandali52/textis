"""
@author: Michael Gau, Joshua Peter Handali, Johannes Schneider (in alphabetic order)
@institution: University of Liechtenstein, Fuerst-Franz-Josef Strasse 21, 9490 Vaduz, Liechtenstein
@funding: European Commission, part of an Erasmus+ Project (Project Reference: 2017-1-LI01-KA203-000083)
@copyright: Copyright (c) 2020, Michael Gau, Joshua Peter Handali, Johannes Schneider
@license : BSD-2-Clause

When using (any part) of this software, please cite our paper:
[JOBADS PAPER] 
"""

#!/usr/bin/env python
import os
import sys


if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webapp.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
