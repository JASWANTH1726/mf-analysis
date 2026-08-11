from django.db import models
from django.contrib.auth.models import User

LANGUAGE_CHOICES = [
    ('en', 'English'), ('hi', 'Hindi'), ('te', 'Telugu'), ('ta', 'Tamil'),
    ('kn', 'Kannada'), ('ml', 'Malayalam'), ('mr', 'Marathi'), ('bn', 'Bengali'),
    ('gu', 'Gujarati'), ('pa', 'Punjabi'), ('ur', 'Urdu'), ('or', 'Odia'),
    ('fr', 'French'), ('de', 'German'), ('es', 'Spanish'), ('ar', 'Arabic'),
    ('zh', 'Chinese'), ('ja', 'Japanese'), ('pt', 'Portuguese'), ('ru', 'Russian'),
]

EDITION_CHOICES = [
    ('print', 'Print'), ('digital', 'Digital'), ('epaper', 'E-Paper'),
]

NEWSPAPER_CHOICES = [
    # --- English National ---
    ('times_of_india',      'Times of India'),
    ('the_hindu',           'The Hindu'),
    ('indian_express',      'The Indian Express'),
    ('hindustan_times',     'Hindustan Times'),
    ('deccan_herald',       'Deccan Herald'),
    ('new_indian_express',  'The New Indian Express'),
    ('deccan_chronicle',    'Deccan Chronicle'),
    ('business_standard',   'Business Standard'),
    ('economic_times',      'Economic Times'),
    ('mint',                'Mint'),
    ('hans_india',          'The Hans India'),
    ('tribune',             'The Tribune'),
    ('statesman',           'The Statesman'),
    # --- English International ---
    ('bbc',                 'BBC News'),
    ('reuters',             'Reuters'),
    ('guardian',            'The Guardian'),
    ('new_york_times',      'The New York Times'),
    ('washington_post',     'The Washington Post'),
    ('al_jazeera',          'Al Jazeera'),
    ('bloomberg',           'Bloomberg'),
    ('cnn',                 'CNN'),
    # --- Hindi ---
    ('dainik_jagran',       'Dainik Jagran'),
    ('dainik_bhaskar',      'Dainik Bhaskar'),
    ('amar_ujala',          'Amar Ujala'),
    ('hindustan_hindi',     'Hindustan (Hindi)'),
    ('rajasthan_patrika',   'Rajasthan Patrika'),
    ('navbharat_times',     'Navbharat Times'),
    ('jansatta',            'Jansatta'),
    # --- Telugu ---
    ('eenadu',              'Eenadu'),
    ('sakshi',              'Sakshi'),
    ('andhrajyothy',        'Andhra Jyothy'),
    ('vaartha',             'Vaartha'),
    ('namaste_telangana',   'Namasthe Telangana (NT News)'),
    ('great_andhra',        'Great Andhra'),
    ('telangana_today',     'Telangana Today'),
    ('andhra_headlines',    'Andhra Headlines'),
    # --- Tamil ---
    ('daily_thanthi',       'Dina Thanthi'),
    ('dinamalar',           'Dinamalar'),
    ('dinamani',            'Dinamani'),
    ('maalai_malar',        'Maalai Malar'),
    # --- Kannada ---
    ('vijaya_karnataka',    'Vijaya Karnataka'),
    ('prajavani',           'Prajavani'),
    ('vijayavani',          'Vijayavani'),
    ('udayavani',           'Udayavani'),
    # --- Malayalam ---
    ('malayala_manorama',   'Malayala Manorama'),
    ('mathrubhumi',         'Mathrubhumi'),
    ('deshabhimani',        'Deshabhimani'),
    # --- Marathi ---
    ('lokmat',              'Lokmat'),
    ('maharashtra_times',   'Maharashtra Times'),
    ('pudhari',             'Pudhari'),
    ('sakal',               'Sakal'),
    # --- Bengali ---
    ('anandabazar',         'Anandabazar Patrika'),
    ('bartaman',            'Bartaman Patrika'),
    ('sangbad_pratidin',    'Sangbad Pratidin'),
    ('telegraph_india',     'The Telegraph India'),
    # --- Gujarati ---
    ('gujarat_samachar',    'Gujarat Samachar'),
    ('divya_bhaskar',       'Divya Bhaskar'),
    ('sandesh',             'Sandesh'),
    # --- District/Regional ---
    ('bangalore_mirror',    'Bangalore Mirror'),
]

AREA_CHOICES = [
    # Andhra Pradesh
    ('vizag',                   'Vizag (Visakhapatnam)'),
    ('vizag_gajuwaka',          'Vizag - Gajuwaka'),
    ('vizag_mvp',               'Vizag - MVP Colony'),
    ('vizag_rushikonda',        'Vizag - Rushikonda'),
    ('vijayawada',              'Vijayawada'),
    ('vijayawada_krishnalanka', 'Vijayawada - Krishna Lanka'),
    ('guntur',      'Guntur'),
    ('tirupati',    'Tirupati'),
    ('kurnool',     'Kurnool'),
    ('nellore',     'Nellore'),
    ('rajahmundry', 'Rajahmundry'),
    ('kakinada',    'Kakinada'),
    ('eluru',       'Eluru'),
    ('ongole',      'Ongole'),
    ('kadapa',      'Kadapa'),
    ('anantapur',   'Anantapur'),
    ('srikakulam',  'Srikakulam'),
    ('vizianagaram','Vizianagaram'),
    # Telangana
    ('hyderabad',               'Hyderabad'),
    ('hyderabad_secunderabad',  'Hyderabad - Secunderabad'),
    ('hyderabad_hitech',        'Hyderabad - HiTech City'),
    ('hyderabad_lb_nagar',      'Hyderabad - LB Nagar'),
    ('warangal',    'Warangal'),
    ('karimnagar',  'Karimnagar'),
    ('nizamabad',   'Nizamabad'),
    ('khammam',     'Khammam'),
    ('nalgonda',    'Nalgonda'),
    ('adilabad',    'Adilabad'),
    # Tamil Nadu
    ('chennai',     'Chennai'),
    ('coimbatore',  'Coimbatore'),
    ('madurai',     'Madurai'),
    ('salem',       'Salem'),
    ('trichy',      'Trichy'),
    ('tirunelveli', 'Tirunelveli'),
    ('vellore',     'Vellore'),
    ('erode',       'Erode'),
    # Karnataka
    ('bangalore',   'Bangalore'),
    ('mysore',      'Mysore'),
    ('mangalore',   'Mangalore'),
    ('hubli',       'Hubli-Dharwad'),
    ('belgaum',     'Belagavi (Belgaum)'),
    # Kerala
    ('kochi',               'Kochi'),
    ('thiruvananthapuram',  'Thiruvananthapuram'),
    ('kozhikode',           'Kozhikode'),
    ('thrissur',            'Thrissur'),
    ('kollam',              'Kollam'),
    # Maharashtra
    ('mumbai',      'Mumbai'),
    ('pune',        'Pune'),
    ('nagpur',      'Nagpur'),
    ('nashik',      'Nashik'),
    ('aurangabad',  'Aurangabad'),
    ('solapur',     'Solapur'),
    # Delhi / NCR
    ('delhi',       'New Delhi'),
    ('noida',       'Noida'),
    ('gurgaon',     'Gurgaon'),
    ('faridabad',   'Faridabad'),
    # West Bengal
    ('kolkata',     'Kolkata'),
    ('siliguri',    'Siliguri'),
    # Gujarat
    ('ahmedabad',   'Ahmedabad'),
    ('surat',       'Surat'),
    ('vadodara',    'Vadodara'),
    ('rajkot',      'Rajkot'),
    # Rajasthan
    ('jaipur',      'Jaipur'),
    ('jodhpur',     'Jodhpur'),
    ('udaipur',     'Udaipur'),
    ('kota',        'Kota'),
    # Punjab / Haryana
    ('chandigarh',  'Chandigarh'),
    ('amritsar',    'Amritsar'),
    ('ludhiana',    'Ludhiana'),
    ('jalandhar',   'Jalandhar'),
    ('ambala',      'Ambala'),
    # Uttar Pradesh
    ('lucknow',     'Lucknow'),
    ('kanpur',      'Kanpur'),
    ('varanasi',    'Varanasi'),
    ('agra',        'Agra'),
    ('allahabad',   'Prayagraj (Allahabad)'),
    ('meerut',      'Meerut'),
    ('noida',       'Noida'),
    # Bihar / Jharkhand
    ('patna',       'Patna'),
    ('gaya',        'Gaya'),
    ('ranchi',      'Ranchi'),
    ('jamshedpur',  'Jamshedpur'),
    # Odisha
    ('bhubaneswar', 'Bhubaneswar'),
    ('cuttack',     'Cuttack'),
    # Madhya Pradesh
    ('bhopal',      'Bhopal'),
    ('indore',      'Indore'),
    ('jabalpur',    'Jabalpur'),
    ('gwalior',     'Gwalior'),
    # Assam / Northeast
    ('guwahati',    'Guwahati'),
    # Chhattisgarh
    ('raipur',      'Raipur'),
    # National / International
    ('national',        'National (All India)'),
    ('international',   'International'),
]

class UserPreference(models.Model):
    user      = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preference')
    language  = models.CharField(max_length=5,  choices=LANGUAGE_CHOICES,  default='en')
    edition   = models.CharField(max_length=10, choices=EDITION_CHOICES,   default='digital')
    area      = models.CharField(max_length=30, choices=AREA_CHOICES,      default='national')
    newspaper = models.CharField(max_length=30, choices=NEWSPAPER_CHOICES, default='the_hindu')
    keywords  = models.TextField(blank=True)

    def get_keywords_list(self):
        return [k.strip() for k in self.keywords.split(',') if k.strip()]

    def __str__(self):
        return f"{self.user.username} preferences"
