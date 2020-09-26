Feature: Test email flows

    Scenario: employees get a quarantine email while he still working
        Given there are two employees working right now
        When one of the employees inform to be sick
        Then the other employee should get an email for quarantine
