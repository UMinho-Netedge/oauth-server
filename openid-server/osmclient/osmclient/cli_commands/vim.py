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


def _check_ca_cert(vim_config: dict) -> None:
    """
    Checks if the VIM has a CA certificate.
    In that case, reads the content and add it to the config
    : param vim_config: configuration provided with the VIM creation
    : return: None
    """

    if vim_config.get("ca_cert"):
        with open(vim_config["ca_cert"], "r") as cert_f:
            vim_config["ca_cert_content"] = str(cert_f.read())
            del vim_config["ca_cert"]


@click.command(name="vim-create", short_help="creates a new VIM account")
@click.option("--name", required=True, help="Name to create datacenter")
@click.option("--user", default=None, help="VIM username")
@click.option("--password", default=None, help="VIM password")
@click.option("--auth_url", default=None, help="VIM url")
@click.option(
    "--tenant", "--project", "tenant", default=None, help="VIM tenant/project name"
)
@click.option("--config", default=None, help="VIM specific config parameters")
@click.option(
    "--config_file",
    default=None,
    help="VIM specific config parameters in YAML or JSON file",
)
@click.option("--account_type", default="openstack", help="VIM type")
@click.option("--description", default=None, help="human readable description")
@click.option(
    "--sdn_controller",
    default=None,
    help="Name or id of the SDN controller associated to this VIM account",
)
@click.option(
    "--sdn_port_mapping",
    default=None,
    help="File describing the port mapping between compute nodes' ports and switch ports",
)
@click.option(
    "--wait",
    required=False,
    default=False,
    is_flag=True,
    help="do not return the control immediately, but keep it "
    "until the operation is completed, or timeout",
)
@click.option("--vca", default=None, help="VCA to be used in this VIM account")
@click.option(
    "--creds", default=None, help="credentials file (only applicable for GCP VIM type)"
)
@click.option(
    "--prometheus_url",
    default=None,
    help="PrometheusTSBD URL to get VIM data",
)
@click.option(
    "--prometheus_map",
    default=None,
    help="PrometheusTSBD metrics mapping for VIM data",
)
@click.option(
    "--prometheus_config_file",
    default=None,
    help="Prometheus configuration to get VIM data",
)
@click.pass_context
def vim_create(
    ctx,
    name,
    user,
    password,
    auth_url,
    tenant,
    config,
    config_file,
    account_type,
    description,
    sdn_controller,
    sdn_port_mapping,
    wait,
    vca,
    creds,
    prometheus_url,
    prometheus_map,
    prometheus_config_file,
):
    """creates a new VIM account"""
    logger.debug("")
    if sdn_controller:
        utils.check_client_version(ctx.obj, "--sdn_controller")
    if sdn_port_mapping:
        utils.check_client_version(ctx.obj, "--sdn_port_mapping")
    vim = {}
    prometheus_config = {}
    if prometheus_url:
        prometheus_config["prometheus-url"] = prometheus_url
    if prometheus_map:
        prometheus_config["prometheus-map"] = prometheus_map
    if prometheus_config_file:
        with open(prometheus_config_file) as prometheus_file:
            prometheus_config_dict = json.load(prometheus_file)
        prometheus_config.update(prometheus_config_dict)
    if prometheus_config:
        vim["prometheus-config"] = prometheus_config
    vim["vim-username"] = user
    vim["vim-password"] = password
    vim["vim-url"] = auth_url
    vim["vim-tenant-name"] = tenant
    vim["vim-type"] = account_type
    vim["description"] = description
    if vca:
        vim["vca"] = vca
    vim_config = utils.create_config(config_file, config)
    _check_ca_cert(vim_config)
    if creds:
        with open(creds, "r") as cf:
            vim_config["credentials"] = yaml.safe_load(cf.read())
    ctx.obj.vim.create(
        name, vim, vim_config, sdn_controller, sdn_port_mapping, wait=wait
    )


@click.command(name="vim-update", short_help="updates a VIM account")
@click.argument("name")
@click.option("--newname", help="New name for the VIM account")
@click.option("--user", help="VIM username")
@click.option("--password", help="VIM password")
@click.option("--auth_url", help="VIM url")
@click.option("--tenant", help="VIM tenant name")
@click.option("--config", help="VIM specific config parameters")
@click.option(
    "--config_file",
    default=None,
    help="VIM specific config parameters in YAML or JSON file",
)
@click.option("--account_type", help="VIM type")
@click.option("--description", help="human readable description")
@click.option(
    "--sdn_controller",
    default=None,
    help="Name or id of the SDN controller to be associated with this VIM"
    "account. Use empty string to disassociate",
)
@click.option(
    "--sdn_port_mapping",
    default=None,
    help="File describing the port mapping between compute nodes' ports and switch ports",
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
    "--creds", default=None, help="credentials file (only applicable for GCP VIM type)"
)
@click.option(
    "--prometheus_url",
    default=None,
    help="PrometheusTSBD URL to get VIM data",
)
@click.option(
    "--prometheus_map",
    default=None,
    help="PrometheusTSBD metrics mapping for VIM data",
)
@click.option(
    "--prometheus_config_file",
    default=None,
    help="Prometheus configuration to get VIM data",
)
@click.pass_context
def vim_update(
    ctx,
    name,
    newname,
    user,
    password,
    auth_url,
    tenant,
    config,
    config_file,
    account_type,
    description,
    sdn_controller,
    sdn_port_mapping,
    wait,
    creds,
    prometheus_url,
    prometheus_map,
    prometheus_config_file,
):
    """updates a VIM account

    NAME: name or ID of the VIM account
    """
    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    vim = {}
    if newname:
        vim["name"] = newname
    if user:
        vim["vim_user"] = user
    if password:
        vim["vim_password"] = password
    if auth_url:
        vim["vim_url"] = auth_url
    if tenant:
        vim["vim-tenant-name"] = tenant
    if account_type:
        vim["vim_type"] = account_type
    if description:
        vim["description"] = description
    vim_config = None
    if config or config_file:
        vim_config = utils.create_config(config_file, config)
        _check_ca_cert(vim_config)
    if creds:
        with open(creds, "r") as cf:
            vim_config["credentials"] = yaml.safe_load(cf.read())
    prometheus_config = {}
    if prometheus_url:
        prometheus_config["prometheus-url"] = prometheus_url
    if prometheus_map:
        prometheus_config["prometheus-map"] = prometheus_map
    if prometheus_config_file:
        with open(prometheus_config_file) as prometheus_file:
            prometheus_config_dict = json.load(prometheus_file)
        prometheus_config.update(prometheus_config_dict)
    if prometheus_config:
        vim["prometheus-config"] = prometheus_config
    ctx.obj.vim.update(
        name, vim, vim_config, sdn_controller, sdn_port_mapping, wait=wait
    )


@click.command(name="vim-delete", short_help="deletes a VIM account")
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
def vim_delete(ctx, name, force, wait):
    """deletes a VIM account

    NAME: name or ID of the VIM account to be deleted
    """
    logger.debug("")
    if not force:
        ctx.obj.vim.delete(name, wait=wait)
    else:
        utils.check_client_version(ctx.obj, "--force")
        ctx.obj.vim.delete(name, force, wait=wait)


@click.command(name="vim-list", short_help="list all VIM accounts")
@click.option(
    "--filter",
    default=None,
    multiple=True,
    help="restricts the list to the VIM accounts matching the filter",
)
@click.option(
    "--long",
    is_flag=True,
    help="get more details of the NS (project, vim, deployment status, configuration status.",
)
@click.pass_context
def vim_list(ctx, filter, long):
    """list all VIM accounts"""
    logger.debug("")
    if filter:
        filter = "&".join(filter)
        utils.check_client_version(ctx.obj, "--filter")
    fullclassname = ctx.obj.__module__ + "." + ctx.obj.__class__.__name__
    if fullclassname == "osmclient.sol005.client.Client":
        resp = ctx.obj.vim.list(filter)
    if long:
        table = PrettyTable(
            ["vim name", "uuid", "project", "operational state", "error details"]
        )
        project_list = ctx.obj.project.list()
    else:
        table = PrettyTable(["vim name", "uuid", "operational state"])
    for vim in resp:
        if long:
            if "vim_password" in vim:
                vim["vim_password"] = "********"
            if "config" in vim and "credentials" in vim["config"]:
                vim["config"]["credentials"] = "********"
            logger.debug("VIM details: {}".format(yaml.safe_dump(vim)))
            vim_state = vim["_admin"].get("operationalState", "-")
            error_details = "N/A"
            if vim_state == "ERROR":
                error_details = vim["_admin"].get("detailed-status", "Not found")
            project_id, project_name = utils.get_project(project_list, vim)
            # project_info = '{} ({})'.format(project_name, project_id)
            project_info = project_name
            table.add_row(
                [
                    vim["name"],
                    vim["uuid"],
                    project_info,
                    vim_state,
                    utils.wrap_text(text=error_details, width=80),
                ]
            )
        else:
            table.add_row(
                [vim["name"], vim["uuid"], vim["_admin"].get("operationalState", "-")]
            )
    table.align = "l"
    print(table)


@click.command(name="vim-show", short_help="shows the details of a VIM account")
@click.argument("name")
@click.option(
    "--filter",
    multiple=True,
    help="restricts the information to the fields in the filter",
)
@click.option("--literal", is_flag=True, help="print literally, no pretty table")
@click.pass_context
def vim_show(ctx, name, filter, literal):
    """shows the details of a VIM account

    NAME: name or ID of the VIM account
    """
    logger.debug("")
    resp = ctx.obj.vim.get(name)
    if "vim_password" in resp:
        resp["vim_password"] = "********"
    if "config" in resp and "credentials" in resp["config"]:
        resp["config"]["credentials"] = "********"

    if literal:
        print(yaml.safe_dump(resp, indent=4, default_flow_style=False))
        return
    table = PrettyTable(["key", "attribute"])
    for k, v in list(resp.items()):
        if not filter or k in filter:
            table.add_row([k, utils.wrap_text(text=json.dumps(v, indent=2), width=100)])
    table.align = "l"
    print(table)
