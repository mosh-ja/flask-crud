
from __future__ import annotations
import logging, time
from datetime import datetime
from typing import Any, Dict, List

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import Integer, String, DateTime, Column, ForeignKey, and_, or_
from sqlalchemy.exc import OperationalError, IntegrityError
from werkzeug.exceptions import BadRequest, Conflict


log = logging.getLogger(__name__)
db = SQLAlchemy()


def init_db(app, retry: int = 2):
    try:
        log.info('Initializing the DB')
        db.create_all(app=app)
        Migrate(app, db)
        log.info('The DB is initialized')
    except OperationalError as err:
        if retry > 1 and "Connection refused" in str(err):
            log.error('Failed to connect to the DB. Trying again in 10 sec.')
            time.sleep(10)
            init_db(app, retry - 1)
        else:
            raise


class Employee(db.Model):
    __tablename__ = 'employee'
    id: Column[int] = Column(Integer, primary_key=True)
    email: Column[str] = Column(String(256), unique=True, nullable=False)

    @staticmethod
    def to_json(employee: Employee) -> Dict:
        return { 'id': employee.id, 'email': employee.email } if employee else {}
    
    @staticmethod
    def to_json_array(employees: List[Employee]) -> List[Dict]:
        return [Employee.to_json(employee) for employee in employees]

    @staticmethod
    def get_all() -> List[Employee]:
        return Employee.query.all()
    
    @staticmethod
    def delete_all() -> int:
        return Employee.query.delete()

    @staticmethod
    def get_employees(filter) -> List[Employee]:
        return Employee.query.filter(filter).all()
    
    @staticmethod
    def get_employees_by_ids(ids: List[int]) -> List[Employee]:
        return Employee.get_employees(Employee.id.in_(ids))

    @staticmethod
    def get_employee(**filter) -> Employee:
        return Employee.query.filter_by(**filter).first()

    @staticmethod
    def add_employee(email: str) -> Employee:
        try:
            employee = Employee(email=email)
            db.session.add(employee)
            db.session.commit()
            return employee
        except IntegrityError:
            raise Conflict(f"Email {email} already exist")


class WorkHours(db.Model):
    __tablename__ = 'work_hours'
    id = Column(Integer, primary_key=True)
    employee_id: Column[int] = Column(db.Integer, ForeignKey('employee.id'), nullable=False)
    start_work: Column[datetime] = Column(DateTime, default=datetime.utcnow, nullable=False)
    end_work: Column[datetime] = Column(DateTime, nullable=True)
    location: Column[str] = Column(String(256), nullable=False)

    @staticmethod
    def to_json(work_hours: WorkHours) -> Dict:
        if not work_hours:
            return {}
        return {
            'id': work_hours.id,
            'employee_id': work_hours.employee_id,
            'start_work': work_hours.start_work,
            'end_work': work_hours.end_work,
            'location': work_hours.location
        }

    @staticmethod
    def to_json_array(works_hours: List[WorkHours]) -> List[Dict]:
        return [WorkHours.to_json(work_hours) for work_hours in works_hours]

    @staticmethod
    def get_all_employee_works(employee_id: int) -> List[Dict]:
        return WorkHours.query.filter_by(employee_id=employee_id)
    
    @staticmethod
    def delete_all_employee_works(employee_id: int) -> int:
        return WorkHours.query.filter_by(employee_id=employee_id).delete()

    @staticmethod
    def get_last_work_hours(employee_id: int) -> WorkHours:
        return WorkHours.query.filter_by(employee_id=employee_id).order_by(WorkHours.start_work.desc()).first()
    
    @staticmethod
    def get_works_hours_by_time_and_location(_time: datetime, location: str) -> List[WorkHours]:
        filter = and_(
            location == location,
            WorkHours.start_work < _time,
            or_(
                WorkHours.end_work == None,
                WorkHours.end_work < _time
            )
        )
        work_hours = WorkHours.query.filter(filter).all()
        return work_hours
    
    @staticmethod
    def set_start_work(employee_id: int, location: str) -> None:
        work_hours = WorkHours.get_last_work_hours(employee_id)
        if work_hours and work_hours.end_work is None:
            raise BadRequest('There is already opened working hours')
        work_hours = WorkHours(employee_id=employee_id, location=location)
        db.session.add(work_hours)
        db.session.commit()

    @staticmethod
    def set_end_work(employee_id: int) -> None:
        work_hours = WorkHours.get_last_work_hours(employee_id)
        if not work_hours or work_hours.end_work is not None:
            raise BadRequest('There is no open working hours')
        work_hours.end_work = datetime.utcnow()
        db.session.commit()
