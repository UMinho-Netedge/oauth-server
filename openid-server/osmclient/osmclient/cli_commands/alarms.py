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
import json
import os
import logging

logger = logging.getLogger("osmclient")


@click.command(name="ns-alarm-create")
@click.argument("name")
@click.option("--ns", prompt=True, help="NS instance id or name")
@click.option(
    "--vnf", prompt=True, help="VNF name (VNF member index as declared in the NSD)"
)
@click.option("--vdu", prompt=True, help="VDU name (VDU name as declared in the VNFD)")
@click.option("--metric", prompt=True, help="Name of the metric (e.g. cpu_utilization)")
@click.option(
    "--severity",
    default="WARNING",
    help="severity of the alarm (WARNING, MINOR, MAJOR, CRITICAL, INDETERMINATE)",
)
@click.option(
    "--threshold_value",
    prompt=True,
    help="threshold value that, when crossed, an alarm is triggered",
)
@click.option(
    "--threshold_operator",
    prompt=True,
    help="threshold operator describing the comparison (GE, LE, GT, LT, EQ)",
)
@click.option(
    "--statistic",
    default="AVERAGE",
    help="statistic (AVERAGE, MINIMUM, MAXIMUM, COUNT, SUM)",
)
@click.pass_context
def ns_alarm_create(
    ctx,
    name,
    ns,
    vnf,
    vdu,
    metric,
    severity,
    threshold_value,
    threshold_operator,
    statistic,
):
    """creates a new alarm for a NS instance"""
    # TODO: Check how to validate threshold_value.
    # Should it be an integer (1-100), percentage, or decimal (0.01-1.00)?
    logger.debug("")
    ns_instance = ctx.obj.ns.get(ns)
    alarm = {}
    alarm["alarm_name"] = name
    alarm["ns_id"] = ns_instance["_id"]
    alarm["correlation_id"] = ns_instance["_id"]
    alarm["vnf_member_index"] = vnf
    alarm["vdu_name"] = vdu
    alarm["metric_name"] = metric
    alarm["severity"] = severity
    alarm["threshold_value"] = int(threshold_value)
    alarm["operation"] = threshold_operator
    alarm["statistic"] = statistic
    utils.check_client_version(ctx.obj, ctx.command.name)
    ctx.obj.ns.create_alarm(alarm)


@click.command(name="alarm-show", short_help="show alarm details")
@click.argument("uuid")
@click.pass_context
def alarm_show(ctx, uuid):
    """Show alarm's detail information"""

    utils.check_client_version(ctx.obj, ctx.command.name)
    resp = ctx.obj.ns.get_alarm(uuid=uuid)
    alarm_filter = [
        "uuid",
        "name",
        "metric",
        "statistic",
        "threshold",
        "operation",
        "ns-id",
        "vnf-id",
        "vdu_name",
        "action",
        "status",
    ]
    table = PrettyTable(["key", "attribute"])
    try:
        # Arrange and return the response data
        alarm = resp.replace("ObjectId", "")
        for key in alarm_filter:
            if key == "uuid":
                value = alarm.get(key)
                key = "alarm-id"
            elif key == "name":
                value = alarm.get(key)
                key = "alarm-name"
            elif key == "ns-id":
                value = alarm["tags"].get("ns_id")
            elif key == "vdu_name":
                value = alarm["tags"].get("vdu_name")
            elif key == "status":
                value = alarm["alarm_status"]
            else:
                value = alarm[key]
            table.add_row(
                [key, utils.wrap_text(text=json.dumps(value, indent=2), width=100)]
            )
        table.align = "l"
        print(table)
    except Exception:
        print(resp)
    # TODO: check the reason for the try-except


# List alarm
@click.command(name="alarm-list", short_help="list all alarms")
@click.option(
    "--ns_id", default=None, required=False, help="List out alarm for given ns id"
)
@click.pass_context
def alarm_list(ctx, ns_id):
    """list all alarms"""

    utils.check_client_version(ctx.obj, ctx.command.name)
    project_name = os.getenv("OSM_PROJECT", "admin")
    # TODO: check the reason for this^
    resp = ctx.obj.ns.get_alarm(project_name=project_name, ns_id=ns_id)

    table = PrettyTable(
        ["alarm-id", "metric", "threshold", "operation", "action", "status"]
    )
    if resp:
        # return the response data in a table
        resp = resp.replace("ObjectId", "")
        for alarm in resp:
            table.add_row(
                [
                    utils.wrap_text(text=str(alarm["uuid"]), width=38),
                    alarm["metric"],
                    alarm["threshold"],
                    alarm["operation"],
                    utils.wrap_text(text=alarm["action"], width=25),
                    alarm["alarm_status"],
                ]
            )
    table.align = "l"
    print(table)


# Update alarm
@click.command(name="alarm-update", short_help="Update a alarm")
@click.argument("uuid")
@click.option("--threshold", default=None, help="Alarm threshold")
@click.option("--is_enable", default=None, type=bool, help="enable or disable alarm")
@click.pass_context
def alarm_update(ctx, uuid, threshold, is_enable):
    """
    Update alarm

    """
    if not threshold and is_enable is None:
        raise ClientException(
            "Please provide option to update i.e threshold or is_enable"
        )
    ctx.obj.ns.update_alarm(uuid, threshold, is_enable)
