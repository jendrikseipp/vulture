from typing import List, Optional
from typing.io import TextIO
from vulture import config

List
Optional
TextIO

# NOTE: This was added to make unit-tests pass and allow commiting intermediate
# work. It should be removed once the TOML parsing is fully implemented.
config._parse_toml
