# Contoh schema Pydantic
from pydantic import BaseModel
from pydantic import ConfigDict


class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = None
    name: str
    email: str
    password: str = None
