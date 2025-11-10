# SPDX-FileCopyrightText: Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
from pathlib import Path
from typing import ItemsView

import yaml
from fastramqpi.config import ClientSettings
from fastramqpi.config import FastAPIIntegrationSystemSettings
from pydantic import BaseModel
from pydantic import FilePath


class ConfigRootOrganisation(BaseModel):
    municipality_code: int | None


class ConfigClass(BaseModel):
    title: str
    scope: str | None
    it_system: str | None
    description: str | None


class ConfigFacet(BaseModel):
    __root__: dict[str, ConfigClass]

    def items(self) -> ItemsView[str, ConfigClass]:
        return self.__root__.items()


class ConfigFile(BaseModel):
    root_organisation: ConfigRootOrganisation | None
    facets: dict[str, ConfigFacet] | None
    it_systems: dict[str, str] | None


def get_config_file(config_file: Path) -> ConfigFile:
    with config_file.open() as f:
        config_yaml = yaml.safe_load(f)
    config = ConfigFile.parse_obj(config_yaml)
    return config


class Settings(FastAPIIntegrationSystemSettings, ClientSettings):
    class Config:
        frozen = True

    config_file: FilePath = Path("/config/config.yml")
