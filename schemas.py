from pydantic import BaseModel,EmailStr,Field
from datetime import date,datetime
from decimal import Decimal
class Bootstrap(BaseModel): company_name:str; cnpj:str; name:str; email:EmailStr; password:str=Field(min_length=12)
class AssetCreate(BaseModel): category_id:int; block_id:int; responsible_id:int|None=None; name:str; description:str|None=None; serial_number:str|None=None; acquired_on:date|None=None; value:Decimal|None=None; state:str='AVAILABLE'
class MoveCreate(BaseModel): destination_block_id:int; type:str; purpose:str|None=None; due_at:datetime|None=None
