# Copyright 2017 Sandvine
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

import unittest
from mock import Mock
from osmclient.v1 import nsd
from osmclient.v1 import client
from osmclient.common.exceptions import NotFound


class TestNsd(unittest.TestCase):
    def test_list_empty(self):
        mock = Mock()
        mock.get_cmd.return_value = list()
        assert len(nsd.Nsd(mock, client=client.Client(host="127.0.0.1")).list()) == 0

    def test_get_notfound(self):
        mock = Mock()
        mock.get_cmd.return_value = "foo"
        self.assertRaises(
            NotFound, nsd.Nsd(mock, client=client.Client(host="127.0.0.1")).get, "bar"
        )

    def test_get_found(self):
        mock = Mock()
        if client.Client(host="127.0.0.1")._so_version == "v3":
            mock.get_cmd.return_value = {"project-nsd:nsd": [{"name": "foo"}]}
        else:
            # Backwards Compatibility
            mock.get_cmd.return_value = {"nsd:nsd": [{"name": "foo"}]}
        assert nsd.Nsd(mock, client=client.Client(host="127.0.0.1")).get("foo")
