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


@click.command(name="k8scluster-add", short_help="adds a K8s cluster to OSM")
@click.argument("name")
@click.option(
    "--creds", prompt=True, help="credentials file, i.e. a valid `.kube/config` file"
)
@click.option("--version", prompt=True, help="Kubernetes version")
@click.option(
    "--vim", prompt=True, help="VIM target, the VIM where the cluster resides"
)
@click.option(
    "--k8s-nets",
    prompt=True,
    help='''list of VIM networks, in JSON inline format, where the cluster is
    accessible via L3 routing, e.g. "{(k8s_net1:vim_network1) [,(k8s_net2:vim_network2) ...]}"''',
)
@click.option(
    "--init-helm2/--skip-helm2",
    required=False,
    default=True,
    help="Initialize helm v2",
)
@click.option(
    "--init-helm3/--skip-helm3",
    required=False,
    default=True,
    help="Initialize helm v3",
)
@click.option(
    "--init-jujubundle/--skip-jujubundle",
    required=False,
    default=True,
    help="Initialize juju-bundle",
)
@click.option("--description", default=None, help="human readable description")
@click.option(
    "--namespace",
    default="kube-system",
    help="namespace to be used for its operation, defaults to `kube-system`",
)
@click.option(
    "--wait",
    required=False,
    default=False,
    is_flag=True,
    help="do not return the control immediately, but keep it "
    "until the operation is completed, or timeout",
)
@click.option(
    "--cni",
    default=None,
    help="list of CNI plugins, in JSON inline format, used in the cluster",
)
# @click.option('--skip-init',
#              is_flag=True,
#              help='If set, K8s cluster is assumed to be ready for its use with OSM')
@click.pass_context
def k8scluster_add(
    ctx,
    name,
    creds,
    version,
    vim,
    k8s_nets,
    init_helm2,
    init_helm3,
    init_jujubundle,
    description,
    namespace,
    wait,
    cni,
):
    """adds a K8s cluster to OSM

    NAME: name of the K8s cluster
    """
    utils.check_client_version(ctx.obj, ctx.command.name)
    cluster = {}
    cluster["name"] = name
    with open(creds, "r") as cf:
        cluster["credentials"] = yaml.safe_load(cf.read())
    cluster["k8s_version"] = version
    cluster["vim_account"] = vim
    cluster["nets"] = yaml.safe_load(k8s_nets)
    if not (init_helm2 and init_jujubundle and init_helm3):
        cluster["deployment_methods"] = {
            "helm-chart": init_helm2,
            "juju-bundle": init_jujubundle,
            "helm-chart-v3": init_helm3,
        }
    if description:
        cluster["description"] = description
    if namespace:
        cluster["namespace"] = namespace
    if cni:
        cluster["cni"] = yaml.safe_load(cni)
    ctx.obj.k8scluster.create(name, cluster, wait)


@click.command(name="k8scluster-update", short_help="updates a K8s cluster")
@click.argument("name")
@click.option("--newname", help="New name for the K8s cluster")
@click.option("--creds", help="credentials file, i.e. a valid `.kube/config` file")
@click.option("--version", help="Kubernetes version")
@click.option("--vim", help="VIM target, the VIM where the cluster resides")
@click.option(
    "--k8s-nets",
    help='''list of VIM networks, in JSON inline format, where the cluster is accessible
    via L3 routing, e.g. "{(k8s_net1:vim_network1) [,(k8s_net2:vim_network2) ...]}"''',
)
@click.option("--description", help="human readable description")
@click.option(
    "--namespace",
    help="namespace to be used for its operation, defaults to `kube-system`",
)
@click.option(
    "--wait",
    required=False,
    default=False,
    is_flag=True,
    help="do not return the control immediately, but keep it "
    "until the operation is completed, or timeout",
)
@click.option(
    "--cni", help="list of CNI plugins, in JSON inline format, used in the cluster"
)
@click.pass_context
def k8scluster_update(
    ctx, name, newname, creds, version, vim, k8s_nets, description, namespace, wait, cni
):
    """updates a K8s cluster

    NAME: name or ID of the K8s cluster
    """
    utils.check_client_version(ctx.obj, ctx.command.name)
    cluster = {}
    if newname:
        cluster["name"] = newname
    if creds:
        with open(creds, "r") as cf:
            cluster["credentials"] = yaml.safe_load(cf.read())
    if version:
        cluster["k8s_version"] = version
    if vim:
        cluster["vim_account"] = vim
    if k8s_nets:
        cluster["nets"] = yaml.safe_load(k8s_nets)
    if description:
        cluster["description"] = description
    if namespace:
        cluster["namespace"] = namespace
    if cni:
        cluster["cni"] = yaml.safe_load(cni)
    ctx.obj.k8scluster.update(name, cluster, wait)


@click.command(name="k8scluster-delete", short_help="deletes a K8s cluster")
@click.argument("name")
@click.option(
    "--force", is_flag=True, help="forces the deletion from the DB (not recommended)"
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
def k8scluster_delete(ctx, name, force, wait):
    """deletes a K8s cluster

    NAME: name or ID of the K8s cluster to be deleted
    """
    utils.check_client_version(ctx.obj, ctx.command.name)
    ctx.obj.k8scluster.delete(name, force, wait)


@click.command(name="k8scluster-list")
@click.option(
    "--filter",
    default=None,
    multiple=True,
    help="restricts the list to the K8s clusters matching the filter",
)
@click.option("--literal", is_flag=True, help="print literally, no pretty table")
@click.option("--long", is_flag=True, help="get more details")
@click.pass_context
def k8scluster_list(ctx, filter, literal, long):
    """list all K8s clusters"""
    utils.check_client_version(ctx.obj, ctx.command.name)
    if filter:
        filter = "&".join(filter)
    resp = ctx.obj.k8scluster.list(filter)
    if literal:
        print(yaml.safe_dump(resp, indent=4, default_flow_style=False))
        return
    if long:
        table = PrettyTable(
            [
                "Name",
                "Id",
                "Project",
                "Version",
                "VIM",
                "K8s-nets",
                "Deployment methods",
                "Operational State",
                "Op. state (details)",
                "Description",
                "Detailed status",
            ]
        )
        project_list = ctx.obj.project.list()
    else:
        table = PrettyTable(
            ["Name", "Id", "VIM", "Operational State", "Op. state details"]
        )
    try:
        vim_list = ctx.obj.vim.list()
    except Exception:
        vim_list = []
    for cluster in resp:
        logger.debug("Cluster details: {}".format(yaml.safe_dump(cluster)))
        vim_name = utils.get_vim_name(vim_list, cluster["vim_account"])
        # vim_info = '{} ({})'.format(vim_name,cluster['vim_account'])
        vim_info = vim_name
        op_state_details = "Helm: {}\nJuju: {}".format(
            cluster["_admin"].get("helm-chart", {}).get("operationalState", "-"),
            cluster["_admin"].get("juju-bundle", {}).get("operationalState", "-"),
        )
        if long:
            project_id, project_name = utils.get_project(project_list, cluster)
            # project_info = '{} ({})'.format(project_name, project_id)
            project_info = project_name
            detailed_status = cluster["_admin"].get("detailed-status", "-")
            table.add_row(
                [
                    cluster["name"],
                    cluster["_id"],
                    project_info,
                    cluster["k8s_version"],
                    vim_info,
                    json.dumps(cluster["nets"]),
                    json.dumps(cluster["deployment_methods"]),
                    cluster["_admin"]["operationalState"],
                    op_state_details,
                    utils.trunc_text(cluster.get("description") or "", 40),
                    utils.wrap_text(text=detailed_status, width=40),
                ]
            )
        else:
            table.add_row(
                [
                    cluster["name"],
                    cluster["_id"],
                    vim_info,
                    cluster["_admin"]["operationalState"],
                    op_state_details,
                ]
            )
    table.align = "l"
    print(table)


@click.command(name="k8scluster-show", short_help="shows the details of a K8s cluster")
@click.argument("name")
@click.option("--literal", is_flag=True, help="print literally, no pretty table")
@click.pass_context
def k8scluster_show(ctx, name, literal):
    """shows the details of a K8s cluster

    NAME: name or ID of the K8s cluster
    """
    resp = ctx.obj.k8scluster.get(name)
    if literal:
        print(yaml.safe_dump(resp, indent=4, default_flow_style=False))
        return
    table = PrettyTable(["key", "attribute"])
    for k, v in list(resp.items()):
        table.add_row([k, utils.wrap_text(text=json.dumps(v, indent=2), width=100)])
    table.align = "l"
    print(table)
