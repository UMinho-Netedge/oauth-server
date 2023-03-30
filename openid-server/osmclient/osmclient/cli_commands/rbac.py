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
import logging

logger = logging.getLogger("osmclient")


##############################
# Role Management Operations #
##############################


@click.command(name="role-create", short_help="creates a new role")
@click.argument("name")
@click.option("--permissions", default=None, help="role permissions using a dictionary")
@click.pass_context
def role_create(ctx, name, permissions):
    """
    Creates a new role.

    \b
    NAME: Name or ID of the role.
    DEFINITION: Definition of grant/denial of access to resources.
    """
    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    ctx.obj.role.create(name, permissions)


@click.command(name="role-update", short_help="updates a role")
@click.argument("name")
@click.option("--set-name", default=None, help="change name of rle")
@click.option(
    "--add",
    default=None,
    help="yaml format dictionary with permission: True/False to access grant/denial",
)
@click.option("--remove", default=None, help="yaml format list to remove a permission")
@click.pass_context
def role_update(ctx, name, set_name, add, remove):
    """
    Updates a role.

    \b
    NAME: Name or ID of the role.
    DEFINITION: Definition overwrites the old definition.
    ADD: Grant/denial of access to resource to add.
    REMOVE: Grant/denial of access to resource to remove.
    """
    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    ctx.obj.role.update(name, set_name, None, add, remove)


@click.command(name="role-delete", short_help="deletes a role")
@click.argument("name")
@click.pass_context
def role_delete(ctx, name):
    """
    Deletes a role.

    \b
    NAME: Name or ID of the role.
    """
    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    ctx.obj.role.delete(name)


@click.command(name="role-list", short_help="list all roles")
@click.option(
    "--filter",
    default=None,
    multiple=True,
    help="restricts the list to the projects matching the filter",
)
@click.pass_context
def role_list(ctx, filter):
    """
    List all roles.
    """
    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    if filter:
        filter = "&".join(filter)
    resp = ctx.obj.role.list(filter)
    table = PrettyTable(["name", "id"])
    for role in resp:
        table.add_row([role["name"], role["_id"]])
    table.align = "l"
    print(table)


@click.command(name="role-show", short_help="show specific role")
@click.argument("name")
@click.pass_context
def role_show(ctx, name):
    """
    Shows the details of a role.

    \b
    NAME: Name or ID of the role.
    """
    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    resp = ctx.obj.role.get(name)

    table = PrettyTable(["key", "attribute"])
    for k, v in resp.items():
        table.add_row([k, json.dumps(v, indent=2)])
    table.align = "l"
    print(table)


####################
# Project mgmt operations
####################


@click.command(name="project-create", short_help="creates a new project")
@click.argument("name")
# @click.option('--description',
#              default='no description',
#              help='human readable description')
@click.option("--domain-name", "domain_name", default=None, help="assign to a domain")
@click.option(
    "--quotas",
    "quotas",
    multiple=True,
    default=None,
    help="provide quotas. Can be used several times: 'quota1=number[,quota2=number,...]'. Quotas can be one "
    "of vnfds, nsds, nsts, pdus, nsrs, nsis, vim_accounts, wim_accounts, sdns, k8sclusters, k8srepos",
)
@click.pass_context
def project_create(ctx, name, domain_name, quotas):
    """Creates a new project

    NAME: name of the project
    DOMAIN_NAME: optional domain name for the project when keystone authentication is used
    QUOTAS: set quotas for the project
    """
    logger.debug("")
    project = {"name": name}
    if domain_name:
        project["domain_name"] = domain_name
    quotas_dict = _process_project_quotas(quotas)
    if quotas_dict:
        project["quotas"] = quotas_dict

    utils.check_client_version(ctx.obj, ctx.command.name)
    ctx.obj.project.create(name, project)


def _process_project_quotas(quota_list):
    quotas_dict = {}
    if not quota_list:
        return quotas_dict
    try:
        for quota in quota_list:
            for single_quota in quota.split(","):
                k, v = single_quota.split("=")
                quotas_dict[k] = None if v in ("None", "null", "") else int(v)
    except (ValueError, TypeError):
        raise ClientException(
            "invalid format for 'quotas'. Use 'k1=v1,v1=v2'. v must be a integer or null"
        )
    return quotas_dict


@click.command(name="project-delete", short_help="deletes a project")
@click.argument("name")
@click.pass_context
def project_delete(ctx, name):
    """deletes a project

    NAME: name or ID of the project to be deleted
    """
    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    ctx.obj.project.delete(name)


@click.command(name="project-list", short_help="list all projects")
@click.option(
    "--filter",
    default=None,
    multiple=True,
    help="restricts the list to the projects matching the filter",
)
@click.pass_context
def project_list(ctx, filter):
    """list all projects"""
    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    if filter:
        filter = "&".join(filter)
    resp = ctx.obj.project.list(filter)
    table = PrettyTable(["name", "id"])
    for proj in resp:
        table.add_row([proj["name"], proj["_id"]])
    table.align = "l"
    print(table)


@click.command(name="project-show", short_help="shows the details of a project")
@click.argument("name")
@click.pass_context
def project_show(ctx, name):
    """shows the details of a project

    NAME: name or ID of the project
    """
    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    resp = ctx.obj.project.get(name)

    table = PrettyTable(["key", "attribute"])
    for k, v in resp.items():
        table.add_row([k, json.dumps(v, indent=2)])
    table.align = "l"
    print(table)


@click.command(
    name="project-update", short_help="updates a project (only the name can be updated)"
)
@click.argument("project")
@click.option("--name", default=None, help="new name for the project")
@click.option(
    "--quotas",
    "quotas",
    multiple=True,
    default=None,
    help="change quotas. Can be used several times: 'quota1=number|empty[,quota2=...]' "
    "(use empty to reset quota to default",
)
@click.pass_context
def project_update(ctx, project, name, quotas):
    """
    Update a project name

    :param ctx:
    :param project: id or name of the project to modify
    :param name:  new name for the project
    :param quotas:  change quotas of the project
    :return:
    """
    logger.debug("")
    project_changes = {}
    if name:
        project_changes["name"] = name
    quotas_dict = _process_project_quotas(quotas)
    if quotas_dict:
        project_changes["quotas"] = quotas_dict

    utils.check_client_version(ctx.obj, ctx.command.name)
    ctx.obj.project.update(project, project_changes)


####################
# User mgmt operations
####################


@click.command(name="user-create", short_help="creates a new user")
@click.argument("username")
@click.option(
    "--password",
    prompt=True,
    hide_input=True,
    confirmation_prompt=True,
    help="user password",
)
@click.option(
    "--projects",
    # prompt="Comma separate list of projects",
    multiple=True,
    callback=lambda ctx, param, value: "".join(value).split(",")
    if all(len(x) == 1 for x in value)
    else value,
    help="list of project ids that the user belongs to",
)
@click.option(
    "--project-role-mappings",
    "project_role_mappings",
    default=None,
    multiple=True,
    help="assign role(s) in a project. Can be used several times: 'project,role1[,role2,...]'",
)
@click.option("--domain-name", "domain_name", default=None, help="assign to a domain")
@click.pass_context
def user_create(ctx, username, password, projects, project_role_mappings, domain_name):
    """Creates a new user

    \b
    USERNAME: name of the user
    PASSWORD: password of the user
    PROJECTS: projects assigned to user (internal only)
    PROJECT_ROLE_MAPPING: roles in projects assigned to user (keystone)
    DOMAIN_NAME: optional domain name for the user when keystone authentication is used
    """
    logger.debug("")
    user = {}
    user["username"] = username
    user["password"] = password
    user["projects"] = projects
    user["project_role_mappings"] = project_role_mappings
    if domain_name:
        user["domain_name"] = domain_name

    utils.check_client_version(ctx.obj, ctx.command.name)
    ctx.obj.user.create(username, user)


@click.command(name="user-update", short_help="updates user information")
@click.argument("username")
@click.option(
    "--password",
    # prompt=True,
    # hide_input=True,
    # confirmation_prompt=True,
    help="user password",
)
@click.option("--set-username", "set_username", default=None, help="change username")
@click.option(
    "--set-project",
    "set_project",
    default=None,
    multiple=True,
    help="create/replace the roles for this project: 'project,role1[,role2,...]'",
)
@click.option(
    "--remove-project",
    "remove_project",
    default=None,
    multiple=True,
    help="removes project from user: 'project'",
)
@click.option(
    "--add-project-role",
    "add_project_role",
    default=None,
    multiple=True,
    help="assign role(s) in a project. Can be used several times: 'project,role1[,role2,...]'",
)
@click.option(
    "--remove-project-role",
    "remove_project_role",
    default=None,
    multiple=True,
    help="remove role(s) in a project. Can be used several times: 'project,role1[,role2,...]'",
)
@click.option("--change_password", "change_password", help="user's current password")
@click.option(
    "--new_password",
    "new_password",
    help="user's new password to update in expiry condition",
)
@click.pass_context
def user_update(
    ctx,
    username,
    password,
    set_username,
    set_project,
    remove_project,
    add_project_role,
    remove_project_role,
    change_password,
    new_password,
):
    """Update a user information

    \b
    USERNAME: name of the user
    PASSWORD: new password
    SET_USERNAME: new username
    SET_PROJECT: creating mappings for project/role(s)
    REMOVE_PROJECT: deleting mappings for project/role(s)
    ADD_PROJECT_ROLE: adding mappings for project/role(s)
    REMOVE_PROJECT_ROLE: removing mappings for project/role(s)
    CHANGE_PASSWORD: user's current password to change
    NEW_PASSWORD: user's new password to update in expiry condition
    """
    logger.debug("")
    user = {}
    user["password"] = password
    user["username"] = set_username
    user["set-project"] = set_project
    user["remove-project"] = remove_project
    user["add-project-role"] = add_project_role
    user["remove-project-role"] = remove_project_role
    user["change_password"] = change_password
    user["new_password"] = new_password

    utils.check_client_version(ctx.obj, ctx.command.name)
    ctx.obj.user.update(username, user)
    if not user.get("change_password"):
        ctx.obj.user.update(username, user)
    else:
        ctx.obj.user.update(username, user, pwd_change=True)


@click.command(name="user-delete", short_help="deletes a user")
@click.argument("name")
# @click.option('--force', is_flag=True, help='forces the deletion bypassing pre-conditions')
@click.pass_context
def user_delete(ctx, name):
    """deletes a user

    \b
    NAME: name or ID of the user to be deleted
    """
    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    ctx.obj.user.delete(name)


@click.command(name="user-list", short_help="list all users")
@click.option(
    "--filter",
    default=None,
    multiple=True,
    help="restricts the list to the users matching the filter",
)
@click.pass_context
def user_list(ctx, filter):
    """list all users"""
    utils.check_client_version(ctx.obj, ctx.command.name)
    if filter:
        filter = "&".join(filter)
    resp = ctx.obj.user.list(filter)
    table = PrettyTable(["name", "id"])
    for user in resp:
        table.add_row([user["username"], user["_id"]])
    table.align = "l"
    print(table)


@click.command(name="user-show", short_help="shows the details of a user")
@click.argument("name")
@click.pass_context
def user_show(ctx, name):
    """shows the details of a user

    NAME: name or ID of the user
    """
    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    resp = ctx.obj.user.get(name)
    if "password" in resp:
        resp["password"] = "********"

    table = PrettyTable(["key", "attribute"])
    for k, v in resp.items():
        table.add_row([k, json.dumps(v, indent=2)])
    table.align = "l"
    print(table)
