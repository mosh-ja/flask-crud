from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import Integer, String, DateTime, Column, ForeignKey, exc

from datetime import datetime
from common import BadRequest

db = SQLAlchemy()


def migrate_db(app):
    db.create_all(app=app)
    Migrate(app, db)


class Employee(db.Model):
    __tablename__ = 'employee'
    id = Column(Integer, primary_key=True)
    email = Column(String(256), unique=True)

    @staticmethod
    def to_json(employee):
        return { 'id': employee.id, 'email': employee.email } if employee else {}

    @staticmethod
    def get_all():
        employees = Employee.query.all()
        employees = [Employee.to_json(employee) for employee in employees]
        return { 'employees': employees }

    @staticmethod
    def get_employee_by_email(email):
        employee = Employee.query.filter_by(email=email).first()
        return Employee.to_json(employee)

    @staticmethod
    def get_employee_by_id(id):
        employee = Employee.query.filter_by(id=id).first()
        return Employee.to_json(employee)
    
    @staticmethod
    def add_employee(email):
        try:
            employee = Employee(email=email)
            db.session.add(employee)
            db.session.commit()
            return Employee.to_json(employee)
        except exc.IntegrityError:
            db.session.rollback()
            raise BadRequest('Email already exist')

class WorkHours(db.Model):
    __tablename__ = 'work_hours'
    id = Column(Integer, primary_key=True)
    employee_id = Column(db.Integer, ForeignKey('employee.id'), nullable=False)
    start = Column(DateTime, default=datetime.utcnow, nullable=False)
    end = Column(DateTime, nullable=True)

    @staticmethod
    def to_json(work_hours):
        if not work_hours:
            return {}
        return { 'id': work_hours.id,
            'employee_id': work_hours.employee_id,
            'start': work_hours.start,
            'end': work_hours.end
        }

    @staticmethod
    def get_all():
        works_hours = WorkHours.query.all()
        work_hours = [WorkHours.to_json(work_hours) for work_hours in works_hours]
        return { 'works_hours': work_hours }

    @staticmethod
    def get_last_work_hours(employee_id):
        work_hours = WorkHours.query.filter_by(employee_id=id).order_by('id desc').first()
        return WorkHours.to_json(work_hours)
    
    @staticmethod
    def start_work(employee_id):
        work_hours = WorkHours.get_last_work_hours(employee_id)
        if work_hours is not None and work_hours.end is None:
            raise BadRequest('There is already opened working hours')
        work_hours = WorkHours(employee_id=employee_id)
        db.session.add(work_hours)
        db.session.commit()

    @staticmethod
    def end_work(employee_id):
        work_hours = WorkHours.get_last_work_hours(employee_id)
        if work_hours is None or work_hours.end is not None:
            raise BadRequest('There is no open working hours')
        work_hours.end = datetime.utcnow
        db.session.commit()

