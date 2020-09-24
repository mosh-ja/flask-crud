import logging
from flask import Blueprint, request
from db import Employee, WorkHours

log = logging.getLogger(__name__)

service  = Blueprint('service', __name__)


@service.route('/employees', methods=['GET'])
def get_employees():
    employees = Employee.get_all()
    return employees

@service.route('/employee', methods=['GET'])
def get_employee():
    email = request.args.get('email')
    if email is None:
        raise BadRequest('Missing email')
    employee = Employee.get_employee_by_email(email)
    return employee

@service.route('/employee', methods=['POST'])
def add_employee():
    email = request.args.get('email')
    if email is None:
        raise BadRequest('Missing email')
    return Employee.add_employee(email)



@service.route('/works', methods=['GET'])
def get_works_hours():
    works_hours = WorkHours.get_all()
    return works_hours

@service.route('/work/start', methods=['POST'])
def start_work():
    email = request.args.get('email')
    if email is None:
        raise BadRequest('Missing email')
    employee = Employee.get_employee_by_email(email)
    if employee is None:
        raise BadRequest('Bad email')
    WorkHours.start_work(employee['id'])


@service.route('/work/end', methods=['POST'])
def end_work():
    email = request.args.get('email')
    if email is None:
        raise BadRequest('Missing email')
    employee = Employee.get_employee_by_email(email)
    if employee is None:
        raise BadRequest('Bad email')
    WorkHours.end_work(employee['id'])