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
import os
from typing import Any, Dict
import logging

logger = logging.getLogger("osmclient")


@click.command(name="vca-add", short_help="adds a VCA (Juju controller) to OSM")
@click.argument("name")
@click.option(
    "--endpoints",
    prompt=True,
    help="Comma-separated list of IP or hostnames of the Juju controller",
)
@click.option("--user", prompt=True, help="Username with admin priviledges")
@click.option("--secret", prompt=True, help="Password of the specified username")
@click.option("--cacert", prompt=True, help="CA certificate")
@click.option(
    "--lxd-cloud",
    prompt=True,
    help="Name of the cloud that will be used for LXD containers (LXD proxy charms)",
)
@click.option(
    "--lxd-credentials",
    prompt=True,
    help="Name of the cloud credentialsto be used for the LXD cloud",
)
@click.option(
    "--k8s-cloud",
    prompt=True,
    help="Name of the cloud that will be used for K8s containers (K8s proxy charms)",
)
@click.option(
    "--k8s-credentials",
    prompt=True,
    help="Name of the cloud credentialsto be used for the K8s cloud",
)
@click.option(
    "--model-config",
    default={},
    help="Configuration options for the models",
)
@click.option("--description", default=None, help="human readable description")
@click.pass_context
def vca_add(
    ctx,
    name,
    endpoints,
    user,
    secret,
    cacert,
    lxd_cloud,
    lxd_credentials,
    k8s_cloud,
    k8s_credentials,
    model_config,
    description,
):
    """adds a VCA to OSM

    NAME: name of the VCA
    """
    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    vca = {}
    vca["name"] = name
    vca["endpoints"] = endpoints.split(",")
    vca["user"] = user
    vca["secret"] = secret
    vca["cacert"] = cacert
    vca["lxd-cloud"] = lxd_cloud
    vca["lxd-credentials"] = lxd_credentials
    vca["k8s-cloud"] = k8s_cloud
    vca["k8s-credentials"] = k8s_credentials
    if description:
        vca["description"] = description
    if model_config:
        model_config = load(model_config)
        vca["model-config"] = model_config
    ctx.obj.vca.create(name, vca)


def load(data: Any):
    logger.debug("")
    if os.path.isfile(data):
        return load_file(data)
    else:
        try:
            return json.loads(data)
        except ValueError as e:
            raise ClientException(e)


def load_file(file_path: str) -> Dict:
    logger.debug("")
    content = None
    with open(file_path, "r") as f:
        content = f.read()
    try:
        return yaml.safe_load(content)
    except yaml.scanner.ScannerError:
        pass
    try:
        return json.loads(content)
    except ValueError:
        pass
    raise ClientException(f"{file_path} must be a valid yaml or json file")


@click.command(name="vca-update", short_help="updates a VCA")
@click.argument("name")
@click.option(
    "--endpoints", help="Comma-separated list of IP or hostnames of the Juju controller"
)
@click.option("--user", help="Username with admin priviledges")
@click.option("--secret", help="Password of the specified username")
@click.option("--cacert", help="CA certificate")
@click.option(
    "--lxd-cloud",
    help="Name of the cloud that will be used for LXD containers (LXD proxy charms)",
)
@click.option(
    "--lxd-credentials",
    help="Name of the cloud credentialsto be used for the LXD cloud",
)
@click.option(
    "--k8s-cloud",
    help="Name of the cloud that will be used for K8s containers (K8s proxy charms)",
)
@click.option(
    "--k8s-credentials",
    help="Name of the cloud credentialsto be used for the K8s cloud",
)
@click.option(
    "--model-config",
    help="Configuration options for the models",
)
@click.option("--description", default=None, help="human readable description")
@click.pass_context
def vca_update(
    ctx,
    name,
    endpoints,
    user,
    secret,
    cacert,
    lxd_cloud,
    lxd_credentials,
    k8s_cloud,
    k8s_credentials,
    model_config,
    description,
):
    """updates a VCA

    NAME: name or ID of the VCA
    """
    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    vca = {}
    vca["name"] = name
    if endpoints:
        vca["endpoints"] = endpoints.split(",")
    if user:
        vca["user"] = user
    if secret:
        vca["secret"] = secret
    if cacert:
        vca["cacert"] = cacert
    if lxd_cloud:
        vca["lxd-cloud"] = lxd_cloud
    if lxd_credentials:
        vca["lxd-credentials"] = lxd_credentials
    if k8s_cloud:
        vca["k8s-cloud"] = k8s_cloud
    if k8s_credentials:
        vca["k8s-credentials"] = k8s_credentials
    if description:
        vca["description"] = description
    if model_config:
        model_config = load(model_config)
        vca["model-config"] = model_config
    ctx.obj.vca.update(name, vca)


@click.command(name="vca-delete", short_help="deletes a VCA")
@click.argument("name")
@click.option(
    "--force", is_flag=True, help="forces the deletion from the DB (not recommended)"
)
@click.pass_context
def vca_delete(ctx, name, force):
    """deletes a VCA

    NAME: name or ID of the VCA to be deleted
    """
    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    ctx.obj.vca.delete(name, force=force)


@click.command(name="vca-list")
@click.option(
    "--filter",
    default=None,
    multiple=True,
    help="restricts the list to the VCAs matching the filter",
)
@click.option("--literal", is_flag=True, help="print literally, no pretty table")
@click.option("--long", is_flag=True, help="get more details")
@click.pass_context
def vca_list(ctx, filter, literal, long):
    """list VCAs"""
    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    if filter:
        filter = "&".join(filter)
    resp = ctx.obj.vca.list(filter)
    if literal:
        print(yaml.safe_dump(resp, indent=4, default_flow_style=False))
        return
    if long:
        table = PrettyTable(
            ["Name", "Id", "Project", "Operational State", "Detailed Status"]
        )
        project_list = ctx.obj.project.list()
    else:
        table = PrettyTable(["Name", "Id", "Operational State"])
    for vca in resp:
        logger.debug("VCA details: {}".format(yaml.safe_dump(vca)))
        if long:
            project_id, project_name = utils.get_project(project_list, vca)
            detailed_status = vca.get("_admin", {}).get("detailed-status", "-")
            table.add_row(
                [
                    vca["name"],
                    vca["_id"],
                    project_name,
                    vca.get("_admin", {}).get("operationalState", "-"),
                    utils.wrap_text(text=detailed_status, width=40),
                ]
            )
        else:
            table.add_row(
                [
                    vca["name"],
                    vca["_id"],
                    vca.get("_admin", {}).get("operationalState", "-"),
                ]
            )
    table.align = "l"
    print(table)


@click.command(name="vca-show", short_help="shows the details of a VCA")
@click.argument("name")
@click.option("--literal", is_flag=True, help="print literally, no pretty table")
@click.pass_context
def vca_show(ctx, name, literal):
    """shows the details of a VCA

    NAME: name or ID of the VCA
    """
    logger.debug("")
    resp = ctx.obj.vca.get(name)
    if literal:
        print(yaml.safe_dump(resp, indent=4, default_flow_style=False))
        return
    table = PrettyTable(["key", "attribute"])
    for k, v in list(resp.items()):
        table.add_row([k, utils.wrap_text(text=json.dumps(v, indent=2), width=100)])
    table.align = "l"
    print(table)
