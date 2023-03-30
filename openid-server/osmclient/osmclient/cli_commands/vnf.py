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
import time
from datetime import datetime
import logging

logger = logging.getLogger("osmclient")


def vnf_list(ctx, ns, filter, long):
    logger.debug("")
    if ns or filter:
        if ns:
            utils.check_client_version(ctx.obj, "--ns")
        if filter:
            filter = "&".join(filter)
            utils.check_client_version(ctx.obj, "--filter")
        resp = ctx.obj.vnf.list(ns, filter)
    else:
        resp = ctx.obj.vnf.list()
    fullclassname = ctx.obj.__module__ + "." + ctx.obj.__class__.__name__
    if fullclassname == "osmclient.sol005.client.Client":
        field_names = [
            "vnf id",
            "name",
            "ns id",
            "vnf member index",
            "vnfd name",
            "vim account id",
            "ip address",
        ]
        if long:
            field_names = [
                "vnf id",
                "name",
                "ns id",
                "vnf member index",
                "vnfd name",
                "vim account id",
                "ip address",
                "date",
                "last update",
            ]
        table = PrettyTable(field_names)
        for vnfr in resp:
            name = vnfr["name"] if "name" in vnfr else "-"
            new_row = [
                vnfr["_id"],
                name,
                vnfr["nsr-id-ref"],
                vnfr["member-vnf-index-ref"],
                vnfr["vnfd-ref"],
                vnfr["vim-account-id"],
                vnfr["ip-address"],
            ]
            if long:
                date = datetime.fromtimestamp(vnfr["_admin"]["created"]).strftime(
                    "%Y-%m-%dT%H:%M:%S"
                )
                last_update = datetime.fromtimestamp(
                    vnfr["_admin"]["modified"]
                ).strftime("%Y-%m-%dT%H:%M:%S")
                new_row.extend([date, last_update])
            table.add_row(new_row)
    else:
        table = PrettyTable(["vnf name", "id", "operational status", "config status"])
        for vnfr in resp:
            if "mgmt-interface" not in vnfr:
                vnfr["mgmt-interface"] = {}
                vnfr["mgmt-interface"]["ip-address"] = None
            table.add_row(
                [
                    vnfr["name"],
                    vnfr["id"],
                    vnfr["operational-status"],
                    vnfr["config-status"],
                ]
            )
    table.align = "l"
    print(table)


@click.command(name="vnf-list", short_help="list all NF instances")
@click.option(
    "--ns", default=None, help="NS instance id or name to restrict the NF list"
)
@click.option(
    "--filter",
    default=None,
    multiple=True,
    help="restricts the list to the NF instances matching the filter.",
)
@click.option("--long", is_flag=True, help="get more details")
@click.pass_context
def vnf_list1(ctx, ns, filter, long):
    """list all NF instances"""
    logger.debug("")
    vnf_list(ctx, ns, filter, long)


@click.command(name="nf-list", short_help="list all NF instances")
@click.option(
    "--ns", default=None, help="NS instance id or name to restrict the NF list"
)
@click.option(
    "--filter",
    default=None,
    multiple=True,
    help="restricts the list to the NF instances matching the filter.",
)
@click.option("--long", is_flag=True, help="get more details")
@click.pass_context
def nf_list(ctx, ns, filter, long):
    """list all NF instances

    \b
    Options:
      --ns     TEXT           NS instance id or name to restrict the VNF list
      --filter filterExpr     Restricts the list to the VNF instances matching the filter

    \b
    filterExpr consists of one or more strings formatted according to "simpleFilterExpr",
    concatenated using the "&" character:

      \b
      filterExpr := <simpleFilterExpr>["&"<simpleFilterExpr>]*
      simpleFilterExpr := <attrName>["."<attrName>]*["."<op>]"="<value>[","<value>]*
      op := "eq" | "neq" | "gt" | "lt" | "gte" | "lte" | "cont" | "ncont"
      attrName := string
      value := scalar value

    \b
    where:
      * zero or more occurrences
      ? zero or one occurrence
      [] grouping of expressions to be used with ? and *
      "" quotation marks for marking string constants
      <> name separator

    \b
    "AttrName" is the name of one attribute in the data type that defines the representation
    of the resource. The dot (".") character in "simpleFilterExpr" allows concatenation of
    <attrName> entries to filter by attributes deeper in the hierarchy of a structured document.
    "Op" stands for the comparison operator. If the expression has concatenated <attrName>
    entries, it means that the operator "op" is applied to the attribute addressed by the last
    <attrName> entry included in the concatenation. All simple filter expressions are combined
    by the "AND" logical operator. In a concatenation of <attrName> entries in a <simpleFilterExpr>,
    the rightmost "attrName" entry in a "simpleFilterExpr" is called "leaf attribute". The
    concatenation of all "attrName" entries except the leaf attribute is called the "attribute
    prefix". If an attribute referenced in an expression is an array, an object that contains a
    corresponding array shall be considered to match the expression if any of the elements in the
    array matches all expressions that have the same attribute prefix.

    \b
    Filter examples:
       --filter  vim-account-id=<VIM_ACCOUNT_ID>
       --filter  vnfd-ref=<VNFD_NAME>
       --filter  vdur.ip-address=<IP_ADDRESS>
       --filter  vnfd-ref=<VNFD_NAME>,vdur.ip-address=<IP_ADDRESS>
    """
    logger.debug("")
    vnf_list(ctx, ns, filter, long)


@click.command(name="vnf-show", short_help="shows the info of a VNF instance")
@click.argument("name")
@click.option("--literal", is_flag=True, help="print literally, no pretty table")
@click.option(
    "--filter",
    multiple=True,
    help="restricts the information to the fields in the filter",
)
@click.option("--kdu", default=None, help="KDU name (whose status will be shown)")
@click.pass_context
def vnf_show(ctx, name, literal, filter, kdu):
    """shows the info of a VNF instance

    NAME: name or ID of the VNF instance
    """

    def print_kdu_status(op_info_status):
        """print KDU status properly formatted"""
        try:
            op_status = yaml.safe_load(op_info_status)
            if (
                "namespace" in op_status
                and "info" in op_status
                and "last_deployed" in op_status["info"]
                and "status" in op_status["info"]
                and "code" in op_status["info"]["status"]
                and "resources" in op_status["info"]["status"]
                and "seconds" in op_status["info"]["last_deployed"]
            ):
                last_deployed_time = datetime.fromtimestamp(
                    op_status["info"]["last_deployed"]["seconds"]
                ).strftime("%a %b %d %I:%M:%S %Y")
                print("LAST DEPLOYED: {}".format(last_deployed_time))
                print("NAMESPACE: {}".format(op_status["namespace"]))
                status_code = "UNKNOWN"
                if op_status["info"]["status"]["code"] == 1:
                    status_code = "DEPLOYED"
                print("STATUS: {}".format(status_code))
                print()
                print("RESOURCES:")
                print(op_status["info"]["status"]["resources"])
                if "notes" in op_status["info"]["status"]:
                    print("NOTES:")
                    print(op_status["info"]["status"]["notes"])
            else:
                print(op_info_status)
        except Exception:
            print(op_info_status)

    logger.debug("")
    if kdu:
        if literal:
            raise ClientException(
                '"--literal" option is incompatible with "--kdu" option'
            )
        if filter:
            raise ClientException(
                '"--filter" option is incompatible with "--kdu" option'
            )

    utils.check_client_version(ctx.obj, ctx.command.name)
    resp = ctx.obj.vnf.get(name)

    if kdu:
        ns_id = resp["nsr-id-ref"]
        op_data = {}
        op_data["member_vnf_index"] = resp["member-vnf-index-ref"]
        op_data["kdu_name"] = kdu
        op_data["primitive"] = "status"
        op_data["primitive_params"] = {}
        op_id = ctx.obj.ns.exec_op(ns_id, op_name="action", op_data=op_data, wait=False)
        t = 0
        while t < 30:
            op_info = ctx.obj.ns.get_op(op_id)
            if op_info["operationState"] == "COMPLETED":
                print_kdu_status(op_info["detailed-status"])
                return
            time.sleep(5)
            t += 5
        print("Could not determine KDU status")
        return

    if literal:
        print(yaml.safe_dump(resp, indent=4, default_flow_style=False))
        return

    table = PrettyTable(["field", "value"])
    for k, v in list(resp.items()):
        if not filter or k in filter:
            table.add_row([k, utils.wrap_text(text=json.dumps(v, indent=2), width=100)])
    table.align = "l"
    print(table)
