from browser import document, window

#Code for SideBar and Menu Toggling
def hide_side_bar(ev):
    document['sidebar'].classList.add('hidden')
    document['smallbar'].classList.remove('hidden')

def show_side_bar(ev):
    document['smallbar'].classList.add('hidden')
    document['sidebar'].classList.remove('hidden')

def _toggle_submenu(menu_id, submenu_id):
    submenu = document[submenu_id]
    arrow = document.getElementById(menu_id).getElementsByTagName('img')[1]
    if 'hidden' in submenu.classList:
        # Showing the submenu
        submenu.classList.remove('hidden')
        # Rotating the arrow
        arrow.style.transform='rotate(270deg)'
    else:
        # Hiding the submenu
        submenu.classList.add('hidden')
        # Rotating the arrow back
        arrow.style.transform='rotate(90deg)'

def toggle_employees_submenu(ev):
    _toggle_submenu("employees-menu", "employees-submenu")

def toggle_attendance_submenu(ev):
    _toggle_submenu("attendance-menu", "attendance-submenu")

def toggle_payroll_submenu(ev):
    _toggle_submenu("payroll-menu", "payroll-submenu")

def toggle_company_submenu(ev):
    _toggle_submenu("company-menu", "company-submenu")

def toggle_banks_submenu(ev):
    _toggle_submenu("banks-menu", "banks-submenu")

def toggle_setting_submenu(ev):
    _toggle_submenu("setting-menu", "setting-submenu")

# Code for opening modal if "save and add button" was clicked
def open_modal():
    jq = window.jQuery
    window['modal'].classList.remove('fade')
    jq('#modal').modal('show')
    window['modal'].classList.add('fade')

# Code for hiding/showing the employee holder account in accounts_list page
def toggle_employee_holder_account_field(ev=None):
    if document['id_account_type'].value == 'company':
        document['id_account_employee_holder'].parentNode.getElementsByTagName('label')[0].style.display = 'none'
        document['id_account_employee_holder'].style.display = 'none'
        document['id_account_employee_holder'].value = ''
    elif document['id_account_type'].value == 'employee':
        document['id_account_employee_holder'].parentNode.getElementsByTagName('label')[0].style.display = 'block'
        document['id_account_employee_holder'].style.display = 'block'

# Code for showing hidden subforms in the formset
def hide_empty_forms():
    i = 2
    while True:
        id = 'form-' + str(i)
        if document.getElementById(id):
            input_field = document.getElementById(id).getElementsByClassName('form-control')[1]
            if not input_field.value:
                document.getElementById(id).style.display = 'none'
            i += 1
        else:
            break

def add_new_form(ev):
    i = 2
    while True:
        id = 'form-' + str(i)
        if document.getElementById(id).style.display == 'none':
            document.getElementById(id).style.display = 'block'
            break
        else:
            i += 1

def main():
    if document.getElementById('id_account_type'):
        toggle_employee_holder_account_field()
        document['id_account_type'].bind('change', toggle_employee_holder_account_field)

    if document.getElementById('open-modal'):
        open_modal()

    if document.getElementById('formset'):
        hide_empty_forms()
        document['add-row-btn'].bind('click', add_new_form)

    document['collapse-btn'].bind('click', hide_side_bar)
    document['show'].bind('click', show_side_bar)
    document['employees-menu'].bind('click', toggle_employees_submenu)
    document['attendance-menu'].bind('click', toggle_attendance_submenu)
    document['payroll-menu'].bind('click', toggle_payroll_submenu)
    document['company-menu'].bind('click', toggle_company_submenu)
    document['banks-menu'].bind('click', toggle_banks_submenu)
    document['setting-menu'].bind('click', toggle_setting_submenu)

if __name__ == '__main__':
    main()
