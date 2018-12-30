from django import forms
from home.models import Requester

class RequesterForm(forms.ModelForm):
    class Meta:
        model = Requester
        fields = ('name', 'email')
        labels = {
            'name': 'الاسم*',
            'email': 'البريد الالكترونى*',
        }
        error_messages = {
            'email': {
                'unique':'هذا البريد الالكترونى مسجل لدينا من قبل !',
                }
            }