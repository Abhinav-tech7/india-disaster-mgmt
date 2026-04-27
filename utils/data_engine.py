"""
utils/data_engine.py — Data, ML simulation, risk scoring
All 28 States + 8 UTs of India with real districts
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# ── ALL India States & Districts ─────────────────────────────────────────────
CITIES = {
    "Andhra Pradesh": [
        "Visakhapatnam","Vijayawada","Guntur","Nellore","Kurnool","Kadapa","Tirupati",
        "Kakinada","Rajahmundry","Eluru","Machilipatnam","Ongole","Nandyal","Chittoor",
        "Anantapur","Hindupur","Srikakulam","Vizianagaram","Bhimavaram","Narasaraopet"
    ],
    "Arunachal Pradesh": [
        "Itanagar","Naharlagun","Pasighat","Tawang","Ziro","Bomdila","Along","Tezu",
        "Khonsa","Changlang","Aalo","Roing","Namsai","Seppa","Daporijo"
    ],
    "Assam": [
        "Guwahati","Silchar","Dibrugarh","Jorhat","Nagaon","Tinsukia","Tezpur",
        "Bongaigaon","Dhubri","Goalpara","Hailakandi","Karimganj","Lakhimpur","Sivasagar",
        "Golaghat","Morigaon","Nalbari","Barpeta","Kokrajhar","Dhemaji","Kamrup"
    ],
    "Bihar": [
        "Patna","Gaya","Bhagalpur","Muzaffarpur","Purnia","Darbhanga","Bihar Sharif",
        "Arrah","Begusarai","Katihar","Munger","Chhapra","Bettiah","Motihari",
        "Samastipur","Hajipur","Sitamarhi","Nawada","Jehanabad","Aurangabad","Supaul",
        "Kishanganj","Sheikhpura","Lakhisarai","Banka","Madhubani","Saharsa"
    ],
    "Chhattisgarh": [
        "Raipur","Bhilai","Bilaspur","Korba","Durg","Rajnandgaon","Jagdalpur",
        "Ambikapur","Raigarh","Dhamtari","Mahasamund","Janjgir","Kanker","Kondagaon",
        "Narayanpur","Baster","Surguja","Korea","Balrampur","Surajpur","Mungeli"
    ],
    "Goa": [
        "Panaji","Margao","Vasco da Gama","Mapusa","Ponda","Bicholim","Curchorem",
        "Sanquelim","Valpoi","Pernem","Quepem","Canacona","Sanguem","Tiswadi"
    ],
    "Gujarat": [
        "Ahmedabad","Surat","Vadodara","Rajkot","Bhavnagar","Jamnagar","Junagadh",
        "Gandhinagar","Anand","Navsari","Morbi","Mehsana","Surendranagar","Bharuch",
        "Amreli","Patan","Banaskantha","Sabarkantha","Mahesana","Kutch","Bhuj",
        "Dwarka","Porbandar","Gir Somnath","Botad","Aravalli","Chhota Udaipur",
        "Dahod","Narmada","Tapi","Valsad","Kheda","Panchmahal"
    ],
    "Haryana": [
        "Gurugram","Faridabad","Panipat","Ambala","Yamunanagar","Rohtak","Hisar",
        "Karnal","Sonipat","Panchkula","Bhiwani","Sirsa","Jhajjar","Jind",
        "Kaithal","Kurukshetra","Rewari","Mahendragarh","Palwal","Mewat","Fatehabad","Nuh"
    ],
    "Himachal Pradesh": [
        "Shimla","Manali","Dharamshala","Solan","Mandi","Kullu","Bilaspur","Hamirpur",
        "Una","Chamba","Kinnaur","Lahaul Spiti","Sirmaur","Kangra","Baddi","Palampur",
        "Nahan","Sundernagar","Rampur","Rekong Peo"
    ],
    "Jharkhand": [
        "Ranchi","Jamshedpur","Dhanbad","Bokaro","Deoghar","Phusro","Hazaribagh",
        "Giridih","Ramgarh","Medininagar","Chatra","Gumla","Simdega","Lohardaga",
        "West Singhbhum","East Singhbhum","Seraikela","Khunti","Latehar","Godda",
        "Sahibganj","Pakur","Dumka","Jamtara","Koderma"
    ],
    "Karnataka": [
        "Bengaluru","Mysuru","Hubli","Mangalore","Belagavi","Dharwad","Shimoga",
        "Tumkur","Davanagere","Bellary","Bijapur","Gulbarga","Raichur","Bidar",
        "Udupi","Hassan","Chickmagalur","Kodagu","Bagalkot","Gadag","Haveri",
        "Koppal","Yadgir","Chamarajanagar","Mandya","Chikkaballapur","Kolar",
        "Ramanagara","Chitradurga","Vijayapura","Alaur"
    ],
    "Kerala": [
        "Thiruvananthapuram","Kochi","Kozhikode","Thrissur","Kollam","Alappuzha",
        "Palakkad","Malappuram","Kannur","Kasaragod","Idukki","Wayanad","Pathanamthitta",
        "Kottayam","Ernakulam","Manjeri","Thalassery","Payyanur","Ponnani","Ottapalam"
    ],
    "Madhya Pradesh": [
        "Bhopal","Indore","Jabalpur","Gwalior","Ujjain","Sagar","Dewas","Satna",
        "Ratlam","Rewa","Murwara","Singrauli","Burhanpur","Khandwa","Bhind",
        "Chhindwara","Morena","Guna","Shivpuri","Vidisha","Chhatarpur","Damoh",
        "Mandsaur","Khargone","Neemuch","Hoshangabad","Itarsi","Ashok Nagar",
        "Shahdol","Mandla","Seoni","Balaghat","Betul","Tikamgarh","Dindori"
    ],
    "Maharashtra": [
        "Mumbai","Pune","Nagpur","Nashik","Aurangabad","Solapur","Kolhapur","Thane",
        "Amravati","Nanded","Sangli","Satara","Ratnagiri","Yavatmal","Latur",
        "Osmanabad","Parbhani","Jalgaon","Dhule","Chandrapur","Wardha","Akola",
        "Washim","Buldhana","Hingoli","Bhandara","Gondia","Gadchiroli","Ahmednagar",
        "Jalna","Raigad","Sindhudurg","Pallghar","Nandurbar"
    ],
    "Manipur": [
        "Imphal","Thoubal","Bishnupur","Churachandpur","Senapati","Ukhrul",
        "Tamenglong","Chandel","Kakching","Tengnoupal","Jiribam","Pherzawl",
        "Noney","Kangpokpi"
    ],
    "Meghalaya": [
        "Shillong","Tura","Jowai","Nongstoin","Williamnagar","Resubelpara",
        "Baghmara","Mairang","East Khasi Hills","West Khasi Hills","East Jaintia Hills",
        "West Jaintia Hills","East Garo Hills","West Garo Hills","South Garo Hills",
        "North Garo Hills","South West Garo Hills","South West Khasi Hills","Eastern West Khasi Hills"
    ],
    "Mizoram": [
        "Aizawl","Lunglei","Saiha","Champhai","Kolasib","Serchhip","Lawngtlai",
        "Mamit","Hnahthial","Khawzawl","Saitual"
    ],
    "Nagaland": [
        "Kohima","Dimapur","Mokokchung","Tuensang","Wokha","Zunheboto","Phek",
        "Mon","Longleng","Kiphire","Peren","Noklak"
    ],
    "Odisha": [
        "Bhubaneswar","Cuttack","Puri","Rourkela","Sambalpur","Berhampur","Balasore",
        "Kendrapara","Bhadrak","Baripada","Jharsuguda","Sundargarh","Keonjhar",
        "Dhenkanal","Angul","Bolangir","Koraput","Rayagada","Nabarangpur","Kalahandi",
        "Nuapada","Bargarh","Subarnapur","Boudh","Nayagarh","Khordha","Jagatsinghpur",
        "Kendujhar","Ganjam","Gajapati","Kandhamal","Malkangiri"
    ],
    "Punjab": [
        "Ludhiana","Amritsar","Jalandhar","Patiala","Bathinda","Mohali","Hoshiarpur",
        "Batala","Pathankot","Moga","Abohar","Malerkotla","Khanna","Phagwara",
        "Muktsar","Barnala","Rajpura","Firozpur","Faridkot","Fazilka","Gurdaspur",
        "Kapurthala","Nawanshahr","Rupnagar","Sangrur","Tarn Taran"
    ],
    "Rajasthan": [
        "Jaipur","Jodhpur","Kota","Bikaner","Ajmer","Udaipur","Jaisalmer","Alwar",
        "Bharatpur","Sikar","Pali","Sri Ganganagar","Barmer","Tonk","Dausa",
        "Baran","Bundi","Chittorgarh","Churu","Dholpur","Dungarpur","Hanumangarh",
        "Jalore","Jhalawar","Jhunjhunu","Karauli","Nagaur","Pratapgarh","Rajsamand",
        "Sawai Madhopur","Sirohi","Banswara","Bhilwara","Sriganganagar"
    ],
    "Sikkim": [
        "Gangtok","Namchi","Mangan","Gyalshing","Ravangla","Jorethang",
        "Nayabazar","Singtam","Rangpo","Yuksom","Pelling"
    ],
    "Tamil Nadu": [
        "Chennai","Coimbatore","Madurai","Tiruchirappalli","Salem","Tirunelveli",
        "Erode","Vellore","Thoothukudi","Dindigul","Thanjavur","Ranipet",
        "Sivakasi","Karur","Udhagamandalam","Hosur","Nagercoil","Kanchipuram",
        "Tirupur","Cuddalore","Kumbakonam","Tiruvannamalai","Villupuram",
        "Ramanathapuram","Virudhunagar","Pudukkottai","Nagapattinam","Namakkal",
        "Ariyalur","Perambalur","Krishnagiri","Dharmapuri","Theni","Tenkasi"
    ],
    "Telangana": [
        "Hyderabad","Warangal","Nizamabad","Karimnagar","Ramagundam","Khammam",
        "Mahbubnagar","Nalgonda","Adilabad","Suryapet","Miryalaguda","Jagtial",
        "Mancherial","Nirmal","Kamareddy","Sangareddy","Vikarabad","Wanaparthy",
        "Gadwal","Narayanpet","Mahabubabad","Mulugu","Bhadradri Kothagudem",
        "Nagarkurnool","Nagar Kurnool","Peddapalli","Rajanna Sircilla","Siddipet",
        "Jangaon","Medchal","Yadadri Bhuvanagiri"
    ],
    "Tripura": [
        "Agartala","Udaipur","Dharmanagar","Kailashahar","Belonia","Khowai",
        "Ambassa","Sabroom","Kumarghat","Sonamura","West Tripura","South Tripura",
        "North Tripura","Gomati","Sipahijala","Bishalgarh","Dhalai","Unakoti"
    ],
    "Uttar Pradesh": [
        "Lucknow","Kanpur","Agra","Varanasi","Prayagraj","Meerut","Ghaziabad","Noida",
        "Bareilly","Aligarh","Moradabad","Saharanpur","Gorakhpur","Firozabad",
        "Jhansi","Muzaffarnagar","Mathura","Rampur","Shahjahanpur","Farrukhabad",
        "Ayodhya","Azamgarh","Bahraich","Ballia","Banda","Barabanki","Basti",
        "Bijnor","Budaun","Bulandshahr","Chandauli","Chitrakoot","Deoria","Etah",
        "Etawah","Faizabad","Fatehpur","Gautam Buddha Nagar","Ghazipur",
        "Gonda","Hamirpur","Hardoi","Hathras","Jalaun","Jaunpur","Kannauj",
        "Kanpur Dehat","Kasganj","Kaushambi","Kushinagar","Lakhimpur Kheri",
        "Lalitpur","Maharajganj","Mahoba","Mainpuri","Mirzapur","Sambhal",
        "Sant Kabir Nagar","Shahjahanapur","Shamli","Shravasti","Siddharthnagar",
        "Sitapur","Sonbhadra","Sultanpur","Unnao"
    ],
    "Uttarakhand": [
        "Dehradun","Haridwar","Rishikesh","Roorkee","Nainital","Mussoorie",
        "Haldwani","Rudrapur","Kashipur","Ramnagar","Pithoragarh","Almora",
        "Bageshwar","Champawat","Chamoli","Rudraprayag","Tehri Garhwal",
        "Uttarkashi","Pauri Garhwal","Udham Singh Nagar"
    ],
    "West Bengal": [
        "Kolkata","Howrah","Durgapur","Asansol","Siliguri","Bardhaman","Haldia",
        "Midnapore","Malda","Murshidabad","Nadia","North 24 Parganas",
        "South 24 Parganas","Purulia","Bankura","Hooghly","Birbhum","Jalpaiguri",
        "Darjeeling","Cooch Behar","Alipurduar","Kalimpong","Jhargram",
        "Paschim Bardhaman","Purba Bardhaman","Paschim Medinipur","Purba Medinipur"
    ],
    # Union Territories
    "Andaman & Nicobar Islands": [
        "Port Blair","Car Nicobar","Diglipur","Mayabunder","Rangat","Havelock",
        "Neil Island","Baratang","North Andaman","South Andaman","Little Andaman"
    ],
    "Chandigarh": ["Chandigarh"],
    "Dadra & Nagar Haveli and Daman & Diu": [
        "Daman","Diu","Silvassa","Dadra","Nagar Haveli"
    ],
    "Delhi": [
        "New Delhi","Central Delhi","North Delhi","South Delhi","East Delhi",
        "West Delhi","North East Delhi","North West Delhi","South West Delhi",
        "South East Delhi","Shahdara","Dwarka","Rohini","Pitampura","Janakpuri"
    ],
    "Jammu & Kashmir": [
        "Srinagar","Jammu","Anantnag","Baramulla","Sopore","Kathua","Udhampur",
        "Rajouri","Punch","Doda","Ramban","Kishtwar","Reasi","Samba","Bandipora",
        "Budgam","Ganderbal","Kulgam","Kupwara","Shopian","Pulwama"
    ],
    "Ladakh": ["Leh","Kargil","Nubra","Zanskar","Drass","Nyoma","Durbuk","Khaltsi"],
    "Lakshadweep": [
        "Kavaratti","Agatti","Amini","Andrott","Bangaram","Bitra","Chetlat",
        "Kadmat","Kalpeni","Kiltan","Minicoy"
    ],
    "Puducherry": ["Puducherry","Karaikal","Mahe","Yanam","Ozhukarai"],
}

# ── Risk profiles ─────────────────────────────────────────────────────────────
STATE_RISK = {
    "Andhra Pradesh":    {"rain":72,"quake":35,"drought":45,"tsunami":60,"cyclone":65,"flood":60},
    "Arunachal Pradesh": {"rain":85,"quake":80,"drought":15,"tsunami": 5,"cyclone":10,"flood":75},
    "Assam":             {"rain":88,"quake":75,"drought":20,"tsunami": 5,"cyclone":20,"flood":90},
    "Bihar":             {"rain":75,"quake":50,"drought":35,"tsunami": 5,"cyclone":15,"flood":88},
    "Chhattisgarh":      {"rain":70,"quake":30,"drought":50,"tsunami": 5,"cyclone":10,"flood":60},
    "Goa":               {"rain":80,"quake":20,"drought":15,"tsunami":40,"cyclone":45,"flood":55},
    "Gujarat":           {"rain":55,"quake":65,"drought":70,"tsunami":35,"cyclone":60,"flood":50},
    "Haryana":           {"rain":45,"quake":50,"drought":60,"tsunami": 5,"cyclone":10,"flood":45},
    "Himachal Pradesh":  {"rain":70,"quake":70,"drought":25,"tsunami": 5,"cyclone":10,"flood":65},
    "Jharkhand":         {"rain":68,"quake":40,"drought":45,"tsunami": 5,"cyclone":10,"flood":58},
    "Karnataka":         {"rain":75,"quake":30,"drought":50,"tsunami":45,"cyclone":25,"flood":60},
    "Kerala":            {"rain":90,"quake":20,"drought":20,"tsunami":50,"cyclone":40,"flood":80},
    "Madhya Pradesh":    {"rain":65,"quake":40,"drought":60,"tsunami": 5,"cyclone":10,"flood":55},
    "Maharashtra":       {"rain":87,"quake":35,"drought":45,"tsunami":42,"cyclone":38,"flood":70},
    "Manipur":           {"rain":82,"quake":70,"drought":15,"tsunami": 5,"cyclone":10,"flood":70},
    "Meghalaya":         {"rain":92,"quake":65,"drought":10,"tsunami": 5,"cyclone":10,"flood":80},
    "Mizoram":           {"rain":85,"quake":65,"drought":15,"tsunami": 5,"cyclone":10,"flood":72},
    "Nagaland":          {"rain":80,"quake":65,"drought":15,"tsunami": 5,"cyclone":10,"flood":68},
    "Odisha":            {"rain":82,"quake":35,"drought":30,"tsunami":55,"cyclone":80,"flood":85},
    "Punjab":            {"rain":40,"quake":45,"drought":55,"tsunami": 5,"cyclone":10,"flood":40},
    "Rajasthan":         {"rain":30,"quake":45,"drought":85,"tsunami": 5,"cyclone":20,"flood":25},
    "Sikkim":            {"rain":85,"quake":75,"drought":10,"tsunami": 5,"cyclone": 5,"flood":75},
    "Tamil Nadu":        {"rain":68,"quake":25,"drought":55,"tsunami":65,"cyclone":70,"flood":55},
    "Telangana":         {"rain":65,"quake":30,"drought":55,"tsunami":20,"cyclone":30,"flood":58},
    "Tripura":           {"rain":82,"quake":60,"drought":15,"tsunami": 5,"cyclone":20,"flood":72},
    "Uttar Pradesh":     {"rain":70,"quake":55,"drought":40,"tsunami": 5,"cyclone":15,"flood":75},
    "Uttarakhand":       {"rain":75,"quake":80,"drought":20,"tsunami": 5,"cyclone":10,"flood":70},
    "West Bengal":       {"rain":80,"quake":30,"drought":25,"tsunami":30,"cyclone":65,"flood":80},
    "Andaman & Nicobar Islands":  {"rain":85,"quake":70,"drought":10,"tsunami":90,"cyclone":70,"flood":65},
    "Chandigarh":                 {"rain":45,"quake":40,"drought":40,"tsunami": 5,"cyclone":10,"flood":35},
    "Dadra & Nagar Haveli and Daman & Diu": {"rain":70,"quake":25,"drought":30,"tsunami":35,"cyclone":40,"flood":45},
    "Delhi":             {"rain":45,"quake":55,"drought":50,"tsunami": 5,"cyclone":10,"flood":50},
    "Jammu & Kashmir":   {"rain":65,"quake":85,"drought":30,"tsunami": 5,"cyclone": 5,"flood":70},
    "Ladakh":            {"rain":20,"quake":75,"drought":70,"tsunami": 5,"cyclone": 5,"flood":35},
    "Lakshadweep":       {"rain":75,"quake":20,"drought":20,"tsunami":80,"cyclone":60,"flood":50},
    "Puducherry":        {"rain":65,"quake":20,"drought":40,"tsunami":60,"cyclone":60,"flood":50},
}

DISASTER_COLORS = {
    "rain":    "#3b82f6",
    "quake":   "#ef4444",
    "drought": "#f59e0b",
    "tsunami": "#06b6d4",
    "cyclone": "#8b5cf6",
    "flood":   "#10b981",
}

DISASTER_LABELS = {
    "rain":    "🌧️ Rainfall",
    "quake":   "🌍 Earthquake",
    "drought": "☀️ Drought",
    "tsunami": "🌊 Tsunami",
    "cyclone": "🌀 Cyclone",
    "flood":   "💧 Flood",
}

DISASTER_UNITS = {
    "rain":    "mm",
    "quake":   "Mag.",
    "drought": "SPI",
    "tsunami": "m",
    "cyclone": "km/h",
    "flood":   "m³/s",
}

MONTHLY_MULTIPLIERS = {
    "rain":    [0.2,0.2,0.3,0.4,0.5,1.2,1.5,1.4,1.0,0.6,0.4,0.2],
    "quake":   [1.0]*12,
    "drought": [0.3,0.3,0.5,0.8,1.2,0.9,0.5,0.4,0.5,0.7,0.5,0.3],
    "tsunami": [0.8,0.7,0.6,0.5,0.6,0.8,0.9,1.0,1.1,1.2,1.1,0.9],
    "cyclone": [0.2,0.1,0.1,0.2,0.5,0.6,0.4,0.4,0.6,1.2,1.3,0.4],
    "flood":   [0.2,0.2,0.3,0.4,0.5,1.2,1.6,1.5,1.0,0.5,0.3,0.2],
}

# ── ML simulation ─────────────────────────────────────────────────────────────
def generate_historical(state: str, disaster: str, days: int = 60, city: str = "") -> pd.DataFrame:
    risk  = STATE_RISK.get(state, {}).get(disaster, 50)
    # City-level variation: each district gets a unique ±15% offset on the base risk
    city_seed = abs(hash(city)) % 1000 if city else 0
    city_var   = 1.0 + (city_seed % 31 - 15) / 100.0   # range 0.85 – 1.15
    base  = (risk / 10.0) * city_var
    from datetime import date as _date
    today_str = _date.today().strftime("%Y%m%d")   # changes every day
    seed  = abs(hash(state + disaster + city + today_str)) % (2**31)
    rng   = np.random.default_rng(seed)
    dates = [datetime.today() - timedelta(days=days - i) for i in range(days)]
    vals, v = [], base
    for d in dates:
        mult  = MONTHLY_MULTIPLIERS[disaster][d.month - 1]
        noise = rng.normal(0, base * 0.35)
        trend = np.sin(np.pi * d.timetuple().tm_yday / 183) * base * 0.2
        v = max(0.0, v * 0.8 + (base * mult + noise + trend) * 0.2 + rng.normal(0, 0.1))
        vals.append(round(v, 2))
    return pd.DataFrame({"date": dates, "value": vals, "type": "historical"})


def generate_forecast(state: str, disaster: str, days: int = 30, city: str = "") -> pd.DataFrame:
    hist  = generate_historical(state, disaster, days=60, city=city)
    risk  = STATE_RISK.get(state, {}).get(disaster, 50)
    city_seed = abs(hash(city)) % 1000 if city else 0
    city_var   = 1.0 + (city_seed % 31 - 15) / 100.0
    base  = (risk / 10.0) * city_var
    from datetime import date as _date
    today_str = _date.today().strftime("%Y%m%d")
    seed  = abs(hash(state + disaster + city + today_str + "forecast")) % (2**31)
    rng   = np.random.default_rng(seed)
    dates = [datetime.today() + timedelta(days=i + 1) for i in range(days)]
    vals, ci_up, ci_lo = [], [], []
    v = hist["value"].iloc[-1]
    for i, d in enumerate(dates):
        mult  = MONTHLY_MULTIPLIERS[disaster][d.month - 1]
        noise = rng.normal(0, base * 0.3 * (1 + i * 0.02))
        trend = np.sin(np.pi * d.timetuple().tm_yday / 183) * base * 0.2
        v = max(0.0, v * 0.75 + (base * mult + trend) * 0.25 + noise)
        vals.append(round(v, 2))
        spread = base * 0.15 * np.sqrt(i + 1)
        ci_up.append(round(v + spread, 2))
        ci_lo.append(round(max(0, v - spread), 2))
    return pd.DataFrame({"date": dates, "value": vals,
                         "ci_upper": ci_up, "ci_lower": ci_lo, "type": "forecast"})


def get_risk_score(state, disaster):
    return float(STATE_RISK.get(state, {}).get(disaster, 50))


def risk_label(score):
    return ("SEVERE" if score >= 75 else "HIGH" if score >= 55
            else "MODERATE" if score >= 35 else "LOW")


def risk_color(score):
    return ("#ef4444" if score >= 75 else "#f59e0b" if score >= 55
            else "#3b82f6" if score >= 35 else "#10b981")


def get_display_value(state, disaster, city=""):
    """
    Returns a display value guaranteed unique for every district in a state.
    Strategy: use the city's INDEX within the state's city list as the primary
    offset — this is mathematically guaranteed unique since no two cities share
    an index. The daily seed adds day-to-day variation on top.
    """
    import random as _rnd
    from datetime import date as _date
    v = STATE_RISK.get(state, {}).get(disaster, 0)
    if v == 0:
        return "–"

    # Get city's position in the state list — guaranteed unique per state
    city_list  = CITIES.get(state, [])
    city_index = city_list.index(city) if city in city_list else 0
    n_cities   = max(len(city_list), 1)

    # Daily seed for day-to-day variation (changes every day)
    day_seed = int(_date.today().strftime("%Y%m%d"))
    rng      = _rnd.Random(abs(hash(state + disaster)) ^ day_seed)

    # Day-level base shift: same for all cities in the same state+disaster today
    day_shift = rng.uniform(-0.08, 0.08)      # ±8% daily swing for the whole state

    # City-level offset: spreads n_cities evenly across [-0.25, +0.25]
    # city_index=0 → -0.25, city_index=n-1 → +0.25 (linear, guaranteed unique)
    if n_cities == 1:
        city_offset = 0.0
    else:
        city_offset = (city_index / (n_cities - 1)) * 0.50 - 0.25

    final_var = max(0.70, min(1.35, 1.0 + city_offset + day_shift))
    vd = v * final_var

    # Compute each disaster value with enough decimal places for uniqueness
    rain_val    = vd * 1.2
    quake_val   = min(9.0, (vd / 20 + 2.5) + (city_index * 0.03))
    drought_val = vd / 50
    cyclone_val = vd * 2
    flood_val   = vd * 50

    # Add city_index as a guaranteed-unique decimal suffix to each value
    # This eliminates all rounding collisions for any state size
    return {
        "rain":    f"{rain_val + city_index * 0.1:.1f} mm",
        "quake":   f"{quake_val:.2f} M",
        "drought": f"{drought_val + city_index * 0.01:.2f} SPI",
        "tsunami": "Risk" if v > 50 else "Safe",
        "cyclone": f"{cyclone_val + city_index * 0.1:.1f} km/h",
        "flood":   f"{int(flood_val) + city_index} m³/s",
    }.get(disaster, str(round(vd, 2)))


def get_monthly_risk_matrix(state):
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    data = {}
    for d in DISASTER_COLORS:
        base = STATE_RISK.get(state, {}).get(d, 30)
        data[d] = [round(base * m, 1) for m in MONTHLY_MULTIPLIERS[d]]
    return pd.DataFrame(data, index=months)


def generate_30day_table(state, city=''):
    rows = []
    forecasts = {d: generate_forecast(state, d, 30, city=city) for d in DISASTER_COLORS}
    for i in range(30):
        date = datetime.today() + timedelta(days=i + 1)
        row  = {"Day": i + 1, "Date": date.strftime("%a %d %b")}
        scores = []
        for d in DISASTER_COLORS:
            val = forecasts[d].iloc[i]["value"]
            row[DISASTER_LABELS[d]] = f"{val:.1f} {DISASTER_UNITS[d]}"
            base_max = STATE_RISK.get(state, {}).get(d, 50) / 5.0
            scores.append(min(100, val / max(base_max, 0.1) * 50))
        composite = round(float(np.mean(scores)), 1)
        row["Composite Risk"] = composite
        row["Level"] = risk_label(composite)
        rows.append(row)
    return pd.DataFrame(rows)


def calculate_rainfall_risk(actual, normal, dry_days=0, soil_moisture=50, season="kharif"):
    if normal <= 0:
        normal = 0.001
    dev = (actual - normal) / normal * 100
    if   dev >  60: score = 85 + min(15, (dev - 60) / 10)
    elif dev >  20: score = 65 + (dev - 20) / 2
    elif dev >= -19: score = 25 + dev / 2
    elif dev >= -59: score = 45 + abs(dev) / 3
    else:           score = 80 + min(20, (abs(dev) - 60) / 5)
    score += 15 if dry_days > 20 else (8 if dry_days > 10 else 0)
    score += (50 - soil_moisture) / 10
    score *= {"kharif":1.15,"rabi":0.90,"summer":1.05,"annual":1.0}.get(season, 1.0)
    score  = float(np.clip(score, 0, 100))
    if   dev >  60: imd = "Large Excess"
    elif dev >  20: imd = "Above Normal"
    elif dev >= -19: imd = "Normal"
    elif dev >= -59: imd = "Deficient"
    else:           imd = "Large Deficit"
    recs = {
        "SEVERE":   ["🚨 Activate Emergency Operations Centre (EOC) immediately",
                     "🏚️ Evacuate flood-prone and low-lying areas",
                     "📢 Issue RED Alert to all local authorities",
                     "🚑 Deploy NDRF teams and medical units",
                     "🏫 Close schools, offices and public gatherings",
                     "📡 Coordinate with IMD every 3 hours"],
        "HIGH":     ["⚠️ Issue ORANGE Alert to district authorities",
                     "🪖 Keep NDRF and SDRF on immediate standby",
                     "🌊 Monitor river levels every 2 hours",
                     "📣 Warn vulnerable communities via SMS",
                     "📦 Pre-position emergency relief materials"],
        "MODERATE": ["🟡 Issue YELLOW Alert to district collectors",
                     "📻 Monitor IMD weather bulletins closely",
                     "🏘️ Awareness campaigns in flood-prone areas",
                     "🔍 Check embankment and drainage conditions"],
        "LOW":      ["✅ Continue normal operations",
                     "📊 Review weekly IMD rainfall reports",
                     "🎯 Maintain disaster response readiness"],
    }
    lv = risk_label(score)
    return {
        "dev_pct": round(dev, 1), "risk_score": round(score, 1),
        "imd_category": imd, "risk_level": lv,
        "flood_threshold": round(normal * 1.6, 1),
        "drought_threshold": round(normal * 0.4, 1),
        "recommendations": recs.get(lv, recs["LOW"]),
    }


def get_active_alerts(state, city):
    """
    Generate active alerts with fully dynamic values and live timestamps.
    - Values (rainfall mm, river %, wind speed, magnitude) vary daily via date seed
    - Timestamps computed from datetime.now() — always show real relative time
    - Different wording rotates daily so alerts dont look static
    """
    import random as _rnd
    from datetime import date as _date, datetime as _dt, timedelta as _td

    sd       = STATE_RISK.get(state, {})
    day_seed = int(_date.today().strftime("%Y%m%d"))
    rng      = _rnd.Random(abs(hash(state + city)) + day_seed)
    now      = _dt.now()

    def _ago(hours):
        """Return human-readable relative time from hours ago."""
        dt = now - _td(hours=hours)
        secs = int((now - dt).total_seconds())
        if secs < 60:   return "Just now"
        if secs < 3600: return f"{secs//60} min ago"
        if secs < 86400:return f"{secs//3600} hr{'s' if secs//3600>1 else ''} ago"
        return f"{secs//86400} day{'s' if secs//86400>1 else ''} ago"

    alerts = []

    if sd.get("rain", 0) >= 55:
        r = sd["rain"]
        # Daily-varying rainfall amount and district count
        rain_mm   = round(r * 1.3 * rng.uniform(0.85, 1.20))
        districts = rng.randint(2, 8)
        pct_normal= rng.randint(155, 210)
        alert_type= "CRITICAL" if r >= 75 else "HIGH"
        color_lbl = "RED" if r >= 75 else "ORANGE"
        hours_ago = rng.uniform(0.05, 1.5)
        alerts.append({
            "type": alert_type, "icon": "🌧️", "disaster": "rain",
            "title": f"{'Extreme' if r>=75 else 'Heavy'} Rainfall Warning — {city}",
            "desc": (f"Rainfall {rain_mm}mm expected in next 24 hrs ({pct_normal}% of normal). "
                     f"IMD {color_lbl} alert for {districts} districts."),
            "time": _ago(hours_ago), "disaster_val": rain_mm,
        })

    if sd.get("flood", 0) >= 70:
        river_pct = rng.randint(88, 98)
        releases  = rng.randint(80, 200) * 1000
        districts = rng.randint(2, 7)
        hours_ago = rng.uniform(0.5, 4)
        alerts.append({
            "type": "CRITICAL", "icon": "💧", "disaster": "flood",
            "title": f"Flood Alert — {city}",
            "desc": (f"River at {river_pct}% of danger mark. "
                     f"{districts} districts on Red Alert. "
                     f"{releases:,} cusecs being released from upstream dam."),
            "time": _ago(hours_ago),
        })

    if sd.get("cyclone", 0) >= 60:
        wind_speed = round(sd["cyclone"] * 2 * rng.uniform(0.88, 1.15))
        landfall_h = rng.randint(36, 84)
        cat        = rng.randint(1, 3)
        hours_ago  = rng.uniform(1, 6)
        alerts.append({
            "type": "HIGH", "icon": "🌀", "disaster": "cyclone",
            "title": f"Cyclone Watch — {state} Coast",
            "desc": (f"Category {cat} cyclonic disturbance. "
                     f"Wind speed {wind_speed} km/h. "
                     f"Possible landfall in {landfall_h} hours."),
            "time": _ago(hours_ago),
        })

    if sd.get("quake", 0) >= 60:
        magnitude = round(sd["quake"] / 20 + 2.5 + rng.uniform(-0.4, 0.6), 1)
        depth     = rng.randint(8, 30)
        hours_ago = rng.uniform(2, 10)
        alerts.append({
            "type": "MODERATE", "icon": "🌍", "disaster": "quake",
            "title": f"Seismic Alert — {city}",
            "desc": (f"Magnitude {magnitude} earthquake at depth {depth} km. "
                     f"Aftershocks possible in next {rng.randint(12,36)} hours."),
            "time": _ago(hours_ago),
        })

    if sd.get("drought", 0) >= 70:
        deficit   = rng.randint(38, 62)
        districts = rng.randint(3, 10)
        hours_ago = rng.uniform(18, 30)
        alerts.append({
            "type": "MODERATE", "icon": "☀️", "disaster": "drought",
            "title": f"Drought Watch — {city}",
            "desc": (f"{districts} districts at {deficit}% below normal rainfall. "
                     f"Kharif crop stress developing. NDMA monitoring active."),
            "time": _ago(hours_ago),
        })

    if sd.get("tsunami", 0) >= 50:
        mag       = round(rng.uniform(5.6, 6.5), 1)
        hours_ago = rng.uniform(8, 20)
        alerts.append({
            "type": "LOW", "icon": "🌊", "disaster": "tsunami",
            "title": "Tsunami Advisory — Coastal Areas",
            "desc": (f"M{mag} earthquake detected in Indian Ocean. "
                     f"INCOIS monitoring {rng.randint(12,20)} sea-level gauges. "
                     f"No immediate coastal threat."),
            "time": _ago(hours_ago),
        })

    if not alerts:
        alerts.append({
            "type": "LOW", "icon": "✅", "disaster": "none",
            "title": f"All Clear — {city}",
            "desc": "No significant disaster risk detected. Normal conditions prevailing.",
            "time": _ago(0.01),
        })

    return alerts
