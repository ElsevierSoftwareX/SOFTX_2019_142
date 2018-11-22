"""Module containing the data structure for experimental values

This module contains the base class ExperimentalValue and all its sub-classes. The
base class represents any object with a value and an uncertainty. An ExperimentalValue
can be the result of an directly recorded measurement, or the result of an operation
done with other instances of ExperimentalValue, which are represented by MeasuredValue
and Function.

This module also provides method overloads for different numeric calculations, so that
any instance of ExperimentalValue can be treated as a regular variable in Python, and
during operations, error propagation will be automatically completed in the background.

"""

import numpy as np

from qexpy.utils.utils import ARRAY_TYPES, NUMBER_TYPES
from qexpy.settings.literals import RECORDED
import qexpy.utils.printing as printing
import qexpy.settings.settings as settings


class ExperimentalValue:
    """Root class for objects with a value and an uncertainty

    This class should not be instantiated directly. Use the record_measurement method
    to create new instances of a MeasuredValue object. The result of operations done with
    other ExperimentalValue objects will be recorded as a Function, which is also a
    child of this class.

    An ExperimentalValue instance can hold multiple value-error pairs. For a MeasuredValue
    object, there can only be one value-error pair. However, for Function objects which
    are the results of operations, have three value-error pairs, each the result of a
    different error method

    The values attribute contains either 1 or 3 value-error pairs. A value-error pair is
    represented as a tuple, with the first entry being the value, and the second being the
    uncertainty on the value. The keys indicate the source of the value-error pair.
    "recorded" suggests that it's a MeasuredValue object with a user recorded value. For
    Function objects, there should be 3 value-error pairs, which is the result of three
    different methods for error propagation. Values for the keys can be found in literals

    Attributes:
        _values (dict): the value-error pairs for this object
        _unit (str): the unit of this value
        _name (str): a name can be given to this value

    """

    __slots__ = "_values", "_unit", "_name"

    def __init__(self, unit="", name=""):
        """Default constructor, not to be called directly"""

        self._values = {}
        # TODO: implement smart unit parsing
        self._unit = unit
        self._name = name

    def __str__(self):
        if isinstance(self, Constant):
            return ""  # There's no point printing a constant value
        string = ""
        # print name of the quantity
        if self.name:
            string += self.name + " = "
        # print the value and error
        string += self._print_value()
        # TODO: implement unit printing
        return string

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        if isinstance(new_name, str):
            self._name = new_name

    @property
    def unit(self):
        return self._unit

    @unit.setter
    def unit(self, new_unit):
        if isinstance(new_unit, str):
            pass  # TODO: implement unit parsing

    def _print_value(self) -> str:
        """Helper method that prints the value-error pair in proper format

        This method is an abstract method. It needs to be overloaded in the children
        of this base class

        """


class MeasuredValue(ExperimentalValue):
    """Root class for values with an uncertainty recorded by the user

    This class is used to hold raw measurement data recorded by a user. It is not to
    be instantiated directly. Use the Measurement method instead.

    """

    def __init__(self, value, error, unit="", name=""):
        super().__init__(unit, name)
        self._values[RECORDED] = (value, error)

    @property
    def value(self):
        """Gets the value for this measurement"""
        return self._values[RECORDED][0]

    @value.setter
    def value(self, new_value):
        """"Modifies the value of a measurement"""
        if isinstance(new_value, NUMBER_TYPES):
            self._values[RECORDED] = (new_value, self._values[RECORDED][1])
        else:
            print("Error: invalid input! You can only set the value of a measurement to a number")
            return
        if hasattr(self, "_raw_data"):  # check if the instance is a repeated measurement
            print("Warning: You are trying to modify the value of a repeated measurement. Doing so has "
                  "caused you to lose the original list of raw measurement data")
            self.__class__ = MeasuredValue  # casting it to base class

    @property
    def error(self):
        """Gets the uncertainty on the measurement"""
        return self._values[RECORDED][1]

    @error.setter
    def error(self, new_error):
        """"Modifies the value of a measurement"""
        if isinstance(new_error, NUMBER_TYPES) and new_error > 0:
            self._values[RECORDED] = (self._values[RECORDED][0], new_error)
        else:
            print("Error: invalid input! You can only set the error of a measurement to a positive number")
            return
        if hasattr(self, "_raw_data"):  # check if the instance is a repeated measurement
            print("Warning: You are trying to modify the uncertainty of a repeated measurement. Doing so has "
                  "caused you to lose the original list of raw measurement data")
            self.__class__ = MeasuredValue  # casting it to base class

    @property
    def relative_error(self):
        """Gets the relative error (error/mean) of a MeasuredValue object."""
        value = self._values[RECORDED]
        return value[1] / value[0] if value[0] != 0 else 0.

    @relative_error.setter
    def relative_error(self, relative_error):
        """Sets the relative error (error/mean) of a MeasuredValue object."""
        value = self._values[RECORDED]
        if isinstance(relative_error, NUMBER_TYPES) and relative_error > 0:
            new_error = value[0] * float(relative_error)
            self._values[RECORDED] = (value[0], new_error)
        else:
            print("Error: invalid input! The relative uncertainty of a measurement has to be a positive number")
            return
        if hasattr(self, "_raw_data"):  # check if the instance is a repeated measurement
            print("Warning: You are trying to modify the uncertainty of a repeated measurement. Doing so has "
                  "caused you to lose the original list of raw measurement data")
            self.__class__ = MeasuredValue  # casting it to base class

    def _print_value(self) -> str:
        value = self._values[RECORDED]
        if value[0] == float('inf'):
            return "inf"
        return printing.get_printer()(value)


class RepeatedlyMeasuredValue(MeasuredValue):
    """The result of repeated measurements of a single quantity

    An instance of this class will be created when the user takes multiple measurements
    of the same quantity. The mean and standard deviation is used as the value and
    uncertainty of this measurement. The raw array of measurement data is preserved

    """

    __slots__ = "_raw_data"

    def __init__(self, measurement_array, unit, name):
        super().__init__(unit, name)
        measurements = np.array(measurement_array)
        self._values[RECORDED] = (measurements.mean(), measurements.std())
        self._raw_data = measurements

    @property
    def raw_data(self):
        """Gets the raw data that was used to generate this measurement"""
        from copy import deepcopy
        # returns a copy of the list so that the original data is not tempered
        return deepcopy(self._raw_data)

    def show_histogram(self):
        """Plots the raw measurement data in a histogram

        For the result of repeated measurements of a single quantity, the raw measurement
        data is preserved. With this method, you can visualize these values in a histogram.
        with lines corresponding to the mean and the range covered by one standard deviation

        """


# noinspection PyPep8Naming
def Measurement(*args, **kwargs) -> MeasuredValue:
    """Records a measurement with uncertainties

    This method is used to create a MeasuredValue object from a single measurement or
    an array of repeated measurements of a single quantity (if you want them averaged).
    This method is named upper case because it is a wrapper for constructors, and should
    look like a constructor from the outside

    When two values are passed to this method, the first argument will be recognized as
    the value, the second as the uncertainty. If the second value is not provided, the
    uncertainty is by default set to 0. If a list of values is passed to this method,
    the mean and standard deviation of the value will be calculated and returned as
    the value and error of the MeasuredValue object.

    Usage:
        Measurement(12, 1) -> 12 +/- 1
        Measurement(12) -> 12 +/- 0
        Measurement([5.6, 4.8, 6.1, 4.9, 5.1]) -> 5.3000 +/- 0.5431

    You can also specify the name and unit of the value as keyword arguments.

    For example:
        Measurement(12, 1, name="length", unit="m") -> length = 12 +/- 1 [m]

    """

    if len(args) == 1 and isinstance(args[0], ARRAY_TYPES):
        return RepeatedlyMeasuredValue(args[0], kwargs["unit"], kwargs["name"])
    elif len(args) == 1 and isinstance(args[0], NUMBER_TYPES):
        return MeasuredValue(float(args[0]), 0, kwargs["unit"], kwargs["name"])
    elif len(args) == 2 and isinstance(args[0], NUMBER_TYPES) and isinstance(args[1], NUMBER_TYPES):
        return MeasuredValue(float(args[0]), float(args[1]), kwargs["unit"], kwargs["name"])
    else:
        print("Error: invalid input! Input must be either a single array of values, or the central value "
              "and its uncertainty in one measurement")


class Function(ExperimentalValue):
    """The result of operations done with other ExperimentalValue objects

    This class is not to be instantiated directly. It will be created when operations
    are done on other ExperimentalValue objects

    Attributes:
        _error_method (ErrorMethod): the error method used for this value
        _is_error_method_specified (bool): true if the user specified an error method for
            this value, false if default was used

    """

    __slots__ = "_error_method", "_is_error_method_specified"

    def __init__(self, propagated_results, unit="", name="", error_method=None):
        """The default constructor for the result of an operation

        The argument for this constructor, "propagated_results" is an dictionary object
        with three entries. The keys should be DERIVATIVE_PROPAGATED, MIN_MAX_PROPAGATED,
        MONTE_CARLO_PROPAGATED, and the entries are tuples representing the value-error
        pairs resulting from each error method.

        There is no check for the validity of the input argument, since this method will
        not be called by a user. A developer is expected to pass legal arguments to this
        constructor.

        Args:
            propagated_results (dict): Three value-error pairs for three error methods
            unit (str): The unit of the value
            name (str): The name of this value

        """
        super().__init__(unit, name)
        self._values = propagated_results
        # set default error method for this value
        if error_method:
            self._is_error_method_specified = True
            self._error_method = error_method
        else:
            # use global default if not specified
            self._is_error_method_specified = False
            self._error_method = settings.get_error_method()

    def _print_value(self) -> str:
        if self._is_error_method_specified:
            value = self._values[self._error_method.value]
        else:
            value = self._values[settings.get_error_method().value]
        if value[0] == float('inf'):
            return "inf"
        return printing.get_printer()(value)


class Constant(ExperimentalValue):
    """A value with no uncertainty

    This is created when a constant (int, float, etc.) is used in operation with another
    ExperimentalValue. This class is instantiated before calculating operations to ensure
    objects can be combined.

    """


class MeasurementArray(np.ndarray):
    """An array of measurements

    This class is used to hold a series of measurements. It can be used for data analysis,
    fitting, and plotting.

    """