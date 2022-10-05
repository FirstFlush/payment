
from django import forms
from .models import Account



class RegistrationForm(forms.ModelForm):

    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Enter Password',
        'class':'form-control'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Confirm Password',
        'class':'form-control'
    }))
    
    # first_name = forms.CharField(widget=forms.TextInput(attrs={
    #     'autofocus':'True',
    # }))

    class Meta:
        model = Account
        fields = ['email', 'password']
    
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        # self.fields['first_name'].widget.attrs['placeholder']= 'First name'
        # self.fields['last_name'].widget.attrs['placeholder']= 'Last name'
        # self.fields['phone_number'].widget.attrs['placeholder']= 'Phone number'
        self.fields['email'].widget.attrs['placeholder']= 'Email address'
        for field in self.fields:
            self.fields[field].widget.attrs['class']= 'form-control'


    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        print(password)

        if password != confirm_password:
            raise forms.ValidationError('Passwords do not match.')