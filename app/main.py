from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
from datetime import timedelta, datetime

from app.schemas import UserCreate, User, TransacaoCriar, Transacao, TipoTransacao
from app.auth import authenticate_user, create_access_token, get_current_user, get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES
from app.database import db_users

app = FastAPI(title="API Bancária Assíncrona com FastAPI")

@app.post("/users/", response_model=User, tags=["Usuários"])
async def criar_usuario(user: UserCreate):
    if user.username in db_users:
        raise HTTPException(status_code=400, detail="Usuário já existe")
    hashed_password = get_password_hash(user.password)
    novo_usuario = {
        "id": len(db_users) + 1,
        "username": user.username,
        "hashed_password": hashed_password,
        "saldo": 0.0,
        "transacoes": []
    }
    db_users[user.username] = novo_usuario
    return novo_usuario

@app.post("/token", tags=["Autenticação"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Usuário ou senha incorretos")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user["username"]}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/transacoes", tags=["Transações"])
async def criar_transacao(transacao: TransacaoCriar, current_user: dict = Depends(get_current_user)):
    global id_transacao_seq
    if transacao.tipo == TipoTransacao.saque and current_user["saldo"] < transacao.valor:
        raise HTTPException(status_code=400, detail="Saldo insuficiente para saque")

    if transacao.tipo == TipoTransacao.saque:
        current_user["saldo"] -= transacao.valor
    else:
        current_user["saldo"] += transacao.valor

    nova_transacao = {
        "id": id_transacao_seq,
        "tipo": transacao.tipo,
        "valor": transacao.valor,
        "data": datetime.utcnow()
    }
    id_transacao_seq += 1
    current_user["transacoes"].append(nova_transacao)
    return {"msg": "Transação realizada com sucesso", "transacao": nova_transacao}

@app.get("/extrato", response_model=List[Transacao], tags=["Extrato"])
async def extrato(current_user: dict = Depends(get_current_user)):
    return current_user["transacoes"]
