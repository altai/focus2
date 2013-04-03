# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Focus2
# Copyright (C) 2012 Grid Dynamics Consulting Services, Inc
# All Rights Reserved
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program. If not, see
# <http://www.gnu.org/licenses/>.

import datetime

from jinja2 import filters


# correct implementation for Jinja2 buggy function
# github.com/mitsuhiko/jinja2/commit/95b1d600780166713acfe05b18266e5e83dfa9a9
def do_filesizeformat(value, binary=True, exactly=False):
    """Format the value like a 'human-readable' file size (i.e. 13 kB,
    4.1 MB, 102 Bytes, etc).  Per default decimal prefixes are used (Mega,
    Giga, etc.), if the second parameter is set to `True` the binary
    prefixes are used (Mebi, Gibi).
    """
    bytes = float(value)
    base = binary and 1024 or 1000
    prefixes = [
        (binary and "KiB" or "kB"),
        (binary and "MiB" or "MB"),
        (binary and "GiB" or "GB"),
        (binary and "TiB" or "TB"),
        (binary and "PiB" or "PB"),
        (binary and "EiB" or "EB"),
        (binary and "ZiB" or "ZB"),
        (binary and "YiB" or "YB")
    ]
    if bytes == 1:
        return "1 Byte"
    elif bytes < base:
        return "%d Bytes" % bytes
    else:
        for i, prefix in enumerate(prefixes):
            unit = base ** (i + 1)
            if bytes < unit * base:
                break
        return "%.1f %s%s" % (
            (bytes / unit), prefix,
            (" (%d Bytes)" % bytes if exactly else ""))


def str_to_datetime(dtstr):
    """
    Convert string to datetime.datetime. String should be in ISO 8601 format.
    The function raises ``ValueError`` for invalid date string.
    """
    if not dtstr:
        return None
    if dtstr.endswith("Z"):
        dtstr = dtstr[:-1]
    for fmt in ("%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%dT%H:%M:%S.%f",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d %H:%M:%S.%f"):
        try:
            return datetime.datetime.strptime(dtstr, fmt)
        except ValueError:
            pass
    raise ValueError("Not ISO 8601 format date: %s" % dtstr)


def do_datetimeformat(value, format, default=""):
    return str_to_datetime(value).strftime(format) if value else default


def do_diskformat(value):
    fmt = {
        "aki": "Amazon kernel image",
        "ari": "Amazon ramdisk image",
        "ami": "Amazon machine image",
    }
    return fmt.get(value, value)


def image_spawnable(image):
    return image["container-format"] not in ("ari", "aki")


def setup_env(env):
    env.filters["filesizeformat"] = do_filesizeformat
    env.filters["datetimeformat"] = do_datetimeformat
    env.filters["diskformat"] = do_diskformat
    env.tests["image_spawnable"] = image_spawnable
