# API v1 Routes
from typing import Annotated

from fastapi import Path

# Database row IDs are SQL ``INTEGER`` (signed 32-bit).  Values larger than
# 2**31 - 1 would otherwise reach psycopg and raise ``NumericValueOutOfRange``
# (HTTP 500).  Constraining the path parameter lets FastAPI return a clean 422
# before we hit the database.
IdPath = Annotated[int, Path(ge=1, le=2_147_483_647)]
