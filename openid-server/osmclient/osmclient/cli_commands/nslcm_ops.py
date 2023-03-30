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
from datetime import datetime
import logging

logger = logging.getLogger("osmclient")


@click.command(
    name="ns-op-list", short_help="shows the history of operations over a NS instance"
)
@click.argument("name")
@click.option(
    "--long", is_flag=True, help="get more details of the NS operation (date, )."
)
@click.pass_context
def ns_op_list(ctx, name, long):
    """shows the history of operations over a NS instance

    NAME: name or ID of the NS instance
    """

    def formatParams(params):
        if params["lcmOperationType"] == "instantiate":
            params.pop("nsDescription")
            params.pop("nsName")
            params.pop("nsdId")
            params.pop("nsr_id")
        elif params["lcmOperationType"] == "action":
            params.pop("primitive")
        params.pop("lcmOperationType")
        params.pop("nsInstanceId")
        return params

    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    resp = ctx.obj.ns.list_op(name)

    if long:
        table = PrettyTable(
            [
                "id",
                "operation",
                "action_name",
                "operation_params",
                "status",
                "date",
                "last update",
                "detail",
            ]
        )
    else:
        table = PrettyTable(
            ["id", "operation", "action_name", "status", "date", "detail"]
        )

    # print(yaml.safe_dump(resp))
    for op in resp:
        action_name = "N/A"
        if op["lcmOperationType"] == "action":
            action_name = op["operationParams"]["primitive"]
        detail = "-"
        if op["operationState"] == "PROCESSING":
            if op.get("queuePosition") is not None and op.get("queuePosition") > 0:
                detail = "In queue. Current position: {}".format(op["queuePosition"])
            elif op["lcmOperationType"] in ("instantiate", "terminate"):
                if op["stage"]:
                    detail = op["stage"]
        elif op["operationState"] in ("FAILED", "FAILED_TEMP"):
            detail = op.get("errorMessage", "-")
        date = datetime.fromtimestamp(op["startTime"]).strftime("%Y-%m-%dT%H:%M:%S")
        last_update = datetime.fromtimestamp(op["statusEnteredTime"]).strftime(
            "%Y-%m-%dT%H:%M:%S"
        )
        if long:
            table.add_row(
                [
                    op["id"],
                    op["lcmOperationType"],
                    action_name,
                    utils.wrap_text(
                        text=json.dumps(formatParams(op["operationParams"]), indent=2),
                        width=50,
                    ),
                    op["operationState"],
                    date,
                    last_update,
                    utils.wrap_text(text=detail, width=50),
                ]
            )
        else:
            table.add_row(
                [
                    op["id"],
                    op["lcmOperationType"],
                    action_name,
                    op["operationState"],
                    date,
                    utils.wrap_text(text=detail or "", width=50),
                ]
            )
    table.align = "l"
    print(table)


@click.command(name="ns-op-show", short_help="shows the info of a NS operation")
@click.argument("id")
@click.option(
    "--filter",
    multiple=True,
    help="restricts the information to the fields in the filter",
)
@click.option("--literal", is_flag=True, help="print literally, no pretty table")
@click.pass_context
def ns_op_show(ctx, id, filter, literal):
    """shows the detailed info of a NS operation

    ID: operation identifier
    """
    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    op_info = ctx.obj.ns.get_op(id)

    if literal:
        print(yaml.safe_dump(op_info, indent=4, default_flow_style=False))
        return

    table = PrettyTable(["field", "value"])
    for k, v in list(op_info.items()):
        if not filter or k in filter:
            table.add_row([k, utils.wrap_text(json.dumps(v, indent=2), 100)])
    table.align = "l"
    print(table)
