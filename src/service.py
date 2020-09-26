import logging
from datetime import datetime

from flask import Blueprint, request
from werkzeug.exceptions import BadRequest, NotFound

from db import Employee, WorkHours


log = logging.getLogger(__name__)
service  = Blueprint('service', __name__)


@service.route('/employees', methods=['GET'])
def get_employees():
    return { 'employees': Employee.to_json_array(Employee.get_all()) }

@service.route('/employee', methods=['GET'])
def get_employee_by_email():
    email = request.args.get('email')
    if email is None:
        raise BadRequest('email query param is missing')
    employee = Employee.get_employee(email=email)
    if not employee:
        raise NotFound(f"Email {email} not found")
    return Employee.to_json(employee)

@service.route('/employee', methods=['POST'])
def add_employee():
    email = request.args.get('email')
    if email is None:
        raise BadRequest('email query param is missing')
    return Employee.to_json(Employee.add_employee(email))


def verify_employee_exists(id):
    if not Employee.get_employee(id=id):
        raise NotFound(f"Employee {id} not found")

@service.route('/employee/<employee_id>/works', methods=['GET'])
def get_works_hours(employee_id):
    verify_employee_exists(employee_id)
    return WorkHours.to_json_array(WorkHours.get_all_employee_works(employee_id))

@service.route('/employee/<employee_id>/works', methods=['DELETE'])
def delete_works_hours(employee_id):
    verify_employee_exists(employee_id)
    deleted = WorkHours.delete_all_employee_works(employee_id)
    return { 'deleted': deleted }

def get_location():
    return request.args.get('location') if request.args.get('location') else 'Office'

@service.route('/employee/<employee_id>/work/start', methods=['POST'])
def start_work(employee_id):
    verify_employee_exists(employee_id)
    WorkHours.set_start_work(employee_id, get_location())
    return {}

@service.route('/employee/<employee_id>/work/end', methods=['POST'])
def end_work(employee_id):
    verify_employee_exists(employee_id)
    WorkHours.set_end_work(employee_id)
    return {}


@service.route('/employee/<employee_id>/sick', methods=['POST'])
def sick_employee(employee_id):
    verify_employee_exists(employee_id)
    works_hors = WorkHours.get_works_hours_by_time_and_location(datetime.utcnow(), get_location())
    ids = [work_hors.employee_id for work_hors in works_hors]
    employee_id = int(employee_id)
    if employee_id in ids:
        ids.remove(employee_id)
    employees = Employee.get_employees_by_ids(ids)
    emails = [employee.email for employee in employees]
    if len(emails) > 0:
        log.info(f"TODO: Email to {emails} that they need to be quarantine")
    return { 'emails': emails }