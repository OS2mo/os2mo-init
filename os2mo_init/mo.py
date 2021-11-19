# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
import asyncio
from typing import Any
from typing import Optional
from uuid import UUID

from gql import gql
from gql.client import AsyncClientSession
from gql.transport.exceptions import TransportQueryError
from httpx import AsyncClient


async def get_root_org(graphql_session: AsyncClientSession) -> Optional[UUID]:
    """
    Get UUID of the existing root MO organisation.

    Args:
        graphql_session: MO GraphQL client session.

    Returns: The UUID of the root organisation if it is configured. None otherwise.
    """
    query = gql(
        """
        query RootOrgQuery {
            org {
                uuid
            }
        }
        """
    )
    try:
        result = await graphql_session.execute(query)
        return UUID(result["org"]["uuid"])
    except TransportQueryError as e:
        if e.errors[0].message == "ErrorCodes.E_ORG_UNCONFIGURED":
            return None
        raise e


async def get_facets(
    client: AsyncClient, organisation_uuid: UUID
) -> dict[str, UUID]:
    """
    Get existing facets.

    Args:
        client: Authenticated MO client.
        organisation_uuid: Root organisation UUID of the facets.

    Returns: Dictionary mapping facet user keys into their UUIDs.
    """
    r = await client.get(f"/service/o/{organisation_uuid}/f/")
    facets = r.json()
    return {f["user_key"]: UUID(f["uuid"]) for f in facets}


async def get_classes_for_facet(
    client: AsyncClient, facet_uuid: UUID
) -> list[dict[str, Any]]:
    """
    Get existing classes for a given facet.

    Args:
        client: Authenticated MO client.
        facet_uuid: UUID of the facet to get classes for.

    Returns: List of class dicts for the given facet.
    """
    r = await client.get(f"/service/f/{facet_uuid}/")
    return r.json()["data"]["items"]


async def get_classes(
    client: AsyncClient, facets: dict[str, UUID]
) -> dict[str, dict[str, UUID]]:
    """
    Get existing classes.

    Args:
        client: Authenticated MO client.
        facets: Dictionary mapping facet user keys into UUIDs.

    Returns: Nested dictionary mapping facet user keys to a dictionary mapping class
     user keys to UUIDs.
    """
    classes_for_facets = (
        get_classes_for_facet(client=client, facet_uuid=facet_uuid)
        for facet_uuid in facets.values()
    )
    facets_and_classes = zip(facets.keys(), await asyncio.gather(*classes_for_facets))
    return {
        facet_user_key: {
            facet_class["user_key"]: UUID(facet_class["uuid"])
            for facet_class in facet_classes
        }
        for facet_user_key, facet_classes in facets_and_classes
    }
