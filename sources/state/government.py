from ..auxiliaries.arithmetic_dict import Arithmetic_Dict
from ..auxiliaries.constants import (
    RESOURCES,
    MONTHS
)
from .social_classes.class_file import (
    InvalidResourcesDictError,
    InvalidParentError,
    NegativeResourcesError
)


class Government:
    """
    Represents the government of the country - the object that the player has
    the most direct control over.
    Properties:
    parent - state this government is part of
    resources - dictionary containing info on the resources the govt owns
    optimal_resources - how much resources the govt wants to own
    """
    def __init__(self, parent, res: dict = None, optimal_res: dict = None):
        """
        Creates an object of type Government.
        Parent is the State_Data object this belongs to.
        """
        self.parent = parent
        if res is None:
            self._resources = Arithmetic_Dict({
                resource: 0 for resource in RESOURCES
            })
        else:
            for resource in RESOURCES:
                if resource not in res:
                    raise InvalidResourcesDictError
            self._resources = Arithmetic_Dict(res)

        self._new_resources = self.resources.copy()
        if optimal_res is None:
            self.optimal_resources = Arithmetic_Dict({
                resource: 0 for resource in RESOURCES
            })
        else:
            for resource in RESOURCES:
                if resource not in optimal_res:
                    raise InvalidResourcesDictError
            self.optimal_resources = Arithmetic_Dict(optimal_res)

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, new_parent):
        if not hasattr(new_parent, "month"):
            raise InvalidParentError
        if new_parent.month not in MONTHS:
            raise InvalidParentError
        self._parent = new_parent

    @property
    def resources(self):
        return self._resources.copy()

    @property
    def new_resources(self):
        return self._new_resources.copy()

    @new_resources.setter
    def new_resources(self, new_new_resources: dict | Arithmetic_Dict):
        """
        Does not modify the actual resources, saves the changes in temporary
        _new_resources. Use flush() to confirm the changes.
        """
        for resource in RESOURCES:
            if resource not in new_new_resources:
                raise InvalidResourcesDictError
        self._new_resources = Arithmetic_Dict(new_new_resources.copy())

    def to_dict(self):
        """
        Converts the government object to a dict. Does not save temporary
        attributes (new_resources).
        """
        data = {
            "resources": dict(self.resources),
            "optimal_resources": dict(self.optimal_resources),
        }
        return data

    @classmethod
    def from_dict(cls, parent, data):
        """
        Creates a government object from the given dict.
        """
        return cls(parent, data["resources"], data["optimal_resources"])

    def handle_negative_resources(self):
        """
        Handles minimal negative resources resulting from floating-point
        rounding errors.
        """
        for resource in self._new_resources:
            if self._new_resources[resource] < 0 and \
                 abs(self._new_resources[resource]) < 0.001:
                self._new_resources[resource] = 0

    def flush(self):
        """
        To be run after multifunctional calculations - to save the temporary
        changes, after checking validity.
        """
        if set(self._new_resources.keys()) != set(RESOURCES):
            raise InvalidResourcesDictError

        self.handle_negative_resources()
        for value in self._new_resources.values():
            if value < 0:
                raise NegativeResourcesError

        self._resources = self._new_resources.copy()
