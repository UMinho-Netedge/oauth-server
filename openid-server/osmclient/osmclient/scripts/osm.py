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
from osmclient import client
from osmclient.common.exceptions import ClientException
from osmclient.cli_commands import (
    alarms,
    k8scluster,
    metrics,
    netslice_instance,
    netslice_ops,
    netslice_template,
    nfpkg,
    ns,
    nslcm_ops,
    nslcm,
    nspkg,
    other,
    packages,
    pdus,
    rbac,
    repo,
    sdnc,
    subscriptions,
    vca,
    vim,
    vnf,
    wim,
)
import yaml
import pycurl
import os
import logging


@click.group(
    context_settings=dict(help_option_names=["-h", "--help"], max_content_width=160)
)
@click.option(
    "--hostname",
    default="127.0.0.1",
    envvar="OSM_HOSTNAME",
    help="hostname of server.  " + "Also can set OSM_HOSTNAME in environment",
)
@click.option(
    "--user",
    default=None,
    envvar="OSM_USER",
    help="user (defaults to admin). " + "Also can set OSM_USER in environment",
)
@click.option(
    "--password",
    default=None,
    envvar="OSM_PASSWORD",
    help="password (defaults to admin). " + "Also can set OSM_PASSWORD in environment",
)
@click.option(
    "--project",
    default=None,
    envvar="OSM_PROJECT",
    help="project (defaults to admin). " + "Also can set OSM_PROJECT in environment",
)
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="increase verbosity (-v INFO, -vv VERBOSE, -vvv DEBUG)",
)
@click.option("--all-projects", default=None, is_flag=True, help="include all projects")
@click.option(
    "--public/--no-public",
    default=None,
    help="flag for public items (packages, instances, VIM accounts, etc.)",
)
@click.option(
    "--project-domain-name",
    "project_domain_name",
    default=None,
    envvar="OSM_PROJECT_DOMAIN_NAME",
    help="project domain name for keystone authentication (default to None). "
    + "Also can set OSM_PROJECT_DOMAIN_NAME in environment",
)
@click.option(
    "--user-domain-name",
    "user_domain_name",
    default=None,
    envvar="OSM_USER_DOMAIN_NAME",
    help="user domain name for keystone authentication (default to None). "
    + "Also can set OSM_USER_DOMAIN_NAME in environment",
)
@click.pass_context
def cli_osm(ctx, **kwargs):
    global logger
    hostname = kwargs.pop("hostname", None)
    if hostname is None:
        print(
            (
                "either hostname option or OSM_HOSTNAME "
                + "environment variable needs to be specified"
            )
        )
        exit(1)
    # Remove None values
    kwargs = {k: v for k, v in kwargs.items() if v is not None}
    sol005 = os.getenv("OSM_SOL005", True)
    ctx.obj = client.Client(host=hostname, sol005=sol005, **kwargs)
    logger = logging.getLogger("osmclient")


# pylint: disable=no-value-for-parameter
def cli():
    try:
        cli_osm.add_command(alarms.alarm_list)
        cli_osm.add_command(alarms.alarm_show)
        cli_osm.add_command(alarms.alarm_update)
        cli_osm.add_command(alarms.ns_alarm_create)

        cli_osm.add_command(k8scluster.k8scluster_add)
        cli_osm.add_command(k8scluster.k8scluster_delete)
        cli_osm.add_command(k8scluster.k8scluster_list)
        cli_osm.add_command(k8scluster.k8scluster_show)
        cli_osm.add_command(k8scluster.k8scluster_update)

        cli_osm.add_command(metrics.ns_metric_export)

        cli_osm.add_command(k8scluster.k8scluster_delete)
        cli_osm.add_command(k8scluster.k8scluster_list)
        cli_osm.add_command(k8scluster.k8scluster_show)
        cli_osm.add_command(k8scluster.k8scluster_update)

        cli_osm.add_command(netslice_instance.nsi_create1)
        cli_osm.add_command(netslice_instance.nsi_create2)
        cli_osm.add_command(netslice_instance.nsi_delete1)
        cli_osm.add_command(netslice_instance.nsi_delete2)
        cli_osm.add_command(netslice_instance.nsi_list1)
        cli_osm.add_command(netslice_instance.nsi_list2)
        cli_osm.add_command(netslice_instance.nsi_show1)
        cli_osm.add_command(netslice_instance.nsi_show2)

        cli_osm.add_command(netslice_ops.nsi_op_list1)
        cli_osm.add_command(netslice_ops.nsi_op_list2)
        cli_osm.add_command(netslice_ops.nsi_op_show1)
        cli_osm.add_command(netslice_ops.nsi_op_show2)

        cli_osm.add_command(netslice_template.nst_create1)
        cli_osm.add_command(netslice_template.nst_create2)
        cli_osm.add_command(netslice_template.nst_delete1)
        cli_osm.add_command(netslice_template.nst_delete2)
        cli_osm.add_command(netslice_template.nst_list1)
        cli_osm.add_command(netslice_template.nst_list2)
        cli_osm.add_command(netslice_template.nst_show1)
        cli_osm.add_command(netslice_template.nst_show2)
        cli_osm.add_command(netslice_template.nst_update1)
        cli_osm.add_command(netslice_template.nst_update2)

        cli_osm.add_command(nfpkg.nfpkg_create)
        cli_osm.add_command(nfpkg.nfpkg_delete)
        cli_osm.add_command(nfpkg.nfpkg_list)
        cli_osm.add_command(nfpkg.nfpkg_show)
        cli_osm.add_command(nfpkg.nfpkg_update)
        cli_osm.add_command(nfpkg.vnfd_create1)
        cli_osm.add_command(nfpkg.vnfd_create2)
        cli_osm.add_command(nfpkg.vnfd_delete1)
        cli_osm.add_command(nfpkg.vnfd_delete2)
        cli_osm.add_command(nfpkg.vnfd_list1)
        cli_osm.add_command(nfpkg.vnfd_list2)
        cli_osm.add_command(nfpkg.vnfd_show1)
        cli_osm.add_command(nfpkg.vnfd_show2)
        cli_osm.add_command(nfpkg.vnfd_update1)
        cli_osm.add_command(nfpkg.vnfd_update2)

        cli_osm.add_command(ns.ns_create)
        cli_osm.add_command(ns.ns_delete)
        cli_osm.add_command(ns.ns_list)
        cli_osm.add_command(ns.ns_show)

        cli_osm.add_command(nslcm_ops.ns_op_list)
        cli_osm.add_command(nslcm_ops.ns_op_show)

        cli_osm.add_command(nslcm.ns_action)
        cli_osm.add_command(nslcm.vnf_scale)
        cli_osm.add_command(nslcm.ns_update)
        cli_osm.add_command(nslcm.ns_heal)
        cli_osm.add_command(nslcm.vnf_heal)

        cli_osm.add_command(nspkg.nsd_create1)
        cli_osm.add_command(nspkg.nsd_create2)
        cli_osm.add_command(nspkg.nsd_delete1)
        cli_osm.add_command(nspkg.nsd_delete2)
        cli_osm.add_command(nspkg.nsd_list1)
        cli_osm.add_command(nspkg.nsd_list2)
        cli_osm.add_command(nspkg.nsd_show1)
        cli_osm.add_command(nspkg.nsd_show2)
        cli_osm.add_command(nspkg.nsd_update1)
        cli_osm.add_command(nspkg.nsd_update2)

        cli_osm.add_command(other.get_version)

        cli_osm.add_command(packages.descriptor_translate)
        cli_osm.add_command(packages.package_build)
        cli_osm.add_command(packages.package_create)
        cli_osm.add_command(packages.package_translate)
        cli_osm.add_command(packages.package_validate)
        cli_osm.add_command(packages.upload_package)

        cli_osm.add_command(pdus.pdu_create)
        cli_osm.add_command(pdus.pdu_delete)
        cli_osm.add_command(pdus.pdu_list)
        cli_osm.add_command(pdus.pdu_show)
        cli_osm.add_command(pdus.pdu_update)

        cli_osm.add_command(rbac.project_create)
        cli_osm.add_command(rbac.project_delete)
        cli_osm.add_command(rbac.project_list)
        cli_osm.add_command(rbac.project_show)
        cli_osm.add_command(rbac.project_update)

        cli_osm.add_command(rbac.role_create)
        cli_osm.add_command(rbac.role_delete)
        cli_osm.add_command(rbac.role_list)
        cli_osm.add_command(rbac.role_show)
        cli_osm.add_command(rbac.role_update)

        cli_osm.add_command(rbac.user_create)
        cli_osm.add_command(rbac.user_delete)
        cli_osm.add_command(rbac.user_list)
        cli_osm.add_command(rbac.user_show)
        cli_osm.add_command(rbac.user_update)

        cli_osm.add_command(repo.repo_add)
        cli_osm.add_command(repo.repo_delete)
        cli_osm.add_command(repo.repo_list)
        cli_osm.add_command(repo.repo_show)
        cli_osm.add_command(repo.repo_update)

        cli_osm.add_command(repo.repo_index)
        cli_osm.add_command(repo.nfpkg_repo_list1)
        cli_osm.add_command(repo.nfpkg_repo_list2)
        cli_osm.add_command(repo.nfpkg_repo_list2)
        cli_osm.add_command(repo.nspkg_repo_list)
        cli_osm.add_command(repo.nspkg_repo_list2)
        cli_osm.add_command(repo.nsd_repo_show)
        cli_osm.add_command(repo.nsd_repo_show2)
        cli_osm.add_command(repo.vnfd_show1)
        cli_osm.add_command(repo.vnfd_show2)

        cli_osm.add_command(sdnc.sdnc_create)
        cli_osm.add_command(sdnc.sdnc_delete)
        cli_osm.add_command(sdnc.sdnc_list)
        cli_osm.add_command(sdnc.sdnc_show)
        cli_osm.add_command(sdnc.sdnc_update)

        cli_osm.add_command(subscriptions.subscription_create)
        cli_osm.add_command(subscriptions.subscription_delete)
        cli_osm.add_command(subscriptions.subscription_list)
        cli_osm.add_command(subscriptions.subscription_show)

        cli_osm.add_command(vca.vca_add)
        cli_osm.add_command(vca.vca_delete)
        cli_osm.add_command(vca.vca_list)
        cli_osm.add_command(vca.vca_show)
        cli_osm.add_command(vca.vca_update)

        cli_osm.add_command(vim.vim_create)
        cli_osm.add_command(vim.vim_delete)
        cli_osm.add_command(vim.vim_list)
        cli_osm.add_command(vim.vim_show)
        cli_osm.add_command(vim.vim_update)

        cli_osm.add_command(vnf.nf_list)
        cli_osm.add_command(vnf.vnf_list1)
        cli_osm.add_command(vnf.vnf_show)

        cli_osm.add_command(wim.wim_create)
        cli_osm.add_command(wim.wim_delete)
        cli_osm.add_command(wim.wim_list)
        cli_osm.add_command(wim.wim_show)
        cli_osm.add_command(wim.wim_update)

        cli_osm()
        exit(0)
    except pycurl.error as exc:
        print(exc)
        print(
            'Maybe "--hostname" option or OSM_HOSTNAME environment variable needs to be specified'
        )
    except ClientException as exc:
        print("ERROR: {}".format(exc))
    except (FileNotFoundError, PermissionError) as exc:
        print("Cannot open file: {}".format(exc))
    except yaml.YAMLError as exc:
        print("Invalid YAML format: {}".format(exc))
    exit(1)
    # TODO capture other controlled exceptions here
    # TODO remove the ClientException captures from all places, unless they do something different


if __name__ == "__main__":
    cli()
