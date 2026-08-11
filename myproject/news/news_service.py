import requests
import xml.etree.ElementTree as ET
from django.conf import settings

NEWS_API_KEY = getattr(settings, 'NEWS_API_KEY', '')
NEWS_API_URL = 'https://newsapi.org/v2/everything'

LANGUAGE_MAP = {
    'en': 'en', 'hi': 'hi', 'fr': 'fr', 'de': 'de', 'es': 'es',
    'ar': 'ar', 'zh': 'zh', 'ja': 'ja', 'pt': 'pt', 'ru': 'ru',
    # Regional Indian — NewsAPI uses 'en' as fallback
    'te': 'en', 'ta': 'en', 'kn': 'en', 'ml': 'en',
    'mr': 'en', 'bn': 'en', 'gu': 'en', 'pa': 'en', 'ur': 'ur', 'or': 'en',
}

AREA_QUERY_MAP = {
    'vizag': 'Visakhapatnam', 'vizag_gajuwaka': 'Visakhapatnam Gajuwaka',
    'vizag_mvp': 'Visakhapatnam MVP Colony', 'vizag_rushikonda': 'Visakhapatnam Rushikonda',
    'vijayawada': 'Vijayawada', 'vijayawada_krishnalanka': 'Vijayawada Krishna Lanka',
    'guntur': 'Guntur', 'tirupati': 'Tirupati', 'kurnool': 'Kurnool',
    'nellore': 'Nellore', 'rajahmundry': 'Rajahmundry', 'kakinada': 'Kakinada',
    'eluru': 'Eluru', 'ongole': 'Ongole', 'kadapa': 'Kadapa', 'anantapur': 'Anantapur',
    'srikakulam': 'Srikakulam', 'vizianagaram': 'Vizianagaram',
    'hyderabad': 'Hyderabad', 'hyderabad_secunderabad': 'Secunderabad',
    'hyderabad_hitech': 'HiTech City Hyderabad', 'hyderabad_lb_nagar': 'LB Nagar Hyderabad',
    'warangal': 'Warangal', 'karimnagar': 'Karimnagar', 'nizamabad': 'Nizamabad',
    'khammam': 'Khammam', 'nalgonda': 'Nalgonda', 'adilabad': 'Adilabad',
    'chennai': 'Chennai', 'coimbatore': 'Coimbatore', 'madurai': 'Madurai',
    'salem': 'Salem', 'trichy': 'Trichy', 'tirunelveli': 'Tirunelveli',
    'vellore': 'Vellore', 'erode': 'Erode',
    'bangalore': 'Bangalore', 'mysore': 'Mysore', 'mangalore': 'Mangalore',
    'hubli': 'Hubli', 'belgaum': 'Belagavi',
    'kochi': 'Kochi', 'thiruvananthapuram': 'Thiruvananthapuram',
    'kozhikode': 'Kozhikode', 'thrissur': 'Thrissur', 'kollam': 'Kollam',
    'mumbai': 'Mumbai', 'pune': 'Pune', 'nagpur': 'Nagpur',
    'nashik': 'Nashik', 'aurangabad': 'Aurangabad', 'solapur': 'Solapur',
    'delhi': 'New Delhi', 'noida': 'Noida', 'gurgaon': 'Gurgaon', 'faridabad': 'Faridabad',
    'kolkata': 'Kolkata', 'siliguri': 'Siliguri',
    'ahmedabad': 'Ahmedabad', 'surat': 'Surat', 'vadodara': 'Vadodara', 'rajkot': 'Rajkot',
    'jaipur': 'Jaipur', 'jodhpur': 'Jodhpur', 'udaipur': 'Udaipur', 'kota': 'Kota',
    'chandigarh': 'Chandigarh', 'amritsar': 'Amritsar', 'ludhiana': 'Ludhiana',
    'jalandhar': 'Jalandhar', 'ambala': 'Ambala',
    'lucknow': 'Lucknow', 'kanpur': 'Kanpur', 'varanasi': 'Varanasi',
    'agra': 'Agra', 'allahabad': 'Prayagraj', 'meerut': 'Meerut',
    'patna': 'Patna', 'gaya': 'Gaya', 'ranchi': 'Ranchi', 'jamshedpur': 'Jamshedpur',
    'bhubaneswar': 'Bhubaneswar', 'cuttack': 'Cuttack',
    'bhopal': 'Bhopal', 'indore': 'Indore', 'jabalpur': 'Jabalpur', 'gwalior': 'Gwalior',
    'guwahati': 'Guwahati', 'raipur': 'Raipur',
    'national': 'India', 'international': 'World',
}

# newspaper key -> (display name, domain, rss_url)
NEWSPAPER_DB = {
    # English National
    'times_of_india':     ('Times of India',            'timesofindia.indiatimes.com',  'https://timesofindia.indiatimes.com/rssfeedstopstories.cms'),
    'the_hindu':          ('The Hindu',                 'thehindu.com',                 'https://www.thehindu.com/feeder/default.rss'),
    'indian_express':     ('The Indian Express',        'indianexpress.com',            'https://indianexpress.com/feed/'),
    'hindustan_times':    ('Hindustan Times',           'hindustantimes.com',           'https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml'),
    'deccan_herald':      ('Deccan Herald',             'deccanherald.com',             'https://www.deccanherald.com/rss-feed/national.rss'),
    'new_indian_express': ('The New Indian Express',    'newindianexpress.com',         'https://www.newindianexpress.com/rss/googlenews/nation.xml'),
    'deccan_chronicle':   ('Deccan Chronicle',          'deccanchronicle.com',          'https://www.deccanchronicle.com/rss_feed/'),
    'business_standard':  ('Business Standard',         'business-standard.com',        'https://www.business-standard.com/rss/latest.rss'),
    'economic_times':     ('Economic Times',            'economictimes.indiatimes.com', 'https://economictimes.indiatimes.com/rssfeedsdefault.cms'),
    'mint':               ('Mint',                      'livemint.com',                 'https://www.livemint.com/rss/news'),
    'hans_india':         ('The Hans India',            'thehansindia.com',             'https://www.thehansindia.com/rss/'),
    'tribune':            ('The Tribune',               'tribuneindia.com',             'https://www.tribuneindia.com/rss'),
    'statesman':          ('The Statesman',             'thestatesman.com',             'https://www.thestatesman.com/feed'),
    # English International
    'bbc':                ('BBC News',                  'bbc.com',                      'https://feeds.bbci.co.uk/news/india/rss.xml'),
    'reuters':            ('Reuters',                   'reuters.com',                  'https://feeds.reuters.com/reuters/INtopNews'),
    'guardian':           ('The Guardian',              'theguardian.com',              'https://www.theguardian.com/world/rss'),
    'new_york_times':     ('The New York Times',        'nytimes.com',                  'https://rss.nytimes.com/services/xml/rss/nyt/World.xml'),
    'washington_post':    ('The Washington Post',       'washingtonpost.com',           'https://feeds.washingtonpost.com/rss/world'),
    'al_jazeera':         ('Al Jazeera',                'aljazeera.com',                'https://www.aljazeera.com/xml/rss/all.xml'),
    'bloomberg':          ('Bloomberg',                 'bloomberg.com',                None),
    'cnn':                ('CNN',                       'cnn.com',                      'http://rss.cnn.com/rss/edition.rss'),
    # Hindi
    'dainik_jagran':      ('Dainik Jagran',             'jagran.com',                   'https://www.jagran.com/rss/news-national.xml'),
    'dainik_bhaskar':     ('Dainik Bhaskar',            'bhaskar.com',                  'https://www.bhaskar.com/rss-feed/8/'),
    'amar_ujala':         ('Amar Ujala',                'amarujala.com',                'https://www.amarujala.com/rss/india-news.xml'),
    'hindustan_hindi':    ('Hindustan (Hindi)',         'livehindustan.com',            'https://feed.livehindustan.com/rss/3127'),
    'rajasthan_patrika':  ('Rajasthan Patrika',         'patrika.com',                  'https://api.patrika.com/rss/india-news'),
    'navbharat_times':    ('Navbharat Times',           'navbharattimes.indiatimes.com','https://navbharattimes.indiatimes.com/rssfeedsdefault.cms'),
    'jansatta':           ('Jansatta',                  'jansatta.com',                 'https://www.jansatta.com/feed/'),
    # Telugu
    'eenadu':             ('Eenadu',                    'eenadu.net',                   'https://www.eenadu.net/rss/feeds/telugu-news.xml'),
    'sakshi':             ('Sakshi',                    'sakshi.com',                   'https://www.sakshi.com/rss/feeds/news.xml'),
    'andhrajyothy':       ('Andhra Jyothy',             'andhrajyothy.com',             'https://www.andhrajyothy.com/rss/feeds/topnews.xml'),
    'vaartha':            ('Vaartha',                   'vaartha.com',                  None),
    'namaste_telangana':  ('Namasthe Telangana',        'ntnews.com',                   'https://www.ntnews.com/rss/feeds/news.xml'),
    'great_andhra':       ('Great Andhra',              'greatandhra.com',              'https://www.greatandhra.com/rss/news.xml'),
    'telangana_today':    ('Telangana Today',           'telanganatoday.com',           'https://telanganatoday.com/feed'),
    'andhra_headlines':   ('Andhra Headlines',          'andhraheadlines.com',          'https://andhraheadlines.com/feed/'),
    # Tamil
    'daily_thanthi':      ('Dina Thanthi',              'dailythanthi.com',             'https://www.dailythanthi.com/rss/feeds/tamilnews.xml'),
    'dinamalar':          ('Dinamalar',                 'dinamalar.com',                'https://www.dinamalar.com/rss_news.asp'),
    'dinamani':           ('Dinamani',                  'dinamani.com',                 'https://www.dinamani.com/feeds/?cat='),
    'maalai_malar':       ('Maalai Malar',              'maalaimalar.com',              None),
    # Kannada
    'vijaya_karnataka':   ('Vijaya Karnataka',          'vijaykarnataka.com',           'https://vijaykarnataka.com/rssfeeds/topstories.cms'),
    'prajavani':          ('Prajavani',                 'prajavani.net',                'https://www.prajavani.net/feed/'),
    'vijayavani':         ('Vijayavani',                'vijayavani.net',               'https://www.vijayavani.net/feed/'),
    'udayavani':          ('Udayavani',                 'udayavani.com',                'https://www.udayavani.com/feed'),
    # Malayalam
    'malayala_manorama':  ('Malayala Manorama',         'manoramaonline.com',           'https://www.manoramaonline.com/news/latest-news.rss.xml'),
    'mathrubhumi':        ('Mathrubhumi',               'mathrubhumi.com',              'https://www.mathrubhumi.com/rss/feeds/mathrubhumi-news.xml'),
    'deshabhimani':       ('Deshabhimani',              'deshabhimani.com',             'https://www.deshabhimani.com/rss'),
    # Marathi
    'lokmat':             ('Lokmat',                    'lokmat.com',                   'https://www.lokmat.com/rss/'),
    'maharashtra_times':  ('Maharashtra Times',         'maharashtratimes.com',         'https://maharashtratimes.com/rssfeedsdefault.cms'),
    'pudhari':            ('Pudhari',                   'pudhari.news',                 'https://www.pudhari.news/feed/'),
    'sakal':              ('Sakal',                     'esakal.com',                   'https://www.esakal.com/rss/feeds/topnews.xml'),
    # Bengali
    'anandabazar':        ('Anandabazar Patrika',       'anandabazar.com',              'https://www.anandabazar.com/rss/desh.xml'),
    'bartaman':           ('Bartaman Patrika',          'bartamanpatrika.com',          None),
    'sangbad_pratidin':   ('Sangbad Pratidin',          'sangbadpratidin.in',           'https://www.sangbadpratidin.in/feed/'),
    'telegraph_india':    ('The Telegraph India',       'telegraphindia.com',           'https://www.telegraphindia.com/rss-feed/rss.xml'),
    # Gujarati
    'gujarat_samachar':   ('Gujarat Samachar',          'gujaratsamachar.com',          'https://www.gujaratsamachar.com/rss/topnews.xml'),
    'divya_bhaskar':      ('Divya Bhaskar',             'divyabhaskar.co.in',           'https://www.divyabhaskar.co.in/rss-feed/1221/'),
    'sandesh':            ('Sandesh',                   'sandesh.com',                  'https://sandesh.com/feed/'),
    # District
    'bangalore_mirror':   ('Bangalore Mirror',          'bangaloremirror.indiatimes.com','https://bangaloremirror.indiatimes.com/rssfeeds/topstories.cms'),
}

NEWSPAPER_NAME_MAP  = {k: v[0] for k, v in NEWSPAPER_DB.items()}
NEWSPAPER_DOMAIN_MAP = {k: v[1] for k, v in NEWSPAPER_DB.items()}
NEWSPAPER_RSS_MAP   = {k: v[2] for k, v in NEWSPAPER_DB.items()}


def _parse_rss(rss_url, max_items=20):
    """Fetch and parse RSS feed, return list of article dicts."""
    try:
        resp = requests.get(rss_url, timeout=8, headers={'User-Agent': 'Mozilla/5.0'})
        root = ET.fromstring(resp.content)
        channel = root.find('channel')
        items = (channel or root).findall('item')
        articles = []
        for item in items[:max_items]:
            def _t(tag):
                el = item.find(tag)
                return el.text.strip() if el is not None and el.text else ''
            # try to get image from media:content or enclosure
            img = ''
            media = item.find('{http://search.yahoo.com/mrss/}content')
            if media is not None:
                img = media.attrib.get('url', '')
            if not img:
                enc = item.find('enclosure')
                if enc is not None:
                    img = enc.attrib.get('url', '')
            articles.append({
                'title':        _t('title'),
                'description':  _t('description'),
                'url':          _t('link'),
                'urlToImage':   img,
                'publishedAt':  _t('pubDate'),
                'source':       {'name': ''},
                'author':       '',
                '_from_rss':    True,
            })
        return articles
    except Exception:
        return []


def fetch_news(query='India', language='en', from_date=None, page_size=20, domains=None):
    api_lang = LANGUAGE_MAP.get(language, 'en')
    params = {
        'q': query, 'language': api_lang,
        'sortBy': 'publishedAt', 'pageSize': page_size, 'apiKey': NEWS_API_KEY,
    }
    if from_date:
        params['from'] = str(from_date)
    if domains:
        params['domains'] = domains
    try:
        resp = requests.get(NEWS_API_URL, params=params, timeout=10)
        data = resp.json()
        return data.get('articles', [])
    except Exception:
        return []


def fetch_by_newspaper(newspaper, area, language='en', from_date=None):
    rss_url = NEWSPAPER_RSS_MAP.get(newspaper)
    domain  = NEWSPAPER_DOMAIN_MAP.get(newspaper)
    area_term = AREA_QUERY_MAP.get(area, 'India')
    name = NEWSPAPER_NAME_MAP.get(newspaper, '')

    # 1. Try RSS feed first (most reliable for regional papers)
    if rss_url:
        articles = _parse_rss(rss_url)
        if articles:
            for a in articles:
                a['source']['name'] = name
            return articles

    # 2. Fallback: NewsAPI domain search
    if domain:
        articles = fetch_news(query=area_term, language=language, from_date=from_date,
                              page_size=20, domains=domain)
        if articles:
            return articles

    # 3. Final fallback: general area search
    return fetch_news(query=f"{name} {area_term}", language=language,
                      from_date=from_date, page_size=20)


def fetch_recommendations(keywords, area, language='en'):
    area_term = AREA_QUERY_MAP.get(area, 'India')
    keyword_str = ' OR '.join(keywords[:5]) if keywords else area_term
    query = f"({keyword_str}) AND {area_term}"
    return fetch_news(query=query, language=language, page_size=10)
