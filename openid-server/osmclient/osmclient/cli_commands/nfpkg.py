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


def vnfd_list(ctx, nf_type, filter, long):
    logger.debug("")
    if nf_type:
        utils.check_client_version(ctx.obj, "--nf_type")
    elif filter:
        utils.check_client_version(ctx.obj, "--filter")
    if filter:
        filter = "&".join(filter)
    if nf_type:
        if nf_type == "vnf":
            nf_filter = "_admin.type=vnfd"
        elif nf_type == "pnf":
            nf_filter = "_admin.type=pnfd"
        elif nf_type == "hnf":
            nf_filter = "_admin.type=hnfd"
        else:
            raise ClientException(
                'wrong value for "--nf_type" option, allowed values: vnf, pnf, hnf'
            )
        if filter:
            filter = "{}&{}".format(nf_filter, filter)
        else:
            filter = nf_filter
    if filter:
        resp = ctx.obj.vnfd.list(filter)
    else:
        resp = ctx.obj.vnfd.list()
    # print(yaml.safe_dump(resp))
    fullclassname = ctx.obj.__module__ + "." + ctx.obj.__class__.__name__
    if fullclassname == "osmclient.sol005.client.Client":
        if long:
            table = PrettyTable(
                [
                    "nfpkg name",
                    "id",
                    "desc type",
                    "vendor",
                    "version",
                    "onboarding state",
                    "operational state",
                    "usage state",
                    "date",
                    "last update",
                ]
            )
        else:
            table = PrettyTable(["nfpkg name", "id", "desc type"])
        for vnfd in resp:
            name = vnfd.get("id", vnfd.get("name", "-"))
            descriptor_type = "sol006" if "product-name" in vnfd else "rel8"
            if long:
                onb_state = vnfd["_admin"].get("onboardingState", "-")
                op_state = vnfd["_admin"].get("operationalState", "-")
                vendor = vnfd.get("provider", vnfd.get("vendor"))
                version = vnfd.get("version")
                usage_state = vnfd["_admin"].get("usageState", "-")
                date = datetime.fromtimestamp(vnfd["_admin"]["created"]).strftime(
                    "%Y-%m-%dT%H:%M:%S"
                )
                last_update = datetime.fromtimestamp(
                    vnfd["_admin"]["modified"]
                ).strftime("%Y-%m-%dT%H:%M:%S")
                table.add_row(
                    [
                        name,
                        vnfd["_id"],
                        descriptor_type,
                        vendor,
                        version,
                        onb_state,
                        op_state,
                        usage_state,
                        date,
                        last_update,
                    ]
                )
            else:
                table.add_row([name, vnfd["_id"], descriptor_type])
    else:
        table = PrettyTable(["nfpkg name", "id"])
        for vnfd in resp:
            table.add_row([vnfd["name"], vnfd["id"]])
    table.align = "l"
    print(table)


@click.command(name="vnfd-list", short_help="list all xNF packages (VNF, HNF, PNF)")
@click.option("--nf_type", help="type of NF (vnf, pnf, hnf)")
@click.option(
    "--filter",
    default=None,
    multiple=True,
    help="restricts the list to the NF pkg matching the filter",
)
@click.option("--long", is_flag=True, help="get more details")
@click.pass_context
def vnfd_list1(ctx, nf_type, filter, long):
    """list all xNF packages (VNF, HNF, PNF)"""
    logger.debug("")
    vnfd_list(ctx, nf_type, filter, long)


@click.command(name="vnfpkg-list", short_help="list all xNF packages (VNF, HNF, PNF)")
@click.option("--nf_type", help="type of NF (vnf, pnf, hnf)")
@click.option(
    "--filter",
    default=None,
    multiple=True,
    help="restricts the list to the NFpkg matching the filter",
)
@click.option("--long", is_flag=True, help="get more details")
@click.pass_context
def vnfd_list2(ctx, nf_type, filter, long):
    """list all xNF packages (VNF, HNF, PNF)"""
    logger.debug("")
    vnfd_list(ctx, nf_type, filter, long)


@click.command(name="nfpkg-list", short_help="list all xNF packages (VNF, HNF, PNF)")
@click.option("--nf_type", help="type of NF (vnf, pnf, hnf)")
@click.option(
    "--filter",
    default=None,
    multiple=True,
    help="restricts the list to the NFpkg matching the filter",
)
@click.option("--long", is_flag=True, help="get more details")
@click.pass_context
def nfpkg_list(ctx, nf_type, filter, long):
    """list all xNF packages (VNF, HNF, PNF)"""
    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    vnfd_list(ctx, nf_type, filter, long)


def vnfd_show(ctx, name, literal):
    logger.debug("")
    resp = ctx.obj.vnfd.get(name)
    # resp = ctx.obj.vnfd.get_individual(name)

    if literal:
        print(yaml.safe_dump(resp, indent=4, default_flow_style=False))
        return

    table = PrettyTable(["field", "value"])
    for k, v in list(resp.items()):
        table.add_row([k, utils.wrap_text(text=json.dumps(v, indent=2), width=100)])
    table.align = "l"
    print(table)


@click.command(name="vnfd-show", short_help="shows the details of a NF package")
@click.option("--literal", is_flag=True, help="print literally, no pretty table")
@click.argument("name")
@click.pass_context
def vnfd_show1(ctx, name, literal):
    """shows the content of a VNFD

    NAME: name or ID of the VNFD/VNFpkg
    """
    logger.debug("")
    vnfd_show(ctx, name, literal)


@click.command(name="vnfpkg-show", short_help="shows the details of a NF package")
@click.option("--literal", is_flag=True, help="print literally, no pretty table")
@click.argument("name")
@click.pass_context
def vnfd_show2(ctx, name, literal):
    """shows the content of a VNFD

    NAME: name or ID of the VNFD/VNFpkg
    """
    logger.debug("")
    vnfd_show(ctx, name, literal)


@click.command(name="nfpkg-show", short_help="shows the details of a NF package")
@click.option("--literal", is_flag=True, help="print literally, no pretty table")
@click.argument("name")
@click.pass_context
def nfpkg_show(ctx, name, literal):
    """shows the content of a NF Descriptor

    NAME: name or ID of the NFpkg
    """
    logger.debug("")
    vnfd_show(ctx, name, literal)


def vnfd_create(
    ctx,
    filename,
    overwrite,
    skip_charm_build,
    override_epa,
    override_nonepa,
    override_paravirt,
    repo,
    vendor,
    version,
):
    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    if repo:
        filename = ctx.obj.osmrepo.get_pkg("vnf", filename, repo, vendor, version)
    ctx.obj.vnfd.create(
        filename,
        overwrite=overwrite,
        skip_charm_build=skip_charm_build,
        override_epa=override_epa,
        override_nonepa=override_nonepa,
        override_paravirt=override_paravirt,
    )


@click.command(name="vnfd-create", short_help="creates a new VNFD/VNFpkg")
@click.argument("filename")
@click.option(
    "--overwrite", "overwrite", default=None, help="overwrite deprecated, use override"
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
@click.option(
    "--override-epa",
    required=False,
    default=False,
    is_flag=True,
    help="adds guest-epa parameters to all VDU",
)
@click.option(
    "--override-nonepa",
    required=False,
    default=False,
    is_flag=True,
    help="removes all guest-epa parameters from all VDU",
)
@click.option(
    "--override-paravirt",
    required=False,
    default=False,
    is_flag=True,
    help="overrides all VDU interfaces to PARAVIRT",
)
@click.option("--repo", default=None, help="[repository]: Repository name")
@click.option("--vendor", default=None, help="[repository]: filter by vendor]")
@click.option(
    "--version",
    default="latest",
    help="[repository]: filter by version. Default: latest",
)
@click.pass_context
def vnfd_create1(
    ctx,
    filename,
    overwrite,
    skip_charm_build,
    override_epa,
    override_nonepa,
    override_paravirt,
    repo,
    vendor,
    version,
):
    """creates a new VNFD/VNFpkg
    \b
    FILENAME: NF Package tar.gz file, NF Descriptor YAML file or NF Package folder
              If FILENAME is a file (NF Package tar.gz or NF Descriptor YAML), it is onboarded.
              If FILENAME is an NF Package folder, it is built and then onboarded.
    """
    logger.debug("")
    vnfd_create(
        ctx,
        filename,
        overwrite=overwrite,
        skip_charm_build=skip_charm_build,
        override_epa=override_epa,
        override_nonepa=override_nonepa,
        override_paravirt=override_paravirt,
        repo=repo,
        vendor=vendor,
        version=version,
    )


@click.command(name="vnfpkg-create", short_help="creates a new VNFD/VNFpkg")
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
@click.option(
    "--override-epa",
    required=False,
    default=False,
    is_flag=True,
    help="adds guest-epa parameters to all VDU",
)
@click.option(
    "--override-nonepa",
    required=False,
    default=False,
    is_flag=True,
    help="removes all guest-epa parameters from all VDU",
)
@click.option(
    "--override-paravirt",
    required=False,
    default=False,
    is_flag=True,
    help="overrides all VDU interfaces to PARAVIRT",
)
@click.option("--repo", default=None, help="[repository]: Repository name")
@click.option("--vendor", default=None, help="[repository]: filter by vendor]")
@click.option(
    "--version",
    default="latest",
    help="[repository]: filter by version. Default: latest",
)
@click.pass_context
def vnfd_create2(
    ctx,
    filename,
    overwrite,
    skip_charm_build,
    override_epa,
    override_nonepa,
    override_paravirt,
    repo,
    vendor,
    version,
):
    """creates a new VNFD/VNFpkg
    \b
    FILENAME: NF Package tar.gz file, NF Descriptor YAML file or NF Package folder
              If FILENAME is a file (NF Package tar.gz or NF Descriptor YAML), it is onboarded.
              If FILENAME is an NF Package folder, it is built and then onboarded.
    """
    logger.debug("")
    vnfd_create(
        ctx,
        filename,
        overwrite=overwrite,
        skip_charm_build=skip_charm_build,
        override_epa=override_epa,
        override_nonepa=override_nonepa,
        override_paravirt=override_paravirt,
        repo=repo,
        vendor=vendor,
        version=version,
    )


@click.command(name="nfpkg-create", short_help="creates a new NFpkg")
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
@click.option(
    "--override-epa",
    required=False,
    default=False,
    is_flag=True,
    help="adds guest-epa parameters to all VDU",
)
@click.option(
    "--override-nonepa",
    required=False,
    default=False,
    is_flag=True,
    help="removes all guest-epa parameters from all VDU",
)
@click.option(
    "--override-paravirt",
    required=False,
    default=False,
    is_flag=True,
    help="overrides all VDU interfaces to PARAVIRT",
)
@click.option("--repo", default=None, help="[repository]: Repository name")
@click.option("--vendor", default=None, help="[repository]: filter by vendor]")
@click.option(
    "--version",
    default="latest",
    help="[repository]: filter by version. Default: latest",
)
@click.pass_context
def nfpkg_create(
    ctx,
    filename,
    overwrite,
    skip_charm_build,
    override_epa,
    override_nonepa,
    override_paravirt,
    repo,
    vendor,
    version,
):
    """creates a new NFpkg

    \b
    FILENAME: NF Package tar.gz file, NF Descriptor YAML file or NF Package folder
              If FILENAME is a file (NF Package tar.gz or NF Descriptor YAML), it is onboarded.
              If FILENAME is an NF Package folder, it is built and then onboarded.
    """
    logger.debug("")
    vnfd_create(
        ctx,
        filename,
        overwrite=overwrite,
        skip_charm_build=skip_charm_build,
        override_epa=override_epa,
        override_nonepa=override_nonepa,
        override_paravirt=override_paravirt,
        repo=repo,
        vendor=vendor,
        version=version,
    )


def vnfd_update(ctx, name, content):
    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    ctx.obj.vnfd.update(name, content)


@click.command(name="vnfd-update", short_help="updates a new VNFD/VNFpkg")
@click.argument("name")
@click.option(
    "--content",
    default=None,
    help="filename with the VNFD/VNFpkg replacing the current one",
)
@click.pass_context
def vnfd_update1(ctx, name, content):
    """updates a VNFD/VNFpkg

    NAME: name or ID of the VNFD/VNFpkg
    """
    logger.debug("")
    vnfd_update(ctx, name, content)


@click.command(name="vnfpkg-update", short_help="updates a VNFD/VNFpkg")
@click.argument("name")
@click.option(
    "--content",
    default=None,
    help="filename with the VNFD/VNFpkg replacing the current one",
)
@click.pass_context
def vnfd_update2(ctx, name, content):
    """updates a VNFD/VNFpkg

    NAME: VNFD yaml file or VNFpkg tar.gz file
    """
    logger.debug("")
    vnfd_update(ctx, name, content)


@click.command(name="nfpkg-update", short_help="updates a NFpkg")
@click.argument("name")
@click.option(
    "--content", default=None, help="filename with the NFpkg replacing the current one"
)
@click.pass_context
def nfpkg_update(ctx, name, content):
    """updates a NFpkg

    NAME: NF Descriptor yaml file or NFpkg tar.gz file
    """
    logger.debug("")
    vnfd_update(ctx, name, content)


def vnfd_delete(ctx, name, force):
    logger.debug("")
    if not force:
        ctx.obj.vnfd.delete(name)
    else:
        utils.check_client_version(ctx.obj, "--force")
        ctx.obj.vnfd.delete(name, force)


@click.command(name="vnfd-delete", short_help="deletes a VNFD/VNFpkg")
@click.argument("name")
@click.option(
    "--force", is_flag=True, help="forces the deletion bypassing pre-conditions"
)
@click.pass_context
def vnfd_delete1(ctx, name, force):
    """deletes a VNFD/VNFpkg

    NAME: name or ID of the VNFD/VNFpkg to be deleted
    """
    logger.debug("")
    vnfd_delete(ctx, name, force)


@click.command(name="vnfpkg-delete", short_help="deletes a VNFD/VNFpkg")
@click.argument("name")
@click.option(
    "--force", is_flag=True, help="forces the deletion bypassing pre-conditions"
)
@click.pass_context
def vnfd_delete2(ctx, name, force):
    """deletes a VNFD/VNFpkg

    NAME: name or ID of the VNFD/VNFpkg to be deleted
    """
    logger.debug("")
    vnfd_delete(ctx, name, force)


@click.command(name="nfpkg-delete", short_help="deletes a NFpkg")
@click.argument("name")
@click.option(
    "--force", is_flag=True, help="forces the deletion bypassing pre-conditions"
)
@click.pass_context
def nfpkg_delete(ctx, name, force):
    """deletes a NFpkg

    NAME: name or ID of the NFpkg to be deleted
    """
    logger.debug("")
    vnfd_delete(ctx, name, force)
