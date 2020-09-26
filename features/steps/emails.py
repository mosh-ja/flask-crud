from behave import *
import time, random, requests, logging

log = logging.getLogger(__name__)

SERVER = 'http://localhost:5000'

sick_user = None
expected_user = None
sick_id = None
respond_emails = []

def post(url):
    response = requests.post(f"{SERVER}/{url}")
    log.info(f"POST {url} return: {response.status_code}, {response.content}")
    assert response.status_code == 200
    return response.json()

@given('there are two employees working right now')
def there_are_two_employees_working_right_now(context):
    global sick_user, expected_user, sick_id
    sick_user = f"sick_user-{time.time()}-{random.randint(1, 1000)}"
    expected_user = f"expected_user-{time.time()}-{random.randint(1, 1000)}"
    
    sick_id = post(f"/employee?email={sick_user}")['id']
    expected_id = post(f"/employee?email={expected_user}")['id']

    post(f"/employee/{sick_id}/work/start")
    post(f"/employee/{expected_id}/work/start")

@when('one of the employees inform to be sick')
def one_ofthe_employees_inform_to_be_sick(context):
    global sick_id, respond_emails
    respond_emails = post(f"/employee/{sick_id}/sick")['emails']

@then('the other employee should get an email for quarantine')
def the_other_employee_should_get_email_for_quarantine(context):
    global sick_user, expected_user, respond_emails
    assert sick_user not in respond_emails
    assert expected_user in respond_emails