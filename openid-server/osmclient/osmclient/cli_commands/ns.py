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
from datetime import datetime
import logging

logger = logging.getLogger("osmclient")


@click.command(name="ns-list", short_help="list all NS instances")
@click.option(
    "--filter",
    default=None,
    multiple=True,
    help="restricts the list to the NS instances matching the filter.",
)
@click.option(
    "--long",
    is_flag=True,
    help="get more details of the NS (project, vim, deployment status, configuration status.",
)
@click.pass_context
def ns_list(ctx, filter, long):
    """list all NS instances

    \b
    Options:
      --filter filterExpr    Restricts the list to the NS instances matching the filter

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
       --filter  admin-status=ENABLED
       --filter  nsd-ref=<NSD_NAME>
       --filter  nsd.vendor=<VENDOR>
       --filter  nsd.vendor=<VENDOR>&nsd-ref=<NSD_NAME>
       --filter  nsd.constituent-vnfd.vnfd-id-ref=<VNFD_NAME>
    """

    def summarize_deployment_status(status_dict):
        # Nets
        summary = ""
        if not status_dict:
            return summary
        n_nets = 0
        status_nets = {}
        net_list = status_dict.get("nets", [])
        for net in net_list:
            n_nets += 1
            if net["status"] not in status_nets:
                status_nets[net["status"]] = 1
            else:
                status_nets[net["status"]] += 1
        message = "Nets: "
        for k, v in status_nets.items():
            message += "{}:{},".format(k, v)
        message += "TOTAL:{}".format(n_nets)
        summary += "{}".format(message)
        # VMs and VNFs
        n_vms = 0
        status_vms = {}
        status_vnfs = {}
        vnf_list = status_dict["vnfs"]
        for vnf in vnf_list:
            member_vnf_index = vnf["member_vnf_index"]
            if member_vnf_index not in status_vnfs:
                status_vnfs[member_vnf_index] = {}
            for vm in vnf["vms"]:
                n_vms += 1
                if vm["status"] not in status_vms:
                    status_vms[vm["status"]] = 1
                else:
                    status_vms[vm["status"]] += 1
                if vm["status"] not in status_vnfs[member_vnf_index]:
                    status_vnfs[member_vnf_index][vm["status"]] = 1
                else:
                    status_vnfs[member_vnf_index][vm["status"]] += 1
        message = "VMs: "
        for k, v in status_vms.items():
            message += "{}:{},".format(k, v)
        message += "TOTAL:{}".format(n_vms)
        summary += "\n{}".format(message)
        summary += "\nNFs:"
        for k, v in status_vnfs.items():
            total = 0
            message = "\n  {} VMs: ".format(k)
            for k2, v2 in v.items():
                message += "{}:{},".format(k2, v2)
                total += v2
            message += "TOTAL:{}".format(total)
        summary += message
        return summary

    def summarize_config_status(ee_list):
        summary = ""
        if not ee_list:
            return summary
        n_ee = 0
        status_ee = {}
        for ee in ee_list:
            n_ee += 1
            if ee["elementType"] not in status_ee:
                status_ee[ee["elementType"]] = {}
                status_ee[ee["elementType"]][ee["status"]] = 1
                continue
            if ee["status"] in status_ee[ee["elementType"]]:
                status_ee[ee["elementType"]][ee["status"]] += 1
            else:
                status_ee[ee["elementType"]][ee["status"]] = 1
        for elementType in ["KDU", "VDU", "PDU", "VNF", "NS"]:
            if elementType in status_ee:
                message = ""
                total = 0
                for k, v in status_ee[elementType].items():
                    message += "{}:{},".format(k, v)
                    total += v
                message += "TOTAL:{}\n".format(total)
                summary += "{}: {}".format(elementType, message)
        summary += "TOTAL Exec. Env.: {}".format(n_ee)
        return summary

    logger.debug("")
    if filter:
        utils.check_client_version(ctx.obj, "--filter")
        filter = "&".join(filter)
        resp = ctx.obj.ns.list(filter)
    else:
        resp = ctx.obj.ns.list()
    if long:
        table = PrettyTable(
            [
                "ns instance name",
                "id",
                "date",
                "ns state",
                "current operation",
                "error details",
                "project",
                "vim (inst param)",
                "deployment status",
                "configuration status",
            ]
        )
        project_list = ctx.obj.project.list()
        try:
            vim_list = ctx.obj.vim.list()
        except Exception:
            vim_list = []
    else:
        table = PrettyTable(
            [
                "ns instance name",
                "id",
                "date",
                "ns state",
                "current operation",
                "error details",
            ]
        )
    for ns in resp:
        fullclassname = ctx.obj.__module__ + "." + ctx.obj.__class__.__name__
        if fullclassname == "osmclient.sol005.client.Client":
            nsr = ns
            logger.debug("NS info: {}".format(nsr))
            nsr_name = nsr["name"]
            nsr_id = nsr["_id"]
            date = datetime.fromtimestamp(nsr["create-time"]).strftime(
                "%Y-%m-%dT%H:%M:%S"
            )
            ns_state = nsr.get("nsState", nsr["_admin"]["nsState"])
            if long:
                deployment_status = summarize_deployment_status(
                    nsr.get("deploymentStatus")
                )
                config_status = summarize_config_status(nsr.get("configurationStatus"))
                project_id, project_name = utils.get_project(project_list, nsr)
                # project = '{} ({})'.format(project_name, project_id)
                project = project_name
                vim_id = nsr.get("datacenter")
                vim_name = utils.get_vim_name(vim_list, vim_id)

                # vim = '{} ({})'.format(vim_name, vim_id)
                vim = vim_name
            if "currentOperation" in nsr:
                current_operation = "{} ({})".format(
                    nsr["currentOperation"], nsr["currentOperationID"]
                )
            else:
                current_operation = "{} ({})".format(
                    nsr["_admin"].get("current-operation", "-"),
                    nsr["_admin"]["nslcmop"],
                )
            error_details = "N/A"
            if (
                ns_state == "BROKEN"
                or ns_state == "DEGRADED"
                or ("currentOperation" not in nsr and nsr.get("errorDescription"))
            ):
                error_details = "{}\nDetail: {}".format(
                    nsr["errorDescription"], nsr["errorDetail"]
                )
        else:
            nsopdata = ctx.obj.ns.get_opdata(ns["id"])
            nsr = nsopdata["nsr:nsr"]
            nsr_name = nsr["name-ref"]
            nsr_id = nsr["ns-instance-config-ref"]
            date = "-"
            project = "-"
            deployment_status = (
                nsr["operational-status"]
                if "operational-status" in nsr
                else "Not found"
            )
            ns_state = deployment_status
            config_status = nsr.get("config-status", "Not found")
            current_operation = "Unknown"
            error_details = nsr.get("detailed-status", "Not found")
            if config_status == "config_not_needed":
                config_status = "configured (no charms)"

        if long:
            table.add_row(
                [
                    nsr_name,
                    nsr_id,
                    date,
                    ns_state,
                    current_operation,
                    utils.wrap_text(text=error_details, width=40),
                    project,
                    vim,
                    deployment_status,
                    config_status,
                ]
            )
        else:
            table.add_row(
                [
                    nsr_name,
                    nsr_id,
                    date,
                    ns_state,
                    current_operation,
                    utils.wrap_text(text=error_details, width=40),
                ]
            )
    table.align = "l"
    print(table)
    print('To get the history of all operations over a NS, run "osm ns-op-list NS_ID"')
    print(
        'For more details on the current operation, run "osm ns-op-show OPERATION_ID"'
    )


@click.command(name="ns-show", short_help="shows the info of a NS instance")
@click.argument("name")
@click.option("--literal", is_flag=True, help="print literally, no pretty table")
@click.option(
    "--filter",
    multiple=True,
    help="restricts the information to the fields in the filter",
)
@click.pass_context
def ns_show(ctx, name, literal, filter):
    """shows the info of a NS instance

    NAME: name or ID of the NS instance
    """
    logger.debug("")
    ns = ctx.obj.ns.get(name)

    if literal:
        print(yaml.safe_dump(ns, indent=4, default_flow_style=False))
        return

    table = PrettyTable(["field", "value"])

    for k, v in list(ns.items()):
        if not filter or k in filter:
            table.add_row([k, utils.wrap_text(text=json.dumps(v, indent=2), width=100)])

    fullclassname = ctx.obj.__module__ + "." + ctx.obj.__class__.__name__
    if fullclassname != "osmclient.sol005.client.Client":
        nsopdata = ctx.obj.ns.get_opdata(ns["id"])
        nsr_optdata = nsopdata["nsr:nsr"]
        for k, v in list(nsr_optdata.items()):
            if not filter or k in filter:
                table.add_row([k, utils.wrap_text(json.dumps(v, indent=2), width=100)])
    table.align = "l"
    print(table)


@click.command(name="ns-create", short_help="creates a new Network Service instance")
@click.option("--ns_name", prompt=True, help="name of the NS instance")
@click.option("--nsd_name", prompt=True, help="name of the NS descriptor")
@click.option(
    "--vim_account",
    prompt=True,
    help="default VIM account id or name for the deployment",
)
@click.option("--admin_status", default="ENABLED", help="administration status")
@click.option(
    "--ssh_keys",
    default=None,
    help="comma separated list of public key files to inject to vnfs",
)
@click.option("--config", default=None, help="ns specific yaml configuration")
@click.option("--config_file", default=None, help="ns specific yaml configuration file")
@click.option(
    "--wait",
    required=False,
    default=False,
    is_flag=True,
    help="do not return the control immediately, but keep it "
    "until the operation is completed, or timeout",
)
@click.option("--timeout", default=None, help="ns deployment timeout")
@click.pass_context
def ns_create(
    ctx,
    nsd_name,
    ns_name,
    vim_account,
    admin_status,
    ssh_keys,
    config,
    config_file,
    wait,
    timeout,
):
    """creates a new NS instance"""
    logger.debug("")
    if config_file:
        utils.check_client_version(ctx.obj, "--config_file")
        if config:
            raise ClientException(
                '"--config" option is incompatible with "--config_file" option'
            )
        with open(config_file, "r") as cf:
            config = cf.read()
    ctx.obj.ns.create(
        nsd_name,
        ns_name,
        config=config,
        ssh_keys=ssh_keys,
        account=vim_account,
        wait=wait,
        timeout=timeout,
    )


@click.command(name="ns-delete", short_help="deletes a NS instance")
@click.argument("name")
@click.option(
    "--force", is_flag=True, help="forces the deletion bypassing pre-conditions"
)
@click.option(
    "--config",
    default=None,
    help="specific yaml configuration for the termination, e.g. '{autoremove: False, timeout_ns_terminate: "
    "600, skip_terminate_primitives: True}'",
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
def ns_delete(ctx, name, force, config, wait):
    """deletes a NS instance

    NAME: name or ID of the NS instance to be deleted
    """
    logger.debug("")
    if not force:
        ctx.obj.ns.delete(name, config=config, wait=wait)
    else:
        utils.check_client_version(ctx.obj, "--force")
        ctx.obj.ns.delete(name, force, config=config, wait=wait)
