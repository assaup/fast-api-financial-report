from app.service import operations as operations_service
from fastapi import APIRouter, Depends
from app.schemas import OperationRequest
from sqlalchemy.orm import Session
from app.dependency import get_db

router = APIRouter()
@router.post("/operation/income")
def add_income(operation: OperationRequest, db: Session = Depends(get_db)):
    return operations_service.add_income(db, operation)


@router.post("/operation/expense")
def add_expense(operation: OperationRequest, db: Session = Depends(get_db)):
    return operations_service.add_expense(db, operation)

