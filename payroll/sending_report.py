# Helper class to create a report for payslip sending
class SendingReport:
    def __init__(self, employee_number, name, email, status=None, reason=None):
        self.employee_number = employee_number
        self.name = name
        self.email = email
        self.status = status
        self.reason = reason
