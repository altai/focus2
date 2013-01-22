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


import re


def transform_search_query(query, default_name):
    """
    Parse query text into list of names and values of search parameters.

    Usage:

    >>> assert transform_search_query('', 'id:in') == {}
    >>> assert (transform_search_query('foo:eq=bar name:in=buzz', 'id:in') ==
    ...     {'foo:eq': 'bar', 'name:in': 'buzz'})
    ...
    >>> assert (transform_search_query(
    ...     'long way to go foo:eq=bar name:in=buzz', 'id:in') ==
    ...     {'id:in': 'long way to go', 'foo:eq': 'bar', 'name:in': 'buzz'})
    ...

    :param query: query text from search form
    :param default_name: name of arg for "free" part of search query
    :return: dictionary of search terms
    """
    # TODO(aababilov): support shortcuts such as id=13 for id:eq=13 etc.
    results = {}
    query = " " + query
    values = re.split(r'\S+:\S+=', query)
    if len(values):
        h = values[0].strip()
        if h:
            results[default_name] = h
        del(values[0])
        names = re.findall(r'\S+:\S+=', query)
        for n, v in zip(names, values):
            v = v.strip()
            m = re.search(r'''^('+|"+)(.*)\1$''', v)
            results[n[:-1]] = m and m.group(2) or v
    return results
