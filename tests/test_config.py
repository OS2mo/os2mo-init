# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from pathlib import Path
from textwrap import dedent

from os2mo_init.config import get_config_file


def test_get_config_file(config_file: Path) -> None:
    config_str = dedent(
        """
        root_organisation:
          municipality_code: 123
        facets:
          org_unit_address_type:
            PhoneUnit:
              title: "Telefon"
              scope: "PHONE"
              it_system: OS2mo
        it_systems:
          AD: "Active Directory"
        """
    )
    config_file.write_text(config_str)
    config = get_config_file(config_file)
    assert config.dict() == {
        "root_organisation": {
            "municipality_code": 123,
        },
        "facets": {
            "org_unit_address_type": {
                "PhoneUnit": {
                    "scope": "PHONE",
                    "title": "Telefon",
                    "description": None,
                    "it_system": "OS2mo",
                },
            }
        },
        "it_systems": {
            "AD": "Active Directory",
        },
    }


def test_nothing() -> None:
    """Our CI templates requires at least two unittests."""
