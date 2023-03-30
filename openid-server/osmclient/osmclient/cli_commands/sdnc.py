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
from prettytable import PrettyTable
import json
import logging

logger = logging.getLogger("osmclient")


@click.command(name="sdnc-create", short_help="creates a new SDN controller")
@click.option("--name", prompt=True, help="Name to create sdn controller")
@click.option("--type", prompt=True, help="SDN controller type")
@click.option(
    "--sdn_controller_version",  # hidden=True,
    help="Deprecated. Use --config {version: sdn_controller_version}",
)
@click.option("--url", help="URL in format http[s]://HOST:IP/")
@click.option("--ip_address", help="Deprecated. Use --url")  # hidden=True,
@click.option("--port", help="Deprecated. Use --url")  # hidden=True,
@click.option(
    "--switch_dpid", help="Deprecated. Use --config {switch_id: DPID}"  # hidden=True,
)
@click.option(
    "--config",
    help="Extra information for SDN in yaml format, as {switch_id: identity used for the plugin (e.g. DPID: "
    "Openflow Datapath ID), version: version}",
)
@click.option("--user", help="SDN controller username")
@click.option(
    "--password",
    hide_input=True,
    confirmation_prompt=True,
    help="SDN controller password",
)
@click.option("--description", default=None, help="human readable description")
@click.option(
    "--wait",
    required=False,
    default=False,
    is_flag=True,
    help="do not return the control immediately, but keep it until the operation is completed, or timeout",
)
@click.pass_context
def sdnc_create(ctx, **kwargs):
    """creates a new SDN controller"""
    logger.debug("")
    sdncontroller = {
        x: kwargs[x]
        for x in kwargs
        if kwargs[x] and x not in ("wait", "ip_address", "port", "switch_dpid")
    }
    if kwargs.get("port"):
        print("option '--port' is deprecated, use '--url' instead")
        sdncontroller["port"] = int(kwargs["port"])
    if kwargs.get("ip_address"):
        print("option '--ip_address' is deprecated, use '--url' instead")
        sdncontroller["ip"] = kwargs["ip_address"]
    if kwargs.get("switch_dpid"):
        print(
            "option '--switch_dpid' is deprecated, use '--config={switch_id: id|DPID}' instead"
        )
        sdncontroller["dpid"] = kwargs["switch_dpid"]
    if kwargs.get("sdn_controller_version"):
        print(
            "option '--sdn_controller_version' is deprecated, use '--config={version: SDN_CONTROLLER_VERSION}'"
            " instead"
        )
    utils.check_client_version(ctx.obj, ctx.command.name)
    ctx.obj.sdnc.create(kwargs["name"], sdncontroller, wait=kwargs["wait"])


@click.command(name="sdnc-update", short_help="updates an SDN controller")
@click.argument("name")
@click.option("--newname", help="New name for the SDN controller")
@click.option("--description", default=None, help="human readable description")
@click.option("--type", help="SDN controller type")
@click.option("--url", help="URL in format http[s]://HOST:IP/")
@click.option(
    "--config",
    help="Extra information for SDN in yaml format, as "
    "{switch_id: identity used for the plugin (e.g. DPID: "
    "Openflow Datapath ID), version: version}",
)
@click.option("--user", help="SDN controller username")
@click.option("--password", help="SDN controller password")
@click.option("--ip_address", help="Deprecated. Use --url")  # hidden=True
@click.option("--port", help="Deprecated. Use --url")  # hidden=True
@click.option(
    "--switch_dpid", help="Deprecated. Use --config {switch_dpid: DPID}"
)  # hidden=True
@click.option(
    "--sdn_controller_version", help="Deprecated. Use --config {version: VERSION}"
)  # hidden=True
@click.option(
    "--wait",
    required=False,
    default=False,
    is_flag=True,
    help="do not return the control immediately, but keep it until the operation is completed, or timeout",
)
@click.pass_context
def sdnc_update(ctx, **kwargs):
    """updates an SDN controller

    NAME: name or ID of the SDN controller
    """
    logger.debug("")
    sdncontroller = {
        x: kwargs[x]
        for x in kwargs
        if kwargs[x]
        and x not in ("wait", "ip_address", "port", "switch_dpid", "new_name")
    }
    if kwargs.get("newname"):
        sdncontroller["name"] = kwargs["newname"]
    if kwargs.get("port"):
        print("option '--port' is deprecated, use '--url' instead")
        sdncontroller["port"] = int(kwargs["port"])
    if kwargs.get("ip_address"):
        print("option '--ip_address' is deprecated, use '--url' instead")
        sdncontroller["ip"] = kwargs["ip_address"]
    if kwargs.get("switch_dpid"):
        print(
            "option '--switch_dpid' is deprecated, use '--config={switch_id: id|DPID}' instead"
        )
        sdncontroller["dpid"] = kwargs["switch_dpid"]
    if kwargs.get("sdn_controller_version"):
        print(
            "option '--sdn_controller_version' is deprecated, use '---config={version: SDN_CONTROLLER_VERSION}'"
            " instead"
        )

    utils.check_client_version(ctx.obj, ctx.command.name)
    ctx.obj.sdnc.update(kwargs["name"], sdncontroller, wait=kwargs["wait"])


@click.command(name="sdnc-delete", short_help="deletes an SDN controller")
@click.argument("name")
@click.option(
    "--force", is_flag=True, help="forces the deletion bypassing pre-conditions"
)
@click.option(
    "--wait",
    required=False,
    default=False,
    is_flag=True,
    help="do not return the control immediately, but keep it until the operation is completed, or timeout",
)
@click.pass_context
def sdnc_delete(ctx, name, force, wait):
    """deletes an SDN controller

    NAME: name or ID of the SDN controller to be deleted
    """
    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    ctx.obj.sdnc.delete(name, force, wait=wait)


@click.command(name="sdnc-list", short_help="list all SDN controllers")
@click.option(
    "--filter",
    default=None,
    multiple=True,
    help="restricts the list to the SDN controllers matching the filter with format: 'k[.k..]=v[&k[.k]=v2]'",
)
@click.pass_context
def sdnc_list(ctx, filter):
    """list all SDN controllers"""
    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    if filter:
        filter = "&".join(filter)
    resp = ctx.obj.sdnc.list(filter)
    table = PrettyTable(["sdnc name", "id"])
    for sdnc in resp:
        table.add_row([sdnc["name"], sdnc["_id"]])
    table.align = "l"
    print(table)


@click.command(name="sdnc-show", short_help="shows the details of an SDN controller")
@click.argument("name")
@click.pass_context
def sdnc_show(ctx, name):
    """shows the details of an SDN controller

    NAME: name or ID of the SDN controller
    """
    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    resp = ctx.obj.sdnc.get(name)

    table = PrettyTable(["key", "attribute"])
    for k, v in list(resp.items()):
        table.add_row([k, json.dumps(v, indent=2)])
    table.align = "l"
    print(table)
