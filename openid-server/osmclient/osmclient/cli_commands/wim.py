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


@click.command(name="wim-create", short_help="creates a new WIM account")
@click.option("--name", prompt=True, help="Name for the WIM account")
@click.option("--user", help="WIM username")
@click.option("--password", help="WIM password")
@click.option("--url", prompt=True, help="WIM url")
@click.option("--config", default=None, help="WIM specific config parameters")
@click.option("--wim_type", help="WIM type")
@click.option("--description", default=None, help="human readable description")
@click.option(
    "--wim_port_mapping",
    default=None,
    help="File describing the port mapping between DC edge (datacenters, switches, ports) and WAN edge "
    "(WAN service endpoint id and info)",
)
@click.option(
    "--wait",
    required=False,
    default=False,
    is_flag=True,
    help="do not return the control immediately, but keep it "
    "until the operation is completed, or timeout",
)
@click.pass_context
def wim_create(
    ctx,
    name,
    user,
    password,
    url,
    config,
    wim_type,
    description,
    wim_port_mapping,
    wait,
):
    """creates a new WIM account"""
    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    wim = {}
    if user:
        wim["user"] = user
    if password:
        wim["password"] = password
    if url:
        wim["wim_url"] = url
    wim["wim_type"] = wim_type
    if description:
        wim["description"] = description
    if config:
        wim["config"] = config
    ctx.obj.wim.create(name, wim, wim_port_mapping, wait=wait)


@click.command(name="wim-update", short_help="updates a WIM account")
@click.argument("name")
@click.option("--newname", help="New name for the WIM account")
@click.option("--user", help="WIM username")
@click.option("--password", help="WIM password")
@click.option("--url", help="WIM url")
@click.option("--config", help="WIM specific config parameters")
@click.option("--wim_type", help="WIM type")
@click.option("--description", help="human readable description")
@click.option(
    "--wim_port_mapping",
    default=None,
    help="File describing the port mapping between DC edge (datacenters, switches, ports) and WAN edge "
    "(WAN service endpoint id and info)",
)
@click.option(
    "--wait",
    required=False,
    default=False,
    is_flag=True,
    help="do not return the control immediately, but keep it until the operation is completed, or timeout",
)
@click.pass_context
def wim_update(
    ctx,
    name,
    newname,
    user,
    password,
    url,
    config,
    wim_type,
    description,
    wim_port_mapping,
    wait,
):
    """updates a WIM account

    NAME: name or ID of the WIM account
    """
    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    wim = {}
    if newname:
        wim["name"] = newname
    if user:
        wim["user"] = user
    if password:
        wim["password"] = password
    if url:
        wim["url"] = url
    if wim_type:
        wim["wim_type"] = wim_type
    if description:
        wim["description"] = description
    if config:
        wim["config"] = config
    ctx.obj.wim.update(name, wim, wim_port_mapping, wait=wait)


@click.command(name="wim-delete", short_help="deletes a WIM account")
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
def wim_delete(ctx, name, force, wait):
    """deletes a WIM account

    NAME: name or ID of the WIM account to be deleted
    """
    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    ctx.obj.wim.delete(name, force, wait=wait)


@click.command(name="wim-list", short_help="list all WIM accounts")
@click.option(
    "--filter",
    default=None,
    multiple=True,
    help="restricts the list to the WIM accounts matching the filter",
)
@click.pass_context
def wim_list(ctx, filter):
    """list all WIM accounts"""
    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    if filter:
        filter = "&".join(filter)
    resp = ctx.obj.wim.list(filter)
    table = PrettyTable(["wim name", "uuid"])
    for wim in resp:
        table.add_row([wim["name"], wim["uuid"]])
    table.align = "l"
    print(table)


@click.command(name="wim-show", short_help="shows the details of a WIM account")
@click.argument("name")
@click.pass_context
def wim_show(ctx, name):
    """shows the details of a WIM account

    NAME: name or ID of the WIM account
    """
    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    resp = ctx.obj.wim.get(name)
    if "password" in resp:
        resp["password"] = "********"

    table = PrettyTable(["key", "attribute"])
    for k, v in list(resp.items()):
        table.add_row([k, json.dumps(v, indent=2)])
    table.align = "l"
    print(table)
