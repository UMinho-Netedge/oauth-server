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
import yaml
import json
import logging

logger = logging.getLogger("osmclient")


def nst_list(ctx, filter):
    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    if filter:
        filter = "&".join(filter)
    resp = ctx.obj.nst.list(filter)
    table = PrettyTable(["nst name", "id"])
    for nst in resp:
        name = nst["name"] if "name" in nst else "-"
        table.add_row([name, nst["_id"]])
    table.align = "l"
    print(table)


@click.command(name="nst-list", short_help="list all Network Slice Templates (NST)")
@click.option(
    "--filter",
    default=None,
    multiple=True,
    help="restricts the list to the NST matching the filter",
)
@click.pass_context
def nst_list1(ctx, filter):
    """list all Network Slice Templates (NST) in the system"""
    logger.debug("")
    nst_list(ctx, filter)


@click.command(
    name="netslice-template-list", short_help="list all Network Slice Templates (NST)"
)
@click.option(
    "--filter",
    default=None,
    multiple=True,
    help="restricts the list to the NST matching the filter",
)
@click.pass_context
def nst_list2(ctx, filter):
    """list all Network Slice Templates (NST) in the system"""
    logger.debug("")
    nst_list(ctx, filter)


def nst_show(ctx, name, literal):
    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    resp = ctx.obj.nst.get(name)
    # resp = ctx.obj.nst.get_individual(name)

    if literal:
        print(yaml.safe_dump(resp, indent=4, default_flow_style=False))
        return

    table = PrettyTable(["field", "value"])
    for k, v in list(resp.items()):
        table.add_row([k, utils.wrap_text(json.dumps(v, indent=2), 100)])
    table.align = "l"
    print(table)


@click.command(
    name="nst-show", short_help="shows the content of a Network Slice Template (NST)"
)
@click.option("--literal", is_flag=True, help="print literally, no pretty table")
@click.argument("name")
@click.pass_context
def nst_show1(ctx, name, literal):
    """shows the content of a Network Slice Template (NST)

    NAME: name or ID of the NST
    """
    logger.debug("")
    nst_show(ctx, name, literal)


@click.command(
    name="netslice-template-show",
    short_help="shows the content of a Network Slice Template (NST)",
)
@click.option("--literal", is_flag=True, help="print literally, no pretty table")
@click.argument("name")
@click.pass_context
def nst_show2(ctx, name, literal):
    """shows the content of a Network Slice Template (NST)

    NAME: name or ID of the NST
    """
    logger.debug("")
    nst_show(ctx, name, literal)


def nst_create(ctx, filename, overwrite):
    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    ctx.obj.nst.create(filename, overwrite)


@click.command(
    name="nst-create", short_help="creates a new Network Slice Template (NST)"
)
@click.argument("filename")
@click.option(
    "--overwrite",
    "overwrite",
    default=None,  # hidden=True,
    help="Deprecated. Use override",
)
@click.option(
    "--override",
    "overwrite",
    default=None,
    help="overrides fields in descriptor, format: "
    '"key1.key2...=value[;key3...=value;...]"',
)
@click.pass_context
def nst_create1(ctx, filename, overwrite):
    """creates a new Network Slice Template (NST)

    FILENAME: NST package folder, NST yaml file or NSTpkg tar.gz file
    """
    logger.debug("")
    nst_create(ctx, filename, overwrite)


@click.command(
    name="netslice-template-create",
    short_help="creates a new Network Slice Template (NST)",
)
@click.argument("filename")
@click.option(
    "--overwrite",
    "overwrite",
    default=None,  # hidden=True,
    help="Deprecated. Use override",
)
@click.option(
    "--override",
    "overwrite",
    default=None,
    help="overrides fields in descriptor, format: "
    '"key1.key2...=value[;key3...=value;...]"',
)
@click.pass_context
def nst_create2(ctx, filename, overwrite):
    """creates a new Network Slice Template (NST)

    FILENAME: NST yaml file or NSTpkg tar.gz file
    """
    logger.debug("")
    nst_create(ctx, filename, overwrite)


def nst_update(ctx, name, content):
    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    ctx.obj.nst.update(name, content)


@click.command(name="nst-update", short_help="updates a Network Slice Template (NST)")
@click.argument("name")
@click.option(
    "--content",
    default=None,
    help="filename with the NST/NSTpkg replacing the current one",
)
@click.pass_context
def nst_update1(ctx, name, content):
    """updates a Network Slice Template (NST)

    NAME: name or ID of the NSD/NSpkg
    """
    logger.debug("")
    nst_update(ctx, name, content)


@click.command(
    name="netslice-template-update", short_help="updates a Network Slice Template (NST)"
)
@click.argument("name")
@click.option(
    "--content",
    default=None,
    help="filename with the NST/NSTpkg replacing the current one",
)
@click.pass_context
def nst_update2(ctx, name, content):
    """updates a Network Slice Template (NST)

    NAME: name or ID of the NSD/NSpkg
    """
    logger.debug("")
    nst_update(ctx, name, content)


def nst_delete(ctx, name, force):
    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    ctx.obj.nst.delete(name, force)


@click.command(name="nst-delete", short_help="deletes a Network Slice Template (NST)")
@click.argument("name")
@click.option(
    "--force", is_flag=True, help="forces the deletion bypassing pre-conditions"
)
@click.pass_context
def nst_delete1(ctx, name, force):
    """deletes a Network Slice Template (NST)

    NAME: name or ID of the NST/NSTpkg to be deleted
    """
    logger.debug("")
    nst_delete(ctx, name, force)


@click.command(
    name="netslice-template-delete", short_help="deletes a Network Slice Template (NST)"
)
@click.argument("name")
@click.option(
    "--force", is_flag=True, help="forces the deletion bypassing pre-conditions"
)
@click.pass_context
def nst_delete2(ctx, name, force):
    """deletes a Network Slice Template (NST)

    NAME: name or ID of the NST/NSTpkg to be deleted
    """
    logger.debug("")
    nst_delete(ctx, name, force)
