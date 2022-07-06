from ..auxiliaries.arithmetic_dict import Arithmetic_Dict
from ..auxiliaries.constants import (
    EMPTY_RESOURCES,
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
    new_resources - temporary resources owned by the govt
    secure_resources - govt's resources declared to be untradeable
    real_resources - how much resources in total the govt owns
    optimal_resources - how much resources the govt wants to own
    max_employees - how many employees can the govt employ
    """
    def __init__(self, parent, res: dict = None, optimal_res: dict = None,
                 secure_res: dict = None):
        """
        Creates an object of type Government.
        Parent is the State_Data object this belongs to.
        """
        self.parent = parent
        if res is None:
            self._resources = EMPTY_RESOURCES
        else:
            if set(res.keys()) != set(RESOURCES):
                raise InvalidResourcesDictError
            for value in res.values():
                if value < 0:
                    raise NegativeResourcesError
            self._resources = Arithmetic_Dict(res)

        self._new_resources = self.resources.copy()

        if optimal_res is None:
            self.optimal_resources = EMPTY_RESOURCES
        else:
            if set(optimal_res.keys()) != set(RESOURCES):
                raise InvalidResourcesDictError
            for value in optimal_res.values():
                if value < 0:
                    raise NegativeResourcesError
            self.optimal_resources = Arithmetic_Dict(optimal_res)

        if secure_res is None:
            self._secure_resources = EMPTY_RESOURCES
        else:
            if set(secure_res.keys()) != set(RESOURCES):
                raise InvalidResourcesDictError
            for value in secure_res.values():
                if value < 0:
                    raise NegativeResourcesError
            self._secure_resources = Arithmetic_Dict(secure_res)

        self.wage = self.parent.sm.others_minimum_wage
        self.wage_autoregulation = True

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
        if set(new_new_resources.keys()) != set(RESOURCES):
            raise InvalidResourcesDictError
        self._new_resources = Arithmetic_Dict(new_new_resources.copy())

    @property
    def secure_resources(self):
        return self._secure_resources.copy()

    @secure_resources.setter
    def secure_resources(self, new_secure_resources: dict | Arithmetic_Dict):
        if set(new_secure_resources.keys()) != set(RESOURCES):
            raise InvalidResourcesDictError
        for value in new_secure_resources.values():
            if value < 0:
                raise NegativeResourcesError
        self._secure_resources = Arithmetic_Dict(new_secure_resources.copy())

    @property
    def real_resources(self):
        return self.resources + self.secure_resources

    @property
    def max_employees(self):
        land_owned = self.resources["land"]
        return min(
            self.resources["tools"] / 3,
            land_owned / self.parent.sm.worker_land_usage,
        )

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
        for key, value in self._new_resources.items():
            if value < 0:
                if self._secure_resources[key] >= -value:
                    self._secure_resources[key] += value
                    self._new_resources[key] = 0
                else:
                    raise NegativeResourcesError

        self._resources = self._new_resources.copy()
