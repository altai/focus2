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

import math

import flask


class Pagination(object):
    """
    Paginator for search results.

    Usage:

    >>> data = range(1, 22)
    >>> per_page = 5
    >>> p = Pagination(1, len(data), per_page)
    >>> assert p.pages == 5
    >>> assert not p.has_prev
    >>> assert p.has_next
    >>> assert list(p.iter_pages()) == [1, 2, 3, 4, 5]
    >>> assert p.limit == per_page
    >>> assert p.offset == 0

    Based on snippet http://flask.pocoo.org/snippets/44/.
    """
    def __init__(self, page, total_count, per_page=20):
        self.page = int(page)
        self.per_page = int(per_page)
        self.total_count = int(total_count)
        if (page - 1) * per_page > total_count:
            flask.abort(404)

    @property
    def pages(self):
        return int(math.ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        last = 0
        for num in xrange(1, self.pages + 1):
            yep = (num <= left_edge or
                   (num > self.page - left_current - 1
                    and num < self.page + right_current)
                   or num > self.pages - right_edge)
            if yep:
                if last + 1 != num:
                    yield None
                yield num
                last = num

    @property
    def offset(self):
        return (self.page - 1) * self.per_page

    @property
    def limit(self):
        return self.per_page
