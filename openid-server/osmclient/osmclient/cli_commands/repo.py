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
from osmclient.common.exceptions import NotFound
from osmclient.cli_commands import utils
from prettytable import PrettyTable
import yaml
import json
import logging

logger = logging.getLogger("osmclient")


@click.command(name="repo-add", short_help="adds a repo to OSM")
@click.argument("name")
@click.argument("uri")
@click.option(
    "--type",
    type=click.Choice(["helm-chart", "juju-bundle", "osm"]),
    default="osm",
    help="type of repo (helm-chart for Helm Charts, juju-bundle for Juju Bundles, osm for OSM Repositories)",
)
@click.option("--description", default=None, help="human readable description")
@click.option(
    "--user", default=None, help="OSM repository: The username of the OSM repository"
)
@click.option(
    "--password",
    default=None,
    help="OSM repository: The password of the OSM repository",
)
@click.pass_context
def repo_add(ctx, **kwargs):
    """adds a repo to OSM

    NAME: name of the repo
    URI: URI of the repo
    """
    kwargs = {k: v for k, v in kwargs.items() if v is not None}
    repo = kwargs
    repo["url"] = repo.pop("uri")
    if repo["type"] in ["helm-chart", "juju-bundle"]:
        ctx.obj.repo.create(repo["name"], repo)
    else:
        ctx.obj.osmrepo.create(repo["name"], repo)


@click.command(name="repo-update", short_help="updates a repo in OSM")
@click.argument("name")
@click.option("--newname", help="New name for the repo")
@click.option("--uri", help="URI of the repo")
@click.option("--description", help="human readable description")
@click.pass_context
def repo_update(ctx, name, newname, uri, description):
    """updates a repo in OSM

    NAME: name of the repo
    """
    utils.check_client_version(ctx.obj, ctx.command.name)
    repo = {}
    if newname:
        repo["name"] = newname
    if uri:
        repo["uri"] = uri
    if description:
        repo["description"] = description
    try:
        ctx.obj.repo.update(name, repo)
    except NotFound:
        ctx.obj.osmrepo.update(name, repo)


@click.command(
    name="repo-index", short_help="Index a repository from a folder with artifacts"
)
@click.option(
    "--origin", default=".", help="origin path where the artifacts are located"
)
@click.option(
    "--destination", default=".", help="destination path where the index is deployed"
)
@click.pass_context
def repo_index(ctx, origin, destination):
    """Index a repository

    NAME: name or ID of the repo to be deleted
    """
    utils.check_client_version(ctx.obj, ctx.command.name)
    ctx.obj.osmrepo.repo_index(origin, destination)


@click.command(name="repo-delete", short_help="deletes a repo")
@click.argument("name")
@click.option(
    "--force", is_flag=True, help="forces the deletion from the DB (not recommended)"
)
@click.pass_context
def repo_delete(ctx, name, force):
    """deletes a repo

    NAME: name or ID of the repo to be deleted
    """
    logger.debug("")
    try:
        ctx.obj.repo.delete(name, force=force)
    except NotFound:
        ctx.obj.osmrepo.delete(name, force=force)


@click.command(name="repo-list")
@click.option(
    "--filter",
    default=None,
    multiple=True,
    help="restricts the list to the repos matching the filter",
)
@click.option("--literal", is_flag=True, help="print literally, no pretty table")
@click.pass_context
def repo_list(ctx, filter, literal):
    """list all repos"""
    # K8s Repositories
    utils.check_client_version(ctx.obj, ctx.command.name)
    if filter:
        filter = "&".join(filter)
    resp = ctx.obj.repo.list(filter)
    resp += ctx.obj.osmrepo.list(filter)
    if literal:
        print(yaml.safe_dump(resp, indent=4, default_flow_style=False))
        return
    table = PrettyTable(["Name", "Id", "Type", "URI", "Description"])
    for repo in resp:
        # cluster['k8s-nets'] = json.dumps(yaml.safe_load(cluster['k8s-nets']))
        table.add_row(
            [
                repo["name"],
                repo["_id"],
                repo["type"],
                repo["url"],
                utils.trunc_text(repo.get("description") or "", 40),
            ]
        )
    table.align = "l"
    print(table)


@click.command(name="repo-show", short_help="shows the details of a repo")
@click.argument("name")
@click.option("--literal", is_flag=True, help="print literally, no pretty table")
@click.pass_context
def repo_show(ctx, name, literal):
    """shows the details of a repo

    NAME: name or ID of the repo
    """
    try:
        resp = ctx.obj.repo.get(name)
    except NotFound:
        resp = ctx.obj.osmrepo.get(name)

    if literal:
        if resp:
            print(yaml.safe_dump(resp, indent=4, default_flow_style=False))
        return
    table = PrettyTable(["key", "attribute"])
    if resp:
        for k, v in list(resp.items()):
            table.add_row([k, json.dumps(v, indent=2)])

    table.align = "l"
    print(table)


########################
# Catalogue commands
########################


def pkg_repo_list(ctx, pkgtype, filter, repo, long):
    resp = ctx.obj.osmrepo.pkg_list(pkgtype, filter, repo)
    if long:
        table = PrettyTable(
            ["nfpkg name", "vendor", "version", "latest", "description", "repository"]
        )
    else:
        table = PrettyTable(["nfpkg name", "repository"])
    for vnfd in resp:
        name = vnfd.get("id", vnfd.get("name", "-"))
        repository = vnfd.get("repository")
        if long:
            vendor = vnfd.get("provider", vnfd.get("vendor"))
            version = vnfd.get("version")
            description = vnfd.get("description")
            latest = vnfd.get("latest")
            table.add_row([name, vendor, version, latest, description, repository])
        else:
            table.add_row([name, repository])
        table.align = "l"
    print(table)


def pkg_repo_show(ctx, pkgtype, name, repo, version, filter, literal):
    logger.debug("")
    if filter:
        filter = "&".join(filter)
    resp = ctx.obj.osmrepo.pkg_get(pkgtype, name, repo, version, filter)

    if literal:
        print(yaml.safe_dump(resp, indent=4, default_flow_style=False))
        return
    pkgtype += "d"
    catalog = pkgtype + "-catalog"
    full_catalog = pkgtype + ":" + catalog
    if resp.get(catalog):
        resp = resp.pop(catalog)[pkgtype][0]
    elif resp.get(full_catalog):
        resp = resp.pop(full_catalog)[pkgtype][0]

    table = PrettyTable(["field", "value"])
    for k, v in list(resp.items()):
        table.add_row([k, utils.wrap_text(text=json.dumps(v, indent=2), width=100)])
    table.align = "l"
    print(table)


@click.command(name="vnfpkg-repo-list", short_help="list all xNF from OSM repositories")
@click.option(
    "--filter",
    default=None,
    multiple=True,
    help="restricts the list to the NFpkg matching the filter",
)
@click.option(
    "--repo", default=None, help="restricts the list to a particular OSM repository"
)
@click.option("--long", is_flag=True, help="get more details")
@click.pass_context
def nfpkg_repo_list1(ctx, filter, repo, long):
    """list xNF packages from OSM repositories"""
    pkgtype = "vnf"
    pkg_repo_list(ctx, pkgtype, filter, repo, long)


@click.command(name="nfpkg-repo-list", short_help="list all xNF from OSM repositories")
@click.option(
    "--filter",
    default=None,
    multiple=True,
    help="restricts the list to the NFpkg matching the filter",
)
@click.option(
    "--repo", default=None, help="restricts the list to a particular OSM repository"
)
@click.option("--long", is_flag=True, help="get more details")
@click.pass_context
def nfpkg_repo_list2(ctx, filter, repo, long):
    """list xNF packages from OSM repositories"""
    pkgtype = "vnf"
    pkg_repo_list(ctx, pkgtype, filter, repo, long)


@click.command(name="nsd-repo-list", short_help="list all NS from OSM repositories")
@click.option(
    "--filter",
    default=None,
    multiple=True,
    help="restricts the list to the NS matching the filter",
)
@click.option(
    "--repo", default=None, help="restricts the list to a particular OSM repository"
)
@click.option("--long", is_flag=True, help="get more details")
@click.pass_context
def nspkg_repo_list(ctx, filter, repo, long):
    """list xNF packages from OSM repositories"""
    pkgtype = "ns"
    pkg_repo_list(ctx, pkgtype, filter, repo, long)


@click.command(name="nspkg-repo-list", short_help="list all NS from OSM repositories")
@click.option(
    "--filter",
    default=None,
    multiple=True,
    help="restricts the list to the NS matching the filter",
)
@click.option(
    "--repo", default=None, help="restricts the list to a particular OSM repository"
)
@click.option("--long", is_flag=True, help="get more details")
@click.pass_context
def nspkg_repo_list2(ctx, filter, repo, long):
    """list xNF packages from OSM repositories"""
    pkgtype = "ns"
    pkg_repo_list(ctx, pkgtype, filter, repo, long)


@click.command(
    name="vnfpkg-repo-show",
    short_help="shows the details of a NF package in an OSM repository",
)
@click.option("--literal", is_flag=True, help="print literally, no pretty table")
@click.option("--repo", required=True, help="Repository name")
@click.argument("name")
@click.option("--filter", default=None, multiple=True, help="filter by fields")
@click.option("--version", default="latest", help="package version")
@click.pass_context
def vnfd_show1(ctx, name, repo, version, literal=None, filter=None):
    """shows the content of a VNFD in a repository

    NAME: name or ID of the VNFD/VNFpkg
    """
    pkgtype = "vnf"
    pkg_repo_show(ctx, pkgtype, name, repo, version, filter, literal)


@click.command(
    name="nsd-repo-show",
    short_help="shows the details of a NS package in an OSM repository",
)
@click.option("--literal", is_flag=True, help="print literally, no pretty table")
@click.option("--repo", required=True, help="Repository name")
@click.argument("name")
@click.option("--filter", default=None, multiple=True, help="filter by fields")
@click.option("--version", default="latest", help="package version")
@click.pass_context
def nsd_repo_show(ctx, name, repo, version, literal=None, filter=None):
    """shows the content of a VNFD in a repository

    NAME: name or ID of the VNFD/VNFpkg
    """
    pkgtype = "ns"
    pkg_repo_show(ctx, pkgtype, name, repo, version, filter, literal)


@click.command(
    name="nspkg-repo-show",
    short_help="shows the details of a NS package in an OSM repository",
)
@click.option("--literal", is_flag=True, help="print literally, no pretty table")
@click.option("--repo", required=True, help="Repository name")
@click.argument("name")
@click.option("--filter", default=None, multiple=True, help="filter by fields")
@click.option("--version", default="latest", help="package version")
@click.pass_context
def nsd_repo_show2(ctx, name, repo, version, literal=None, filter=None):
    """shows the content of a VNFD in a repository

    NAME: name or ID of the VNFD/VNFpkg
    """
    pkgtype = "ns"
    pkg_repo_show(ctx, pkgtype, name, repo, version, filter, literal)


@click.command(
    name="nfpkg-repo-show",
    short_help="shows the details of a NF package in an OSM repository",
)
@click.option("--literal", is_flag=True, help="print literally, no pretty table")
@click.option("--repo", required=True, help="Repository name")
@click.argument("name")
@click.option("--filter", default=None, multiple=True, help="filter by fields")
@click.option("--version", default="latest", help="package version")
@click.pass_context
def vnfd_show2(ctx, name, repo, version, literal=None, filter=None):
    """shows the content of a VNFD in a repository

    NAME: name or ID of the VNFD/VNFpkg
    """
    pkgtype = "vnf"
    pkg_repo_show(ctx, pkgtype, name, repo, version, filter, literal)
