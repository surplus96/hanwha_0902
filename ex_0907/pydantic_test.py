from datetime import datetime
from pydantic import BaseModel, PositiveInt, ValidationError
from typing import Annotated, Literal
from annotated_types import Gt

class User(BaseModel):
    id: int
    name: str = 'John Doe'
    signup_ts: datetime | None
    tastes: dict[str, PositiveInt]

external_data = {
    'id': 123,
    'signup_ts': '2019-06-01 12:22',
    'tastes': {
        'wine': 9,
        b'cheese': 7,
        'cabbage': '1',
    },
}


user = User(**external_data)

print(user.id)  #> 123
print(user.model_dump())
print("--------------------------------------------")

"""
{
    'id': 123,
    'name': 'John Doe',
    'signup_ts': datetime.datetime(2019. 6, 1, 12, 22),
    'tastes': {'wine': 9, 'cheese': 7, 'cabbage': 1},
}
"""

external_data2 = {
    'id': 'not an int',
    'tastes': {},
}

try:
    User(**external_data2)
except ValidationError as e:
    print(e.errors())

class Fruit(BaseModel):
    name: str
    color: Literal['red', 'green']
    weight: Annotated[float, Gt(0)]
    bazam: dict[str, list[tuple[int, bool, float]]]

print(
    Fruit(
    name='Apple',
    color='red',
    weight=4.2,
    bazam={'foobar':[(1, True, 0.1)]},
    )
)
print("--------------------------------------------")

class Meeting(BaseModel):
    when:datetime
    where:bytes
    why:str="No idea"

m = Meeting(when='2020-01-01T12:00', where='home')
print(m.model_dump(exclude_unset=True))
print(m.model_dump(exclude={'where'}, mode='json'))
print(m.model_dump_json(exclude_defaults=True))
print("--------------------------------------------3")