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

import textwrap
import logging
import yaml
from osmclient.common.exceptions import ClientException

logger = logging.getLogger("osmclient")


def wrap_text(text, width):
    wrapper = textwrap.TextWrapper(width=width)
    lines = text.splitlines()
    return "\n".join(map(wrapper.fill, lines))


def trunc_text(text, length):
    if len(text) > length:
        return text[: (length - 3)] + "..."
    else:
        return text


def check_client_version(obj, what, version="sol005"):
    """
    Checks the version of the client object and raises error if it not the expected.

    :param obj: the client object
    :what: the function or command under evaluation (used when an error is raised)
    :return: -
    :raises ClientError: if the specified version does not match the client version
    """
    logger.debug("")
    fullclassname = obj.__module__ + "." + obj.__class__.__name__
    message = 'The following commands or options are only supported with the option "--sol005": {}'.format(
        what
    )
    if version == "v1":
        message = 'The following commands or options are not supported when using option "--sol005": {}'.format(
            what
        )
    if fullclassname != "osmclient.{}.client.Client".format(version):
        raise ClientException(message)
    return


def get_project(project_list, item):
    # project_list = ctx.obj.project.list()
    item_project_list = item.get("_admin", {}).get("projects_read")
    project_id = "None"
    project_name = "None"
    if item_project_list:
        for p1 in item_project_list:
            project_id = p1
            for p2 in project_list:
                if p2["_id"] == project_id:
                    project_name = p2["name"]
                    return project_id, project_name
    return project_id, project_name


def get_vim_name(vim_list, vim_id):
    vim_name = "-"
    for v in vim_list:
        if v["uuid"] == vim_id:
            vim_name = v["name"]
            break
    return vim_name


def create_config(config_file, json_string):
    """
    Combines a YAML or JSON file with a JSON string into a Python3 structure
    It loads the YAML or JSON file 'cfile' into a first dictionary.
    It loads the JSON string into a second dictionary.
    Then it updates the first dictionary with the info in the second dictionary.
    If the field is present in both cfile and cdict, the field in cdict prevails.
    If both cfile and cdict are None, it returns an empty dict (i.e. {})
    """
    config = {}
    if config_file:
        with open(config_file, "r") as cf:
            config = yaml.safe_load(cf.read())
    if json_string:
        cdict = yaml.safe_load(json_string)
        for k, v in cdict.items():
            config[k] = v
    return config
