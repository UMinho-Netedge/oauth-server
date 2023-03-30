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
from osmclient.common.utils import validate_uuid4
from osmclient.cli_commands import utils
import yaml
import logging

logger = logging.getLogger("osmclient")


@click.command(
    name="ns-action", short_help="executes an action/primitive over a NS instance"
)
@click.argument("ns_name")
@click.option(
    "--vnf_name",
    default=None,
    help="member-vnf-index if the target is a vnf instead of a ns)",
)
@click.option("--kdu_name", default=None, help="kdu-name if the target is a kdu)")
@click.option("--vdu_id", default=None, help="vdu-id if the target is a vdu")
@click.option(
    "--vdu_count", default=None, type=int, help="number of vdu instance of this vdu_id"
)
@click.option("--action_name", prompt=True, help="action name")
@click.option("--params", default=None, help="action params in YAML/JSON inline string")
@click.option("--params_file", default=None, help="YAML/JSON file with action params")
@click.option(
    "--timeout", required=False, default=None, type=int, help="timeout in seconds"
)
@click.option(
    "--wait",
    required=False,
    default=False,
    is_flag=True,
    help="do not return the control immediately, but keep it until the operation is completed, or timeout",
)
@click.pass_context
def ns_action(
    ctx,
    ns_name,
    vnf_name,
    kdu_name,
    vdu_id,
    vdu_count,
    action_name,
    params,
    params_file,
    timeout,
    wait,
):
    """executes an action/primitive over a NS instance

    NS_NAME: name or ID of the NS instance
    """
    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    op_data = {}
    if vnf_name:
        op_data["member_vnf_index"] = vnf_name
    if kdu_name:
        op_data["kdu_name"] = kdu_name
    if vdu_id:
        op_data["vdu_id"] = vdu_id
    if vdu_count is not None:
        op_data["vdu_count_index"] = vdu_count
    if timeout:
        op_data["timeout_ns_action"] = timeout
    op_data["primitive"] = action_name
    if params_file:
        with open(params_file, "r") as pf:
            params = pf.read()
    if params:
        op_data["primitive_params"] = yaml.safe_load(params)
    else:
        op_data["primitive_params"] = {}
    print(ctx.obj.ns.exec_op(ns_name, op_name="action", op_data=op_data, wait=wait))


@click.command(
    name="vnf-scale", short_help="executes a VNF scale (adding/removing VDUs)"
)
@click.argument("ns_name")
@click.argument("vnf_name")
@click.option(
    "--scaling-group", prompt=True, help="scaling-group-descriptor name to use"
)
@click.option(
    "--scale-in", default=False, is_flag=True, help="performs a scale in operation"
)
@click.option(
    "--scale-out",
    default=False,
    is_flag=True,
    help="performs a scale out operation (by default)",
)
@click.option(
    "--timeout", required=False, default=None, type=int, help="timeout in seconds"
)
@click.option(
    "--wait",
    required=False,
    default=False,
    is_flag=True,
    help="do not return the control immediately, but keep it until the operation is completed, or timeout",
)
@click.pass_context
def vnf_scale(
    ctx, ns_name, vnf_name, scaling_group, scale_in, scale_out, timeout, wait
):
    """
    Executes a VNF scale (adding/removing VDUs)

    \b
    NS_NAME: name or ID of the NS instance.
    VNF_NAME: member-vnf-index in the NS to be scaled.
    """
    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    if not scale_in and not scale_out:
        scale_out = True
    ctx.obj.ns.scale_vnf(
        ns_name, vnf_name, scaling_group, scale_in, scale_out, wait, timeout
    )


@click.command(name="ns-update", short_help="executes an update of a Network Service.")
@click.argument("ns_name")
@click.option(
    "--updatetype", required=True, type=str, help="available types: CHANGE_VNFPKG"
)
@click.option(
    "--config",
    required=True,
    type=str,
    help="extra information for update operation as YAML/JSON inline string as --config"
    " '{changeVnfPackageData:[{vnfInstanceId: xxx, vnfdId: yyy}]}'",
)
@click.option(
    "--timeout", required=False, default=None, type=int, help="timeout in seconds"
)
@click.option(
    "--wait",
    required=False,
    default=False,
    is_flag=True,
    help="do not return the control immediately, but keep it until the operation is completed, or timeout",
)
@click.pass_context
def ns_update(ctx, ns_name, updatetype, config, timeout, wait):
    """Executes an update of a Network Service.

    The update will check new revisions of the Network Functions that are part of the
    Network Service, and it will update them if needed.
    Sample update command: osm ns-update  ns_instance_id --updatetype CHANGE_VNFPKG
    --config '{changeVnfPackageData: [{vnfInstanceId: id_x,vnfdId: id_y}]}' --timeout 300 --wait

    NS_NAME: Network service instance name or ID.

    """
    op_data = {
        "timeout": timeout,
        "updateType": updatetype,
    }
    if config:
        op_data["config"] = yaml.safe_load(config)

    utils.check_client_version(ctx.obj, ctx.command.name)
    ctx.obj.ns.update(ns_name, op_data, wait=wait)


def iterator_split(iterator, separators):
    """
    Splits a tuple or list into several lists whenever a separator is found
    For instance, the following tuple will be separated with the separator "--vnf" as follows.
    From:
        ("--vnf", "A", "--cause", "cause_A", "--vdu", "vdu_A1", "--vnf", "B", "--cause", "cause_B", ...
        "--vdu", "vdu_B1", "--count_index", "1", "--run-day1", "--vdu", "vdu_B1", "--count_index", "2")
    To:
        [
            ("--vnf", "A", "--cause", "cause_A", "--vdu", "vdu_A1"),
            ("--vnf", "B", "--cause", "cause_B", "--vdu", "vdu_B1", "--count_index", "1", "--run-day1", ...
             "--vdu", "vdu_B1", "--count_index", "2")
        ]

    Returns as many lists as separators are found
    """
    logger.debug("")
    if iterator[0] not in separators:
        raise ClientException(f"Expected one of {separators}. Received: {iterator[0]}.")
    list_of_lists = []
    first = 0
    for i in range(len(iterator)):
        if iterator[i] in separators:
            if i == first:
                continue
            if i - first < 2:
                raise ClientException(
                    f"Expected at least one argument after separator (possible separators: {separators})."
                )
            list_of_lists.append(list(iterator[first:i]))
            first = i
    if (len(iterator) - first) < 2:
        raise ClientException(
            f"Expected at least one argument after separator (possible separators: {separators})."
        )
    else:
        list_of_lists.append(list(iterator[first : len(iterator)]))
    # logger.debug(f"List of lists: {list_of_lists}")
    return list_of_lists


def process_common_heal_params(heal_vnf_dict, args):
    logger.debug("")
    current_item = "vnf"
    i = 0
    while i < len(args):
        if args[i] == "--cause":
            if (i + 1 >= len(args)) or args[i + 1].startswith("--"):
                raise ClientException("No cause was provided after --cause")
            heal_vnf_dict["cause"] = args[i + 1]
            i = i + 2
            continue
        if args[i] == "--run-day1":
            if current_item == "vnf":
                if "additionalParams" not in heal_vnf_dict:
                    heal_vnf_dict["additionalParams"] = {}
                heal_vnf_dict["additionalParams"]["run-day1"] = True
            else:
                # if current_item == "vdu"
                heal_vnf_dict["additionalParams"]["vdu"][-1]["run-day1"] = True
            i = i + 1
            continue
        if args[i] == "--vdu":
            if "additionalParams" not in heal_vnf_dict:
                heal_vnf_dict["additionalParams"] = {}
                heal_vnf_dict["additionalParams"]["vdu"] = []
            if (i + 1 >= len(args)) or args[i + 1].startswith("--"):
                raise ClientException("No VDU ID was provided after --vdu")
            heal_vnf_dict["additionalParams"]["vdu"].append({"vdu-id": args[i + 1]})
            current_item = "vdu"
            i = i + 2
            continue
        if args[i] == "--count-index":
            if current_item == "vnf":
                raise ClientException(
                    "Option --count-index only applies to VDU, not to VNF"
                )
            if (i + 1 >= len(args)) or args[i + 1].startswith("--"):
                raise ClientException("No count index was provided after --count-index")
            heal_vnf_dict["additionalParams"]["vdu"][-1]["count-index"] = int(
                args[i + 1]
            )
            i = i + 2
            continue
        i = i + 1
    return


def process_ns_heal_params(ctx, param, value):
    """
    Processes the params in the command ns-heal
    Click does not allow advanced patterns for positional options like this:
    --vnf volumes_vnf --cause "Heal several_volumes-VM of several_volumes_vnf"
                      --vdu several_volumes-VM
    --vnf charm_vnf --cause "Heal two VMs of native_manual_scale_charm_vnf"
                    --vdu mgmtVM --count-index 1 --run-day1
                    --vdu mgmtVM --count-index 2

    It returns the dictionary with all the params stored in ctx.params["heal_params"]
    """
    logger.debug("")
    # logger.debug(f"Args: {value}")
    if param.name != "args":
        raise ClientException(f"Unexpected param: {param.name}")
    # Split the tuple "value" by "--vnf"
    vnfs = iterator_split(value, ["--vnf"])
    logger.debug(f"VNFs: {vnfs}")
    heal_dict = {}
    heal_dict["healVnfData"] = []
    for vnf in vnfs:
        # logger.debug(f"VNF: {vnf}")
        heal_vnf = {}
        if vnf[1].startswith("--"):
            raise ClientException("Expected a VNF_ID after --vnf")
        heal_vnf["vnfInstanceId"] = vnf[1]
        process_common_heal_params(heal_vnf, vnf[2:])
        heal_dict["healVnfData"].append(heal_vnf)
    ctx.params["heal_params"] = heal_dict
    return


@click.command(
    name="ns-heal",
    short_help="heals (recreates) VNFs or VDUs of a NS instance",
    context_settings=dict(
        ignore_unknown_options=True,
    ),
)
@click.argument("ns_name")
@click.argument(
    "args",
    nargs=-1,
    type=click.UNPROCESSED,
    callback=process_ns_heal_params,
)
@click.option("--timeout", type=int, default=None, help="timeout in seconds")
@click.option(
    "--wait",
    default=False,
    is_flag=True,
    help="do not return the control immediately, but keep it until the operation is completed, or timeout",
)
@click.pass_context
def ns_heal(ctx, ns_name, args, heal_params, timeout, wait):
    """heals (recreates) VNFs or VDUs of a NS instance

    NS_NAME: name or ID of the NS instance

    \b
    Options:
      --vnf TEXT             VNF instance ID or VNF id in the NS [required]
      --cause TEXT           human readable cause of the healing
      --run-day1             indicates whether or not to run day1 primitives for the VNF/VDU
      --vdu TEXT             vdu-id
      --count-index INTEGER  count-index

    \b
    Example:
    osm ns-heal NS_NAME|NS_ID --vnf volumes_vnf --cause "Heal several_volumes-VM of several_volumes_vnf"
                                                --vdu several_volumes-VM
                              --vnf charm_vnf --cause "Heal two VMs of native_manual_scale_charm_vnf"
                                              --vdu mgmtVM --count-index 1 --run-day1
                                              --vdu mgmtVM --count-index 2
    """
    logger.debug("")
    heal_dict = ctx.params["heal_params"]
    logger.debug(f"Heal dict:\n{yaml.safe_dump(heal_dict)}")
    # replace VNF id in the NS by the VNF instance ID
    for vnf in heal_dict["healVnfData"]:
        vnf_id = vnf["vnfInstanceId"]
        if not validate_uuid4(vnf_id):
            vnf_filter = f"member-vnf-index-ref={vnf_id}"
            vnf_list = ctx.obj.vnf.list(ns=ns_name, filter=vnf_filter)
            if len(vnf_list) == 0:
                raise ClientException(
                    f"No VNF found in NS {ns_name} with filter {vnf_filter}"
                )
            elif len(vnf_list) == 1:
                vnf["vnfInstanceId"] = vnf_list[0]["_id"]
            else:
                raise ClientException(
                    f"More than 1 VNF found in NS {ns_name} with filter {vnf_filter}"
                )
    logger.debug(f"Heal dict:\n{yaml.safe_dump(heal_dict)}")
    utils.check_client_version(ctx.obj, ctx.command.name)
    ctx.obj.ns.heal(ns_name, heal_dict, wait, timeout)


def process_vnf_heal_params(ctx, param, value):
    """
    Processes the params in the command vnf-heal
    Click does not allow advanced patterns for positional options like this:
    --vdu mgmtVM --count-index 1 --run-day1 --vdu mgmtVM --count-index 2

    It returns the dictionary with all the params stored in ctx.params["heal_params"]
    """
    logger.debug("")
    # logger.debug(f"Args: {value}")
    if param.name != "args":
        raise ClientException(f"Unexpected param: {param.name}")
    # Split the tuple "value" by "--vnf"
    vnf = value
    heal_dict = {}
    heal_dict["healVnfData"] = []
    logger.debug(f"VNF: {vnf}")
    heal_vnf = {"vnfInstanceId": "id_to_be_substituted"}
    process_common_heal_params(heal_vnf, vnf)
    heal_dict["healVnfData"].append(heal_vnf)
    ctx.params["heal_params"] = heal_dict
    return


@click.command(
    name="vnf-heal",
    short_help="heals (recreates) a VNF instance or the VDUs of a VNF instance",
    context_settings=dict(
        ignore_unknown_options=True,
    ),
)
@click.argument("vnf_name")
@click.argument(
    "args",
    nargs=-1,
    type=click.UNPROCESSED,
    callback=process_vnf_heal_params,
)
@click.option("--timeout", type=int, default=None, help="timeout in seconds")
@click.option(
    "--wait",
    default=False,
    is_flag=True,
    help="do not return the control immediately, but keep it until the operation is completed, or timeout",
)
@click.pass_context
def vnf_heal(
    ctx,
    vnf_name,
    args,
    heal_params,
    timeout,
    wait,
):
    """heals (recreates) a VNF instance or the VDUs of a VNF instance

    VNF_NAME: name or ID of the VNF instance

    \b
    Options:
      --cause TEXT           human readable cause of the healing of the VNF
      --run-day1             indicates whether or not to run day1 primitives for the VNF/VDU
      --vdu TEXT             vdu-id
      --count-index INTEGER  count-index

    \b
    Example:
    osm vnf-heal VNF_INSTANCE_ID --vdu mgmtVM --count-index 1 --run-day1
                                 --vdu mgmtVM --count-index 2
    """
    logger.debug("")
    heal_dict = ctx.params["heal_params"]
    heal_dict["healVnfData"][-1]["vnfInstanceId"] = vnf_name
    logger.debug(f"Heal dict:\n{yaml.safe_dump(heal_dict)}")
    utils.check_client_version(ctx.obj, ctx.command.name)
    vnfr = ctx.obj.vnf.get(vnf_name)
    ns_id = vnfr["nsr-id-ref"]
    ctx.obj.ns.heal(ns_id, heal_dict, wait, timeout)
