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
#

"""
OSM Repo API handling
"""

from osmclient.common import utils
from osmclient.common.exceptions import ClientException
from osmclient.common.exceptions import NotFound
import json


class Repo(object):
    def __init__(self, http=None, client=None):
        self._http = http
        self._client = client
        self._apiName = "/admin"
        self._apiVersion = "/v1"
        self._apiResource = "/k8srepos"
        self._apiBase = "{}{}{}".format(
            self._apiName, self._apiVersion, self._apiResource
        )

    def create(self, name, repo):
        self._client.get_token()
        http_code, resp = self._http.post_cmd(
            endpoint=self._apiBase, postfields_dict=repo
        )
        # print 'HTTP CODE: {}'.format(http_code)
        # print 'RESP: {}'.format(resp)
        # if http_code in (200, 201, 202, 204):
        if resp:
            resp = json.loads(resp)
        if not resp or "id" not in resp:
            raise ClientException("unexpected response from server - {}".format(resp))
        print(resp["id"])
        # else:
        #    msg = ""
        #    if resp:
        #        try:
        #            msg = json.loads(resp)
        #        except ValueError:
        #            msg = resp
        #    raise ClientException("failed to add repo {} - {}".format(name, msg))

    def update(self, name, repo):
        self._client.get_token()
        repo_dict = self.get(name)
        http_code, resp = self._http.put_cmd(
            endpoint="{}/{}".format(self._apiBase, repo_dict["_id"]),
            postfields_dict=repo,
        )
        # print 'HTTP CODE: {}'.format(http_code)
        # print 'RESP: {}'.format(resp)
        # if http_code in (200, 201, 202, 204):
        #    pass
        # else:
        #    msg = ""
        #    if resp:
        #        try:
        #            msg = json.loads(resp)
        #        except ValueError:
        #            msg = resp
        #    raise ClientException("failed to update repo {} - {}".format(name, msg))

    def get_id(self, name):
        """Returns a repo id from a repo name"""
        self._client.get_token()
        for repo in self.list():
            if name == repo["name"]:
                return repo["_id"]
        raise NotFound("Repo {} not found".format(name))

    def delete(self, name, force=False):
        self._client.get_token()
        repo_id = name
        if not utils.validate_uuid4(name):
            repo_id = self.get_id(name)
        querystring = ""
        if force:
            querystring = "?FORCE=True"
        http_code, resp = self._http.delete_cmd(
            "{}/{}{}".format(self._apiBase, repo_id, querystring)
        )
        # print 'HTTP CODE: {}'.format(http_code)
        # print 'RESP: {}'.format(resp)
        if http_code == 202:
            print("Deletion in progress")
        elif http_code == 204:
            print("Deleted")
        else:
            msg = resp or ""
            # if resp:
            #     try:
            #         msg = json.loads(resp)
            #     except ValueError:
            #         msg = resp
            raise ClientException("failed to delete repo {} - {}".format(name, msg))

    def list(self, filter=None):
        """Returns a list of repos"""
        self._client.get_token()
        filter_string = ""
        if filter:
            filter_string = "?{}".format(filter)
        _, resp = self._http.get2_cmd("{}{}".format(self._apiBase, filter_string))
        if resp:
            return json.loads(resp)
        return list()

    def get(self, name):
        """Returns a repo based on name or id"""
        self._client.get_token()
        repo_id = name
        if not utils.validate_uuid4(name):
            repo_id = self.get_id(name)
        try:
            _, resp = self._http.get2_cmd("{}/{}".format(self._apiBase, repo_id))
            if resp:
                resp = json.loads(resp)
            if not resp or "_id" not in resp:
                raise ClientException("failed to get repo info: {}".format(resp))
            return resp
        except NotFound:
            raise NotFound("Repo {} not found".format(name))
