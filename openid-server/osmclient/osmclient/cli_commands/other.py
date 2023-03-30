# Copyright ETSI Contributors and Others.
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

import click
from osmclient.cli_commands import utils
import pkg_resources
import logging

logger = logging.getLogger("osmclient")


@click.command(name="version", short_help="shows client and server versions")
@click.pass_context
def get_version(ctx):
    """shows client and server versions"""
    utils.check_client_version(ctx.obj, "version")
    print("Server version: {}".format(ctx.obj.get_version()))
    print(
        "Client version: {}".format(pkg_resources.get_distribution("osmclient").version)
    )
