from typing import List
from datetime import datetime
from pydantic import BaseModel, PositiveFloat
from enum import Enum

class TipoTransacao(str, Enum):
    deposito = "deposito"
    saque = "saque"

class TransacaoBase(BaseModel):
    tipo: TipoTransacao
    valor: PositiveFloat

class TransacaoCriar(TransacaoBase):
    pass

class Transacao(TransacaoBase):
    id: int
    data: datetime

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    saldo: float
    transacoes: List[Transacao] = []

    class Config:
        orm_mode = True
