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
from osmclient.common.exceptions import ClientException
from osmclient.cli_commands import utils
from prettytable import PrettyTable
import yaml
import json
import logging

logger = logging.getLogger("osmclient")


def nsi_list(ctx, filter):
    """list all Network Slice Instances"""
    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    if filter:
        filter = "&".join(filter)
    resp = ctx.obj.nsi.list(filter)
    table = PrettyTable(
        [
            "netslice instance name",
            "id",
            "operational status",
            "config status",
            "detailed status",
        ]
    )
    for nsi in resp:
        nsi_name = nsi["name"]
        nsi_id = nsi["_id"]
        opstatus = (
            nsi["operational-status"] if "operational-status" in nsi else "Not found"
        )
        configstatus = nsi["config-status"] if "config-status" in nsi else "Not found"
        detailed_status = (
            nsi["detailed-status"] if "detailed-status" in nsi else "Not found"
        )
        if configstatus == "config_not_needed":
            configstatus = "configured (no charms)"
        table.add_row([nsi_name, nsi_id, opstatus, configstatus, detailed_status])
    table.align = "l"
    print(table)


@click.command(name="nsi-list", short_help="list all Network Slice Instances (NSI)")
@click.option(
    "--filter",
    default=None,
    multiple=True,
    help="restricts the list to the Network Slice Instances matching the filter",
)
@click.pass_context
def nsi_list1(ctx, filter):
    """list all Network Slice Instances (NSI)"""
    logger.debug("")
    nsi_list(ctx, filter)


@click.command(
    name="netslice-instance-list", short_help="list all Network Slice Instances (NSI)"
)
@click.option(
    "--filter",
    default=None,
    multiple=True,
    help="restricts the list to the Network Slice Instances matching the filter",
)
@click.pass_context
def nsi_list2(ctx, filter):
    """list all Network Slice Instances (NSI)"""
    logger.debug("")
    nsi_list(ctx, filter)


def nsi_show(ctx, name, literal, filter):
    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    nsi = ctx.obj.nsi.get(name)

    if literal:
        print(yaml.safe_dump(nsi, indent=4, default_flow_style=False))
        return

    table = PrettyTable(["field", "value"])

    for k, v in list(nsi.items()):
        if not filter or k in filter:
            table.add_row([k, json.dumps(v, indent=2)])

    table.align = "l"
    print(table)


@click.command(
    name="nsi-show", short_help="shows the content of a Network Slice Instance (NSI)"
)
@click.argument("name")
@click.option("--literal", is_flag=True, help="print literally, no pretty table")
@click.option(
    "--filter",
    multiple=True,
    help="restricts the information to the fields in the filter",
)
@click.pass_context
def nsi_show1(ctx, name, literal, filter):
    """shows the content of a Network Slice Instance (NSI)

    NAME: name or ID of the Network Slice Instance
    """
    logger.debug("")
    nsi_show(ctx, name, literal, filter)


@click.command(
    name="netslice-instance-show",
    short_help="shows the content of a Network Slice Instance (NSI)",
)
@click.argument("name")
@click.option("--literal", is_flag=True, help="print literally, no pretty table")
@click.option(
    "--filter",
    multiple=True,
    help="restricts the information to the fields in the filter",
)
@click.pass_context
def nsi_show2(ctx, name, literal, filter):
    """shows the content of a Network Slice Instance (NSI)

    NAME: name or ID of the Network Slice Instance
    """
    logger.debug("")
    nsi_show(ctx, name, literal, filter)


def nsi_create(
    ctx, nst_name, nsi_name, vim_account, ssh_keys, config, config_file, wait
):
    """creates a new Network Slice Instance (NSI)"""
    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    if config_file:
        if config:
            raise ClientException(
                '"--config" option is incompatible with "--config_file" option'
            )
        with open(config_file, "r") as cf:
            config = cf.read()
    ctx.obj.nsi.create(
        nst_name,
        nsi_name,
        config=config,
        ssh_keys=ssh_keys,
        account=vim_account,
        wait=wait,
    )


@click.command(name="nsi-create", short_help="creates a new Network Slice Instance")
@click.option("--nsi_name", prompt=True, help="name of the Network Slice Instance")
@click.option("--nst_name", prompt=True, help="name of the Network Slice Template")
@click.option(
    "--vim_account",
    prompt=True,
    help="default VIM account id or name for the deployment",
)
@click.option(
    "--ssh_keys", default=None, help="comma separated list of keys to inject to vnfs"
)
@click.option(
    "--config",
    default=None,
    help="Netslice specific yaml configuration:\n"
    "netslice_subnet: [\n"
    "id: TEXT, vim_account: TEXT,\n"
    "vnf: [member-vnf-index: TEXT, vim_account: TEXT]\n"
    "vld: [name: TEXT, vim-network-name: TEXT or DICT with vim_account, vim_net entries]\n"
    "additionalParamsForNsi: {param: value, ...}\n"
    "additionalParamsForsubnet: [{id: SUBNET_ID, additionalParamsForNs: {}, additionalParamsForVnf: {}}]\n"
    "],\n"
    "netslice-vld: [name: TEXT, vim-network-name: TEXT or DICT with vim_account, vim_net entries]",
)
@click.option(
    "--config_file", default=None, help="nsi specific yaml configuration file"
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
def nsi_create1(
    ctx, nst_name, nsi_name, vim_account, ssh_keys, config, config_file, wait
):
    """creates a new Network Slice Instance (NSI)"""
    logger.debug("")
    nsi_create(
        ctx, nst_name, nsi_name, vim_account, ssh_keys, config, config_file, wait=wait
    )


@click.command(
    name="netslice-instance-create", short_help="creates a new Network Slice Instance"
)
@click.option("--nsi_name", prompt=True, help="name of the Network Slice Instance")
@click.option("--nst_name", prompt=True, help="name of the Network Slice Template")
@click.option(
    "--vim_account",
    prompt=True,
    help="default VIM account id or name for the deployment",
)
@click.option(
    "--ssh_keys", default=None, help="comma separated list of keys to inject to vnfs"
)
@click.option(
    "--config",
    default=None,
    help="Netslice specific yaml configuration:\n"
    "netslice_subnet: [\n"
    "id: TEXT, vim_account: TEXT,\n"
    "vnf: [member-vnf-index: TEXT, vim_account: TEXT]\n"
    "vld: [name: TEXT, vim-network-name: TEXT or DICT with vim_account, vim_net entries]"
    "],\n"
    "netslice-vld: [name: TEXT, vim-network-name: TEXT or DICT with vim_account, vim_net entries]",
)
@click.option(
    "--config_file", default=None, help="nsi specific yaml configuration file"
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
def nsi_create2(
    ctx, nst_name, nsi_name, vim_account, ssh_keys, config, config_file, wait
):
    """creates a new Network Slice Instance (NSI)"""
    logger.debug("")
    nsi_create(
        ctx, nst_name, nsi_name, vim_account, ssh_keys, config, config_file, wait=wait
    )


def nsi_delete(ctx, name, force, wait):
    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    ctx.obj.nsi.delete(name, force, wait=wait)


@click.command(name="nsi-delete", short_help="deletes a Network Slice Instance (NSI)")
@click.argument("name")
@click.option(
    "--force", is_flag=True, help="forces the deletion bypassing pre-conditions"
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
def nsi_delete1(ctx, name, force, wait):
    """deletes a Network Slice Instance (NSI)

    NAME: name or ID of the Network Slice instance to be deleted
    """
    logger.debug("")
    nsi_delete(ctx, name, force, wait=wait)


@click.command(
    name="netslice-instance-delete", short_help="deletes a Network Slice Instance (NSI)"
)
@click.argument("name")
@click.option(
    "--force", is_flag=True, help="forces the deletion bypassing pre-conditions"
)
@click.pass_context
def nsi_delete2(ctx, name, force, wait):
    """deletes a Network Slice Instance (NSI)

    NAME: name or ID of the Network Slice instance to be deleted
    """
    logger.debug("")
    nsi_delete(ctx, name, force, wait=wait)
