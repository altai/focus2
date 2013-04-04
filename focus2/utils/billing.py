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

import flask

from openstackclient_base.exceptions import NotFound


class BillingHelper(object):

    def __init__(self, altai_api, billing_client):
        self.altai_api = altai_api
        self.billing_client = billing_client

    @staticmethod
    def _calc_cost(res):
        '''
        Currently one level of folded data.
        '''
        cost = res.get("cost", 0.0)
        for child in res.get("children", ()):
            cost += BillingHelper._calc_cost(child)
        return cost

    @staticmethod
    def compact_bill(resources):
        '''
        Return list of resources which do not have parents, in descending
        chronological order.
        Resourced with parents must be grouped under their parents.
        Cost must be calculated for parents based on their children cost.
        '''
        # build dict of resources
        res_by_id = {}
        for res in resources:
            res_by_id[res['id']] = res
        # iterate through non-orphans
        for res in filter(lambda x: x['parent_id'] not in [None, 0],
                          resources):
            #  add non-orphan to 'children' of it's parent in dict of resources
            parent = res_by_id[res['parent_id']]
            if not 'children' in parent:
                parent['children'] = []
            parent['children'].append(res)
        # iterate through orphans
        for res in filter(lambda x: x['parent_id'] in [None, 0], resources):
            orphan = res_by_id[res['id']]
            #  calculate cost based on children recorded in dict of resources
            #  change cost in resource in the dict
            orphan['cost'] = BillingHelper._calc_cost(orphan)
        # return orphans sorted chronologically
        return map(
            lambda res: res_by_id[res['id']],
            sorted(
                filter(
                    lambda x: x['parent_id'] in [None, 0],
                    resources),
                key=lambda x: x['created_at'],
                reverse=True))

    # TODO: add local volume support
    def add_details(self, resources):
        '''
        For every orphan resource add verbose name and brief info url.
        '''
        processors = (
            ('nova/instance', self.altai_api.instances.list(
                    filter={"my-projects": True})["instances"],
             'instances.show'),
            ('glance/image', self.altai_api.images.list(
                    filter={"my-projects": True})["images"],
             'images.show'),
        )

        def process(objs, info, endpoint, arg):
            ref = dict(((x['name'], x) for x in objs))
            result = {}
            # some objs will lack detailed info. it is not a problem
            # it is solved during presentation to user
            informative = [x._info
                           for x in info
                           if unicode(x.id) in ref.keys()]
            for x in informative:
                actual = copy.deepcopy(ref[unicode(x['id'])])
                actual['detailed'] = x
                actual['detailed']['focus_url'] = flask.url_for(
                    endpoint, id=x['id'])
                result[(actual['id'], actual['rtype'])] = actual
            return result

        def filter_type(resource_type):
            return filter(
                lambda x:
                    x['rtype'] == resource_type and x['parent_id'] is None,
                resources
            )

        for rtype, model, endpoint in processors:
            rsrc_list = filter_type(rtype)
            details_list = dict(((x["id"], x) for x in model))
            for rsrc in rsrc_list:
                # yes, `id' is stored as `name' in billing
                rsrc_id = rsrc["name"]
                try:
                    details = details_list[rsrc_id]
                except KeyError:
                    pass
                else:
                    rsrc["details"] = details
                    rsrc["details"]["url"] = flask.url_for(
                        endpoint, id=rsrc_id)

        return resources

    def tariff_list(self):
        tariffs = {
            "glance/image": 1.0,
            "memory_mb": 1.0,
            "vcpus": 1.0,
            "nova/volume": 1.0,
            "local_gb": 1.0,
        }
        tariffs.update(self.billing_client.tariff.list())
        return tariffs

    def report(self, **kw):
        # list with tenant_id as ['name']
        projects = self.altai_api.me.get_current_user()["projects"]
        resources = []
        for pr in projects:
            try:
                resources += self.billing_client.report.list(
                    account_name=pr["id"], **kw)["accounts"][0]["resources"]
            except (NotFound, IndexError):
                pass
        resources = self.compact_bill(resources)
        return resources
