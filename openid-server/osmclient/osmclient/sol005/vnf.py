# Copyright 2018 Telefonica
#
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
OSM vnf API handling
"""

from osmclient.common import utils
from osmclient.common.exceptions import NotFound
import logging
import json


class Vnf(object):
    def __init__(self, http=None, client=None):
        self._http = http
        self._client = client
        self._logger = logging.getLogger("osmclient")
        self._apiName = "/nslcm"
        self._apiVersion = "/v1"
        self._apiResource = "/vnfrs"
        self._apiBase = "{}{}{}".format(
            self._apiName, self._apiVersion, self._apiResource
        )

    def list(self, ns=None, filter=None):
        """Returns a list of VNF instances"""
        self._logger.debug("")
        self._client.get_token()
        filter_string = ""
        if filter:
            filter_string = "?{}".format(filter)
        if ns:
            ns_instance = self._client.ns.get(ns)
            if filter_string:
                filter_string += ",nsr-id-ref={}".format(ns_instance["_id"])
            else:
                filter_string = "?nsr-id-ref={}".format(ns_instance["_id"])
        _, resp = self._http.get2_cmd("{}{}".format(self._apiBase, filter_string))
        # print('RESP: {}'.format(resp))
        if resp:
            return json.loads(resp)
        return list()

    def get(self, name):
        """Returns a VNF instance based on name or id"""
        self._logger.debug("")
        self._client.get_token()
        if utils.validate_uuid4(name):
            for vnf in self.list():
                if name == vnf["_id"]:
                    return vnf
        else:
            for vnf in self.list():
                if name == vnf.get("name"):
                    return vnf
        raise NotFound("vnf {} not found".format(name))

    def get_individual(self, name):
        self._logger.debug("")
        self._client.get_token()
        vnf_id = name
        if not utils.validate_uuid4(name):
            for vnf in self.list():
                if name == vnf["name"]:
                    vnf_id = vnf["_id"]
                    break
        try:
            _, resp = self._http.get2_cmd("{}/{}".format(self._apiBase, vnf_id))
            # print('RESP: {}'.format(resp))
            if resp:
                return json.loads(resp)
        except NotFound:
            raise NotFound("vnf '{}' not found".format(name))
        raise NotFound("vnf '{}' not found".format(name))
