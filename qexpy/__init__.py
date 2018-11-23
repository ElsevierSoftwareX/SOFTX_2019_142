import sys

__version__ = '2.0.1'

from .utils import load_data_from_file
from .settings import set_print_style, set_error_method, reset_default_configuration

from .data import Measurement

# Check the python interpreter version
if sys.version_info[0] < 3:  # No reason to assume a future Python 4 will break comparability.
    raise ImportError("Error: QExPy is only supported on Python 3. Please upgrade your interpreter.\n"
                      "If you're using Anaconda, you can download the correct version here:\n"
                      "https://www.continuum.io/downloads")
