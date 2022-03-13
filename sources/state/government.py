from ..auxiliaries.constants import (
    RESOURCES,
    LAND_TYPES,
    MONTHS
)
from ..auxiliaries.arithmetic_dict import Arithmetic_Dict


class Government:
    """
    Represents the government of the country.
    Properties:
    parent - state of this govt
    resources - dictionary containing info on the resources the govt owns
    land - dictionary containing info on the land the govt owns
    optimal_resources - how much resources the govt wants to own
    """
    def __init__(self, parent, resources: dict = None, land: dict = None):
        self.parent = parent
        if resources is None:
            self.resources = {
                resource: 0 for resource in RESOURCES
            }
        else:
            self.resources = resources

        if land is None:
            self.land = {
                land_type: 0 for land_type in LAND_TYPES
            }
        else:
            self.land = land

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, new_parent):
        assert new_parent.month in MONTHS
        self._parent = new_parent

    @property
    def resources(self):
        return self._resources

    @resources.setter
    def resources(self, new_resources: dict):
        for resource in RESOURCES:
            assert resource in new_resources
        self._resources = Arithmetic_Dict(new_resources)

    @property
    def land(self):
        return self._land

    @land.setter
    def land(self, new_land: dict):
        for land_type in LAND_TYPES:
            assert land_type in new_land
            assert new_land[land_type] >= 0
        self._land = Arithmetic_Dict(new_land)

    @property
    def optimal_resources(self):
        opt_res = {
            resource: resource_per_capita * self._population
            for resource, resource_per_capita
            in self.optimal_resources_per_capita().items()
        }
        return Arithmetic_Dict(opt_res)
