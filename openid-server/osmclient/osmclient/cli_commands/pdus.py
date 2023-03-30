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


@click.command(name="pdu-list", short_help="list all Physical Deployment Units (PDU)")
@click.option(
    "--filter",
    default=None,
    multiple=True,
    help="restricts the list to the Physical Deployment Units matching the filter",
)
@click.pass_context
def pdu_list(ctx, filter):
    """list all Physical Deployment Units (PDU)"""
    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    if filter:
        filter = "&".join(filter)
    resp = ctx.obj.pdu.list(filter)
    table = PrettyTable(["pdu name", "id", "type", "mgmt ip address"])
    for pdu in resp:
        pdu_name = pdu["name"]
        pdu_id = pdu["_id"]
        pdu_type = pdu["type"]
        pdu_ipaddress = "None"
        for iface in pdu["interfaces"]:
            if iface["mgmt"]:
                pdu_ipaddress = iface["ip-address"]
                break
        table.add_row([pdu_name, pdu_id, pdu_type, pdu_ipaddress])
    table.align = "l"
    print(table)


@click.command(
    name="pdu-show", short_help="shows the content of a Physical Deployment Unit (PDU)"
)
@click.argument("name")
@click.option("--literal", is_flag=True, help="print literally, no pretty table")
@click.option(
    "--filter",
    multiple=True,
    help="restricts the information to the fields in the filter",
)
@click.pass_context
def pdu_show(ctx, name, literal, filter):
    """shows the content of a Physical Deployment Unit (PDU)

    NAME: name or ID of the PDU
    """
    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    pdu = ctx.obj.pdu.get(name)

    if literal:
        print(yaml.safe_dump(pdu, indent=4, default_flow_style=False))
        return

    table = PrettyTable(["field", "value"])

    for k, v in list(pdu.items()):
        if not filter or k in filter:
            table.add_row([k, json.dumps(v, indent=2)])

    table.align = "l"
    print(table)


@click.command(
    name="pdu-create", short_help="adds a new Physical Deployment Unit to the catalog"
)
@click.option("--name", help="name of the Physical Deployment Unit")
@click.option("--pdu_type", help="type of PDU (e.g. router, firewall, FW001)")
@click.option(
    "--interface",
    help="interface(s) of the PDU: name=<NAME>,mgmt=<true|false>,ip-address=<IP_ADDRESS>"
    + "[,type=<overlay|underlay>][,mac-address=<MAC_ADDRESS>][,vim-network-name=<VIM_NET_NAME>]",
    multiple=True,
)
@click.option("--description", help="human readable description")
@click.option(
    "--vim_account",
    help="list of VIM accounts (in the same VIM) that can reach this PDU\n"
    + "The format for multiple VIMs is --vim_account <vim_account_id_1> "
    + "--vim_account <vim_account_id_2> ... --vim_account <vim_account_id_N>",
    multiple=True,
)
@click.option(
    "--descriptor_file",
    default=None,
    help="PDU descriptor file (as an alternative to using the other arguments)",
)
@click.pass_context
def pdu_create(
    ctx, name, pdu_type, interface, description, vim_account, descriptor_file
):
    """creates a new Physical Deployment Unit (PDU)"""
    logger.debug("")

    utils.check_client_version(ctx.obj, ctx.command.name)

    pdu = create_pdu_dictionary(
        name, pdu_type, interface, description, vim_account, descriptor_file
    )
    ctx.obj.pdu.create(pdu)


@click.command(
    name="pdu-update", short_help="updates a Physical Deployment Unit to the catalog"
)
@click.argument("name")
@click.option("--newname", help="New name for the Physical Deployment Unit")
@click.option("--pdu_type", help="type of PDU (e.g. router, firewall, FW001)")
@click.option(
    "--interface",
    help="interface(s) of the PDU: name=<NAME>,mgmt=<true|false>,ip-address=<IP_ADDRESS>"
    + "[,type=<overlay|underlay>][,mac-address=<MAC_ADDRESS>][,vim-network-name=<VIM_NET_NAME>]",
    multiple=True,
)
@click.option("--description", help="human readable description")
@click.option(
    "--vim_account",
    help="list of VIM accounts (in the same VIM) that can reach this PDU\n"
    + "The format for multiple VIMs is --vim_account <vim_account_id_1> "
    + "--vim_account <vim_account_id_2> ... --vim_account <vim_account_id_N>",
    multiple=True,
)
@click.option(
    "--descriptor_file",
    default=None,
    help="PDU descriptor file (as an alternative to using the other arguments)",
)
@click.pass_context
def pdu_update(
    ctx, name, newname, pdu_type, interface, description, vim_account, descriptor_file
):
    """Updates a new Physical Deployment Unit (PDU)"""
    logger.debug("")

    utils.check_client_version(ctx.obj, ctx.command.name)

    update = True

    if not newname:
        newname = name

    pdu = create_pdu_dictionary(
        newname, pdu_type, interface, description, vim_account, descriptor_file, update
    )
    ctx.obj.pdu.update(name, pdu)


def create_pdu_dictionary(
    name, pdu_type, interface, description, vim_account, descriptor_file, update=False
):
    logger.debug("")
    pdu = {}

    if not descriptor_file:
        if not update:
            if not name:
                raise ClientException(
                    'in absence of descriptor file, option "--name" is mandatory'
                )
            if not pdu_type:
                raise ClientException(
                    'in absence of descriptor file, option "--pdu_type" is mandatory'
                )
            if not interface:
                raise ClientException(
                    'in absence of descriptor file, option "--interface" is mandatory (at least once)'
                )
            if not vim_account:
                raise ClientException(
                    'in absence of descriptor file, option "--vim_account" is mandatory (at least once)'
                )
    else:
        with open(descriptor_file, "r") as df:
            pdu = yaml.safe_load(df.read())
    if name:
        pdu["name"] = name
    if pdu_type:
        pdu["type"] = pdu_type
    if description:
        pdu["description"] = description
    if vim_account:
        pdu["vim_accounts"] = vim_account
    if interface:
        ifaces_list = []
        for iface in interface:
            new_iface = {k: v for k, v in [i.split("=") for i in iface.split(",")]}
            new_iface["mgmt"] = new_iface.get("mgmt", "false").lower() == "true"
            ifaces_list.append(new_iface)
        pdu["interfaces"] = ifaces_list
    return pdu


@click.command(name="pdu-delete", short_help="deletes a Physical Deployment Unit (PDU)")
@click.argument("name")
@click.option(
    "--force", is_flag=True, help="forces the deletion bypassing pre-conditions"
)
@click.pass_context
def pdu_delete(ctx, name, force):
    """deletes a Physical Deployment Unit (PDU)

    NAME: name or ID of the PDU to be deleted
    """
    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    ctx.obj.pdu.delete(name, force)
