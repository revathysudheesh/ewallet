
from datetime import datetime
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
from sqlalchemy import func
from auth import create_access_token, create_refresh_token, decode_jwt_token, get_hashed_password, verify_password
from schema import User, UserLogin, UserReturn
from models import Account, Transaction, User as UserModel
from fastapi_sqlalchemy import db
token_auth_schema = OAuth2PasswordBearer(tokenUrl="/login",
    scheme_name="JWT"
)

router=APIRouter()

@router.get("/")
async def root():
    return {"message": "hello world"}

@router.post('/register', response_model=UserReturn)
async def register(request:Request):
    data= await request.json()
    username=data.get('username',None)
    password=data.get('password',None)
    first_name=data.get('first_name',None)
    email=data.get('email',None)
    contact=data.get('contact',None)
    user = db.session.query(UserModel).filter(UserModel.username == username).first()
    if user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password= get_hashed_password(password)
    user = UserModel(username=username, password=hashed_password, first_name=first_name, email=email,contact=contact)
    db.session.add(user)
    db.session.commit()
    account = Account(user_id=user.id)
    db.session.add(account)
    db.session.commit()
    return user
 

@router.post("/login/")
async def login_user(request_data: Request, login_data: UserLogin):
    """it access the model and check the table email with user typed email,if not equals no
     emailfound message appeare then it checks the password  user typed password(login_data) with database data(user)"""
    request_body  = await request_data.json()
    user = db.session.query(UserModel).filter(UserModel.username == request_body.get("username")).first()
    if not user:
        return dict(status_code=401, message="No Username Found")
    
    else:
        password=request_body.get("password")
        auth_password=verify_password(password,user.password)
        if not auth_password:
            return dict(status_code=401, message="Invalid password")
           
        return {
        "access_token": create_access_token(user.username, user.id),
        "refresh_token": create_refresh_token(user.username,user.id)
        
    }

@router.post("/deposit")
async def deposit_money(
     request_data: Request,
    token: str = Depends(token_auth_schema)
):
    try:
        request_body  = await request_data.json()
        transaction_amount=request_body.get("deposit_amount")
        payload = decode_jwt_token(token)
        if payload.get("status") != 200:
            return payload
        username = payload.get("message",None).get('sub')
        user_id = payload.get("message",None).get('user_id')
        user = db.session.query(UserModel).filter(UserModel.username == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        account = db.session.query(Account).filter(Account.user_id == user_id).first()
        transaction = Transaction(
            transaction_type="DEPOSIT",
            from_account=None,
            to_account=account.id,
            transaction_amount=transaction_amount,
            transaction_date=datetime.now()
        )
        db.session.add(transaction)
        account.balance += transaction_amount
        db.session.commit()
        return {"message": f"Successfully deposited {transaction_amount} credits into {user.username}'s account"}

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=500, detail="Deposit failed")
    finally:
        db.session.close()

@router.post("/withrawal")
async def withdraw_money(
     request_data: Request,
    token: str = Depends(token_auth_schema)
):
    try:
        request_body  = await request_data.json()
        transaction_amount=request_body.get("withdraw_amount")
        payload = decode_jwt_token(token)
        if payload.get("status") != 200:
            return payload
        username = payload.get("message",None).get('sub')
        user_id = payload.get("message",None).get('user_id')
        user = db.session.query(UserModel).filter(UserModel.username == username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        account = db.session.query(Account).filter(Account.user_id == user_id).first()
        if account.balance<transaction_amount:
            raise HTTPException(status_code=400, detail="Insufficient balance")
        transaction = Transaction(
            transaction_type="WITHDRAW",
            from_account=account.id,
            to_account=None,
            transaction_amount=transaction_amount,
            transaction_date=datetime.now()
        )
        db.session.add(transaction)
        account.balance -= transaction_amount
        db.session.commit()
        return {"message": f"Successfully withdrew {transaction_amount} debits from {user.username}'s account"}

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=500, detail="Deposit failed")
    finally:
        db.session.close()

@router.post("/transfer")
async def transfer_money(
    request_data: Request,
    token: str = Depends(token_auth_schema)
):
    
    result = decode_jwt_token(token)
    if result.get("status") != 200:
        return result
    request_body  = await request_data.json()
    recipient_username=request_body.get("recipient_username")
    amount=request_body.get("amount")
    user_id = result['message']['user_id']
    recipient = db.session.query(UserModel).filter(UserModel.username == recipient_username).first()
    current_user = db.session.query(UserModel).filter(UserModel.id == user_id).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    sender_account = db.session.query(Account).filter(Account.user_id == user_id).first()
    receiver_account = db.session.query(Account).filter(Account.user_id == recipient.id).first()
    if sender_account.balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    try:
        sender_account.balance -= amount
        receiver_account.balance += amount

        transaction = Transaction(
            transaction_type="TRANSFER",
            from_account=sender_account.id,
            to_account=receiver_account.id,
            transaction_amount=amount,
            transaction_date=datetime.now()
        )
        db.session.add(transaction)
        db.session.commit()
        return {"message": "Transfer successful"}
    except Exception as e:
        db.session.rollback()
        raise HTTPException(status_code=500, detail="Transfer failed")
    finally:
        db.session.close()



@router.get("/transactions")
async def get_transaction_history(
    request_data: Request,
    token: str = Depends(token_auth_schema)
):
    try:
        request_body  = await request_data.json()
        start_date=request_body.get("start_date")
        end_date=request_body.get("end_date")
        payload = decode_jwt_token(token)
        if payload.get("status") != 200:
            return payload
        user_id = payload.get("message",None).get('user_id')
        account = db.session.query(Account).filter(Account.user_id == user_id).first()
        if start_date:
            start_datetime = datetime.strptime(start_date, "%d-%m-%Y").date()
        else:
            start_datetime = None
        if end_date:
            end_datetime = datetime.strptime(end_date, "%d-%m-%Y").date()
        else:
            end_datetime = None
        # query = db.session.query(Transaction).join(Transaction.sender).filter(Transaction.sender.has(username=username))
        
        query =db.session.query(Transaction).filter((Transaction.from_account == account.id)
                                                     | (Transaction.to_account == account.id)).order_by(Transaction.transaction_date.desc())
        if start_datetime:
            
            query = query.filter(func.date(Transaction.transaction_date) >= start_datetime)
            
        if end_datetime:
            query = query.filter(func.date(Transaction.transaction_date) <= end_datetime)
        transactions = query.all()
        db.session.close()
        return {"transactions": transactions}
    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch transactions")
    finally:
        db.session.close()