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


def nsd_list(ctx, filter, long):
    logger.debug("")
    if filter:
        utils.check_client_version(ctx.obj, "--filter")
        filter = "&".join(filter)
        resp = ctx.obj.nsd.list(filter)
    else:
        resp = ctx.obj.nsd.list()
    # print(yaml.safe_dump(resp))
    fullclassname = ctx.obj.__module__ + "." + ctx.obj.__class__.__name__
    if fullclassname == "osmclient.sol005.client.Client":
        if long:
            table = PrettyTable(
                [
                    "nsd name",
                    "id",
                    "onboarding state",
                    "operational state",
                    "usage state",
                    "date",
                    "last update",
                ]
            )
        else:
            table = PrettyTable(["nsd name", "id"])
        for nsd in resp:
            name = nsd.get("id", "-")
            if long:
                onb_state = nsd["_admin"].get("onboardingState", "-")
                op_state = nsd["_admin"].get("operationalState", "-")
                usage_state = nsd["_admin"].get("usageState", "-")
                date = datetime.fromtimestamp(nsd["_admin"]["created"]).strftime(
                    "%Y-%m-%dT%H:%M:%S"
                )
                last_update = datetime.fromtimestamp(
                    nsd["_admin"]["modified"]
                ).strftime("%Y-%m-%dT%H:%M:%S")
                table.add_row(
                    [
                        name,
                        nsd["_id"],
                        onb_state,
                        op_state,
                        usage_state,
                        date,
                        last_update,
                    ]
                )
            else:
                table.add_row([name, nsd["_id"]])
    else:
        table = PrettyTable(["nsd name", "id"])
        for nsd in resp:
            table.add_row([nsd["name"], nsd["id"]])
    table.align = "l"
    print(table)


@click.command(name="nsd-list", short_help="list all NS packages")
@click.option(
    "--filter",
    default=None,
    multiple=True,
    help="restricts the list to the NSD/NSpkg matching the filter",
)
@click.option("--long", is_flag=True, help="get more details")
@click.pass_context
def nsd_list1(ctx, filter, long):
    """list all NSD/NS pkg in the system"""
    logger.debug("")
    nsd_list(ctx, filter, long)


@click.command(name="nspkg-list", short_help="list all NS packages")
@click.option(
    "--filter",
    default=None,
    multiple=True,
    help="restricts the list to the NSD/NSpkg matching the filter",
)
@click.option("--long", is_flag=True, help="get more details")
@click.pass_context
def nsd_list2(ctx, filter, long):
    """list all NS packages"""
    logger.debug("")
    nsd_list(ctx, filter, long)


def nsd_show(ctx, name, literal):
    logger.debug("")
    resp = ctx.obj.nsd.get(name)
    # resp = ctx.obj.nsd.get_individual(name)

    if literal:
        print(yaml.safe_dump(resp, indent=4, default_flow_style=False))
        return

    table = PrettyTable(["field", "value"])
    for k, v in list(resp.items()):
        table.add_row([k, utils.wrap_text(text=json.dumps(v, indent=2), width=100)])
    table.align = "l"
    print(table)


@click.command(name="nsd-show", short_help="shows the details of a NS package")
@click.option("--literal", is_flag=True, help="print literally, no pretty table")
@click.argument("name")
@click.pass_context
def nsd_show1(ctx, name, literal):
    """shows the content of a NSD

    NAME: name or ID of the NSD/NSpkg
    """
    logger.debug("")
    nsd_show(ctx, name, literal)


@click.command(name="nspkg-show", short_help="shows the details of a NS package")
@click.option("--literal", is_flag=True, help="print literally, no pretty table")
@click.argument("name")
@click.pass_context
def nsd_show2(ctx, name, literal):
    """shows the content of a NSD

    NAME: name or ID of the NSD/NSpkg
    """
    logger.debug("")
    nsd_show(ctx, name, literal)


def nsd_create(ctx, filename, overwrite, skip_charm_build, repo, vendor, version):
    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    if repo:
        filename = ctx.obj.osmrepo.get_pkg("ns", filename, repo, vendor, version)
    ctx.obj.nsd.create(filename, overwrite=overwrite, skip_charm_build=skip_charm_build)


@click.command(name="nsd-create", short_help="creates a new NSD/NSpkg")
@click.argument("filename")
@click.option(
    "--overwrite",
    "overwrite",
    default=None,  # hidden=True,
    help="Deprecated. Use override",
)
@click.option(
    "--override",
    "overwrite",
    default=None,
    help="overrides fields in descriptor, format: "
    '"key1.key2...=value[;key3...=value;...]"',
)
@click.option(
    "--skip-charm-build",
    default=False,
    is_flag=True,
    help="The charm will not be compiled, it is assumed to already exist",
)
@click.option("--repo", default=None, help="[repository]: Repository name")
@click.option("--vendor", default=None, help="[repository]: filter by vendor]")
@click.option(
    "--version",
    default="latest",
    help="[repository]: filter by version. Default: latest",
)
@click.pass_context
def nsd_create1(ctx, filename, overwrite, skip_charm_build, repo, vendor, version):
    """onboards a new NSpkg (alias of nspkg-create) (TO BE DEPRECATED)

    \b
    FILENAME: NF Package tar.gz file, NF Descriptor YAML file or NF Package folder
              If FILENAME is a file (NF Package tar.gz or NF Descriptor YAML), it is onboarded.
              If FILENAME is an NF Package folder, it is built and then onboarded.
    """
    logger.debug("")
    nsd_create(
        ctx,
        filename,
        overwrite=overwrite,
        skip_charm_build=skip_charm_build,
        repo=repo,
        vendor=vendor,
        version=version,
    )


@click.command(name="nspkg-create", short_help="creates a new NSD/NSpkg")
@click.argument("filename")
@click.option(
    "--overwrite",
    "overwrite",
    default=None,  # hidden=True,
    help="Deprecated. Use override",
)
@click.option(
    "--override",
    "overwrite",
    default=None,
    help="overrides fields in descriptor, format: "
    '"key1.key2...=value[;key3...=value;...]"',
)
@click.option(
    "--skip-charm-build",
    default=False,
    is_flag=True,
    help="The charm will not be compiled, it is assumed to already exist",
)
@click.option("--repo", default=None, help="[repository]: Repository name")
@click.option("--vendor", default=None, help="[repository]: filter by vendor]")
@click.option(
    "--version",
    default="latest",
    help="[repository]: filter by version. Default: latest",
)
@click.pass_context
def nsd_create2(ctx, filename, overwrite, skip_charm_build, repo, vendor, version):
    """onboards a new NSpkg
    \b
    FILENAME: NF Package tar.gz file, NF Descriptor YAML file or NF Package folder
              If FILENAME is a file (NF Package tar.gz or NF Descriptor YAML), it is onboarded.
              If FILENAME is an NF Package folder, it is built and then onboarded.
    """
    logger.debug("")
    nsd_create(
        ctx,
        filename,
        overwrite=overwrite,
        skip_charm_build=skip_charm_build,
        repo=repo,
        vendor=vendor,
        version=version,
    )


def nsd_update(ctx, name, content):
    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    ctx.obj.nsd.update(name, content)


@click.command(name="nsd-update", short_help="updates a NSD/NSpkg")
@click.argument("name")
@click.option(
    "--content",
    default=None,
    help="filename with the NSD/NSpkg replacing the current one",
)
@click.pass_context
def nsd_update1(ctx, name, content):
    """updates a NSD/NSpkg

    NAME: name or ID of the NSD/NSpkg
    """
    logger.debug("")
    nsd_update(ctx, name, content)


@click.command(name="nspkg-update", short_help="updates a NSD/NSpkg")
@click.argument("name")
@click.option(
    "--content",
    default=None,
    help="filename with the NSD/NSpkg replacing the current one",
)
@click.pass_context
def nsd_update2(ctx, name, content):
    """updates a NSD/NSpkg

    NAME: name or ID of the NSD/NSpkg
    """
    logger.debug("")
    nsd_update(ctx, name, content)


def nsd_delete(ctx, name, force):
    logger.debug("")
    if not force:
        ctx.obj.nsd.delete(name)
    else:
        utils.check_client_version(ctx.obj, "--force")
        ctx.obj.nsd.delete(name, force)


@click.command(name="nsd-delete", short_help="deletes a NSD/NSpkg")
@click.argument("name")
@click.option(
    "--force", is_flag=True, help="forces the deletion bypassing pre-conditions"
)
@click.pass_context
def nsd_delete1(ctx, name, force):
    """deletes a NSD/NSpkg

    NAME: name or ID of the NSD/NSpkg to be deleted
    """
    logger.debug("")
    nsd_delete(ctx, name, force)


@click.command(name="nspkg-delete", short_help="deletes a NSD/NSpkg")
@click.argument("name")
@click.option(
    "--force", is_flag=True, help="forces the deletion bypassing pre-conditions"
)
@click.pass_context
def nsd_delete2(ctx, name, force):
    """deletes a NSD/NSpkg

    NAME: name or ID of the NSD/NSpkg to be deleted
    """
    logger.debug("")
    nsd_delete(ctx, name, force)
