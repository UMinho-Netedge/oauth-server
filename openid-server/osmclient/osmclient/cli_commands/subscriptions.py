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


@click.command(
    name="subscription-create",
    short_help="creates a new subscription to a specific event",
)
@click.option(
    "--event_type",
    # type=click.Choice(['ns', 'nspkg', 'vnfpkg'], case_sensitive=False))
    type=click.Choice(["ns"], case_sensitive=False),
    help="event type to be subscribed (for the moment, only ns is supported)",
)
@click.option("--event", default=None, help="specific yaml configuration for the event")
@click.option(
    "--event_file", default=None, help="specific yaml configuration file for the event"
)
@click.pass_context
def subscription_create(ctx, event_type, event, event_file):
    """creates a new subscription to a specific event"""
    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    if event_file:
        if event:
            raise ClientException(
                '"--event" option is incompatible with "--event_file" option'
            )
        with open(event_file, "r") as cf:
            event = cf.read()
    ctx.obj.subscription.create(event_type, event)


@click.command(name="subscription-delete", short_help="deletes a subscription")
@click.option(
    "--event_type",
    # type=click.Choice(['ns', 'nspkg', 'vnfpkg'], case_sensitive=False))
    type=click.Choice(["ns"], case_sensitive=False),
    help="event type to be subscribed (for the moment, only ns is supported)",
)
@click.argument("subscription_id")
@click.option(
    "--force", is_flag=True, help="forces the deletion bypassing pre-conditions"
)
@click.pass_context
def subscription_delete(ctx, event_type, subscription_id, force):
    """deletes a subscription

    SUBSCRIPTION_ID: ID of the subscription to be deleted
    """
    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    ctx.obj.subscription.delete(event_type, subscription_id, force)


@click.command(name="subscription-list", short_help="list all subscriptions")
@click.option(
    "--event_type",
    # type=click.Choice(['ns', 'nspkg', 'vnfpkg'], case_sensitive=False))
    type=click.Choice(["ns"], case_sensitive=False),
    help="event type to be subscribed (for the moment, only ns is supported)",
)
@click.option(
    "--filter",
    default=None,
    multiple=True,
    help="restricts the list to the subscriptions matching the filter",
)
@click.pass_context
def subscription_list(ctx, event_type, filter):
    """list all subscriptions"""
    logger.debug("")
    utils.check_client_version(ctx.obj, ctx.command.name)
    if filter:
        filter = "&".join(filter)
    resp = ctx.obj.subscription.list(event_type, filter)
    table = PrettyTable(["id", "filter", "CallbackUri"])
    for sub in resp:
        table.add_row(
            [
                sub["_id"],
                utils.wrap_text(text=json.dumps(sub["filter"], indent=2), width=70),
                sub["CallbackUri"],
            ]
        )
    table.align = "l"
    print(table)


@click.command(
    name="subscription-show", short_help="shows the details of a subscription"
)
@click.argument("subscription_id")
@click.option(
    "--event_type",
    # type=click.Choice(['ns', 'nspkg', 'vnfpkg'], case_sensitive=False))
    type=click.Choice(["ns"], case_sensitive=False),
    help="event type to be subscribed (for the moment, only ns is supported)",
)
@click.option(
    "--filter",
    multiple=True,
    help="restricts the information to the fields in the filter",
)
@click.pass_context
def subscription_show(ctx, event_type, subscription_id, filter):
    """shows the details of a subscription

    SUBSCRIPTION_ID: ID of the subscription
    """
    logger.debug("")
    resp = ctx.obj.subscription.get(subscription_id)
    table = PrettyTable(["key", "attribute"])
    for k, v in list(resp.items()):
        if not filter or k in filter:
            table.add_row([k, utils.wrap_text(text=json.dumps(v, indent=2), width=100)])
    table.align = "l"
    print(table)
