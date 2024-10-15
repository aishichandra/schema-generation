from typing import List, Union

from pydantic import BaseModel


class Table(BaseModel):
    class Column(BaseModel):
        column_name: str
        column_data_type: str
        column_data: List[Union[str, int, float]]

    table_name: str
    table_columns: List["Table.Column"]
