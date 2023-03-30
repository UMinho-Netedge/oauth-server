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


def nsi_op_list(ctx, name):
    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    resp = ctx.obj.nsi.list_op(name)
    table = PrettyTable(["id", "operation", "status"])
    for op in resp:
        table.add_row([op["id"], op["lcmOperationType"], op["operationState"]])
    table.align = "l"
    print(table)


@click.command(
    name="nsi-op-list",
    short_help="shows the history of operations over a Network Slice Instance (NSI)",
)
@click.argument("name")
@click.pass_context
def nsi_op_list1(ctx, name):
    """shows the history of operations over a Network Slice Instance (NSI)

    NAME: name or ID of the Network Slice Instance
    """
    logger.debug("")
    nsi_op_list(ctx, name)


@click.command(
    name="netslice-instance-op-list",
    short_help="shows the history of operations over a Network Slice Instance (NSI)",
)
@click.argument("name")
@click.pass_context
def nsi_op_list2(ctx, name):
    """shows the history of operations over a Network Slice Instance (NSI)

    NAME: name or ID of the Network Slice Instance
    """
    logger.debug("")
    nsi_op_list(ctx, name)


def nsi_op_show(ctx, id, filter):
    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    op_info = ctx.obj.nsi.get_op(id)

    table = PrettyTable(["field", "value"])
    for k, v in list(op_info.items()):
        if not filter or k in filter:
            table.add_row([k, json.dumps(v, indent=2)])
    table.align = "l"
    print(table)


@click.command(
    name="nsi-op-show",
    short_help="shows the info of an operation over a Network Slice Instance(NSI)",
)
@click.argument("id")
@click.option(
    "--filter",
    multiple=True,
    help="restricts the information to the fields in the filter",
)
@click.pass_context
def nsi_op_show1(ctx, id, filter):
    """shows the info of an operation over a Network Slice Instance(NSI)

    ID: operation identifier
    """
    logger.debug("")
    nsi_op_show(ctx, id, filter)


@click.command(
    name="netslice-instance-op-show",
    short_help="shows the info of an operation over a Network Slice Instance(NSI)",
)
@click.argument("id")
@click.option(
    "--filter",
    multiple=True,
    help="restricts the information to the fields in the filter",
)
@click.pass_context
def nsi_op_show2(ctx, id, filter):
    """shows the info of an operation over a Network Slice Instance(NSI)

    ID: operation identifier
    """
    logger.debug("")
    nsi_op_show(ctx, id, filter)
