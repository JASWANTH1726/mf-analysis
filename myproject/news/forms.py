from django import forms
from django.contrib.auth.models import User
from .models import UserPreference, LANGUAGE_CHOICES, EDITION_CHOICES, AREA_CHOICES, NEWSPAPER_CHOICES

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

# Group newspapers by language for grouped <optgroup> display
NEWSPAPER_GROUPED = [
    ('── English National ──', [
        ('times_of_india','Times of India'), ('the_hindu','The Hindu'),
        ('indian_express','The Indian Express'), ('hindustan_times','Hindustan Times'),
        ('deccan_herald','Deccan Herald'), ('new_indian_express','The New Indian Express'),
        ('deccan_chronicle','Deccan Chronicle'), ('business_standard','Business Standard'),
        ('economic_times','Economic Times'), ('mint','Mint'),
        ('hans_india','The Hans India'), ('tribune','The Tribune'), ('statesman','The Statesman'),
    ]),
    ('── English International ──', [
        ('bbc','BBC News'), ('reuters','Reuters'), ('guardian','The Guardian'),
        ('new_york_times','The New York Times'), ('washington_post','The Washington Post'),
        ('al_jazeera','Al Jazeera'), ('bloomberg','Bloomberg'), ('cnn','CNN'),
    ]),
    ('── Hindi ──', [
        ('dainik_jagran','Dainik Jagran'), ('dainik_bhaskar','Dainik Bhaskar'),
        ('amar_ujala','Amar Ujala'), ('hindustan_hindi','Hindustan (Hindi)'),
        ('rajasthan_patrika','Rajasthan Patrika'), ('navbharat_times','Navbharat Times'),
        ('jansatta','Jansatta'),
    ]),
    ('── Telugu ──', [
        ('eenadu','Eenadu'), ('sakshi','Sakshi'), ('andhrajyothy','Andhra Jyothy'),
        ('vaartha','Vaartha'), ('namaste_telangana','Namasthe Telangana'),
        ('great_andhra','Great Andhra'), ('telangana_today','Telangana Today'),
        ('andhra_headlines','Andhra Headlines'),
    ]),
    ('── Tamil ──', [
        ('daily_thanthi','Dina Thanthi'), ('dinamalar','Dinamalar'),
        ('dinamani','Dinamani'), ('maalai_malar','Maalai Malar'),
    ]),
    ('── Kannada ──', [
        ('vijaya_karnataka','Vijaya Karnataka'), ('prajavani','Prajavani'),
        ('vijayavani','Vijayavani'), ('udayavani','Udayavani'),
    ]),
    ('── Malayalam ──', [
        ('malayala_manorama','Malayala Manorama'), ('mathrubhumi','Mathrubhumi'),
        ('deshabhimani','Deshabhimani'),
    ]),
    ('── Marathi ──', [
        ('lokmat','Lokmat'), ('maharashtra_times','Maharashtra Times'),
        ('pudhari','Pudhari'), ('sakal','Sakal'),
    ]),
    ('── Bengali ──', [
        ('anandabazar','Anandabazar Patrika'), ('bartaman','Bartaman Patrika'),
        ('sangbad_pratidin','Sangbad Pratidin'), ('telegraph_india','The Telegraph India'),
    ]),
    ('── Gujarati ──', [
        ('gujarat_samachar','Gujarat Samachar'), ('divya_bhaskar','Divya Bhaskar'),
        ('sandesh','Sandesh'),
    ]),
    ('── District / Regional ──', [
        ('bangalore_mirror','Bangalore Mirror'),
    ]),
]

class NewsFilterForm(forms.Form):
    language  = forms.ChoiceField(choices=LANGUAGE_CHOICES, required=False)
    edition   = forms.ChoiceField(choices=EDITION_CHOICES, required=False)
    area      = forms.ChoiceField(choices=AREA_CHOICES, required=False)
    newspaper = forms.ChoiceField(
        choices=[('', 'All Newspapers')] + [(k, v) for grp, items in NEWSPAPER_GROUPED for k, v in items],
        required=False
    )
    date         = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    keywords     = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'e.g. politics, sports'}))
    save_keywords = forms.BooleanField(required=False, label='Save my preferences')
