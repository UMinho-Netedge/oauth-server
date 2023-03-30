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
import time
import logging

logger = logging.getLogger("osmclient")


@click.command(
    name="ns-metric-export",
    short_help="exports a metric to the internal OSM bus, which can be read by other apps",
)
@click.option("--ns", prompt=True, help="NS instance id or name")
@click.option(
    "--vnf", prompt=True, help="VNF name (VNF member index as declared in the NSD)"
)
@click.option("--vdu", prompt=True, help="VDU name (VDU name as declared in the VNFD)")
@click.option("--metric", prompt=True, help="name of the metric (e.g. cpu_utilization)")
# @click.option('--period', default='1w',
#              help='metric collection period (e.g. 20s, 30m, 2h, 3d, 1w)')
@click.option(
    "--interval", help="periodic interval (seconds) to export metrics continuously"
)
@click.pass_context
def ns_metric_export(ctx, ns, vnf, vdu, metric, interval):
    """exports a metric to the internal OSM bus, which can be read by other apps"""
    # TODO: Check how to validate interval.
    # Should it be an integer (seconds), or should a suffix (s,m,h,d,w) also be permitted?
    logger.debug("")
    ns_instance = ctx.obj.ns.get(ns)
    metric_data = {}
    metric_data["ns_id"] = ns_instance["_id"]
    metric_data["correlation_id"] = ns_instance["_id"]
    metric_data["vnf_member_index"] = vnf
    metric_data["vdu_name"] = vdu
    metric_data["metric_name"] = metric
    metric_data["collection_unit"] = "WEEK"
    metric_data["collection_period"] = 1
    utils.check_client_version(ctx.obj, ctx.command.name)
    if not interval:
        print("{}".format(ctx.obj.ns.export_metric(metric_data)))
    else:
        i = 1
        while True:
            print("{} {}".format(ctx.obj.ns.export_metric(metric_data), i))
            time.sleep(int(interval))
            i += 1
