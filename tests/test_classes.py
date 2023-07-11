# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from unittest.mock import ANY
from unittest.mock import AsyncMock
from unittest.mock import call
from uuid import UUID

from os2mo_init.classes import Class
from os2mo_init.classes import ensure_classes
from os2mo_init.classes import Facet
from os2mo_init.classes import get_classes
from os2mo_init.config import ConfigClass
from os2mo_init.config import ConfigFacet


async def test_get_classes() -> None:
    """Test GraphQL parsing."""
    graphql_session = AsyncMock()
    graphql_session.execute.return_value = {
        "facets": {
            "objects": [
                {
                    "current": {
                        "uuid": "182df2a8-2594-4a3f-9103-a9894d5e0c36",
                        "user_key": "engagement_type",
                        "classes": [
                            {
                                "uuid": "8acc5743-044b-4c82-9bb9-4e572d82b524",
                                "user_key": "Ansat",
                                "name": "Ansat",
                                "scope": "TEXT",
                            }
                        ],
                    }
                },
                {
                    "current": {
                        "uuid": "2cc2dbc5-30dc-4955-8b9a-19fe32b41ce4",
                        "user_key": "visibility",
                        "classes": [
                            {
                                "uuid": "940b39cd-828e-4b6d-a98c-007e512f694c",
                                "user_key": "Ekstern",
                                "name": "Må vises eksternt",
                                "scope": "PUBLIC",
                            },
                            {
                                "uuid": "c0bb2572-8432-720e-0f97-3c61bb7bbb2e",
                                "user_key": "Secret",
                                "name": "Hemmelig",
                                "scope": "SECRET",
                            },
                        ],
                    }
                },
            ]
        }
    }

    classes = await get_classes(graphql_session)

    assert classes == [
        Facet(
            uuid=UUID("182df2a8-2594-4a3f-9103-a9894d5e0c36"),
            user_key="engagement_type",
            classes=[
                Class(
                    uuid=UUID("8acc5743-044b-4c82-9bb9-4e572d82b524"),
                    user_key="Ansat",
                    name="Ansat",
                    scope="TEXT",
                )
            ],
        ),
        Facet(
            uuid=UUID("2cc2dbc5-30dc-4955-8b9a-19fe32b41ce4"),
            user_key="visibility",
            classes=[
                Class(
                    uuid=UUID("940b39cd-828e-4b6d-a98c-007e512f694c"),
                    user_key="Ekstern",
                    name="Må vises eksternt",
                    scope="PUBLIC",
                ),
                Class(
                    uuid=UUID("c0bb2572-8432-720e-0f97-3c61bb7bbb2e"),
                    user_key="Secret",
                    name="Hemmelig",
                    scope="SECRET",
                ),
            ],
        ),
    ]


async def test_ensure_classes(monkeypatch) -> None:
    """Test that classes are created or updated."""
    get_classes_mock = AsyncMock()
    get_classes_mock.return_value = [
        Facet(
            uuid=UUID("182df2a8-2594-4a3f-9103-a9894d5e0c36"),
            user_key="engagement_type",
            classes=[
                Class(
                    uuid=UUID("8acc5743-044b-4c82-9bb9-4e572d82b524"),
                    user_key="Ansat",
                    name="Ansat",
                    scope="TEXT",
                )
            ],
        ),
        Facet(
            uuid=UUID("2cc2dbc5-30dc-4955-8b9a-19fe32b41ce4"),
            user_key="visibility",
            classes=[],
        ),
    ]
    monkeypatch.setattr("os2mo_init.classes.get_classes", get_classes_mock)

    graphql_session = AsyncMock()

    config_classes = {
        "engagement_type": ConfigFacet(
            __root__={
                "Ansat": ConfigClass(
                    title="Updated Title",
                    scope="Updated Scope",
                )
            }
        ),
        "visibility": ConfigFacet(
            __root__={
                "Intern": ConfigClass(
                    title="New Internal Title",
                    scope="NEW INTERNAL SCOPE",
                )
            }
        ),
    }
    await ensure_classes(graphql_session, config_classes)

    graphql_session.execute.assert_has_awaits(
        [
            call(
                ANY,
                {
                    "facet_uuid": "182df2a8-2594-4a3f-9103-a9894d5e0c36",
                    "uuid": "8acc5743-044b-4c82-9bb9-4e572d82b524",
                    "user_key": "Ansat",
                    "name": "Updated Title",
                    "scope": "Updated Scope",
                },
            ),
            call(
                ANY,
                {
                    "facet_uuid": "2cc2dbc5-30dc-4955-8b9a-19fe32b41ce4",
                    "user_key": "Intern",
                    "name": "New Internal Title",
                    "scope": "NEW INTERNAL SCOPE",
                },
            ),
        ]
    )
