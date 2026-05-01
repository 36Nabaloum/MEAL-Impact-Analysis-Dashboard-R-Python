"""
Generate MEAL datasets for Project 3 — R Analysis
Produces 4 CSV files consumed by the R scripts.
"""
import csv, random
from datetime import date, timedelta

random.seed(2025)

COUNTRIES  = ["Burkina Faso", "Mali", "Niger", "Chad"]
REGIONS    = {
    "Burkina Faso": ["Sahel", "Nord", "Est", "Centre", "Cascades"],
    "Mali":         ["Mopti", "Gao", "Tombouctou", "Segou", "Bamako"],
    "Niger":        ["Diffa", "Zinder", "Maradi", "Agadez", "Niamey"],
    "Chad":         ["Lac", "Ouaddai", "Borkou", "N'Djamena", "Kanem"],
}
SECTORS    = ["Nutrition", "WASH", "Shelter", "Protection", "Health", "Food Security"]
DONORS     = ["USAID", "UNICEF", "BHA", "NORAD", "GFFO"]
ORGS       = ["IRC", "ACF", "MSF", "SPONG", "WFP", "UNICEF"]
INDICATORS = {
    "Nutrition":     ["SAM Treatment Rate (%)", "MUAC Screening Coverage (%)", "Referral Rate (%)"],
    "WASH":          ["HH Safe Water Access (%)", "Latrines Coverage (%)", "Hygiene Kits Distributed (#)"],
    "Shelter":       ["Families Sheltered (#)", "NFI Kits Distributed (#)", "Shelter Completion Rate (%)"],
    "Protection":    ["GBV Referral Rate (%)", "Child Protection Cases (#)", "Legal Aid Coverage (%)"],
    "Health":        ["Consultation Rate (%)", "Vaccination Coverage (%)", "Skilled Birth Attendance (%)"],
    "Food Security": ["Food Ration Coverage (%)", "Cash Transfer Rate (%)", "HH Food Security Score"],
}

# ── 1. indicators.csv — programme indicators ────────────────
with open("data/indicators.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["IndicatorID","Country","Region","Sector","Donor","Organization",
                "Indicator","Target","Achieved","Quarter","Year","Status"])
    iid = 1
    for yr in [2023, 2024]:
        for q in [1,2,3,4]:
            for _ in range(60):
                country = random.choice(COUNTRIES)
                region  = random.choice(REGIONS[country])
                sector  = random.choice(SECTORS)
                donor   = random.choice(DONORS)
                org     = random.choice(ORGS)
                indic   = random.choice(INDICATORS[sector])
                target  = random.randint(100, 5000)
                achieved= int(target * random.gauss(0.78, 0.18))
                achieved= max(0, min(int(target * 1.20), achieved))
                status  = ("On Track" if achieved/target >= 0.80
                           else "At Risk" if achieved/target >= 0.55
                           else "Delayed")
                w.writerow([f"IND-{iid:04d}", country, region, sector,
                            donor, org, indic, target, achieved, q, yr, status])
                iid += 1

# ── 2. beneficiaries.csv — individual level ─────────────────
with open("data/beneficiaries.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["BenID","Country","Region","Sector","Donor","Gender",
                "AgeGroup","VulnType","RegDate","HasDisability","HHSize"])
    bid = 1
    start = date(2023, 1, 1)
    for _ in range(1200):
        country = random.choice(COUNTRIES)
        region  = random.choice(REGIONS[country])
        sector  = random.choice(SECTORS)
        donor   = random.choice(DONORS)
        gender  = random.choices(["Female","Male"], weights=[60,40])[0]
        age_grp = random.choices(["0-5","6-17","18-59","60+"], weights=[20,28,45,7])[0]
        vuln    = random.choices(["IDP","Refugee","Host Community","Returnee"],
                                  weights=[40,20,30,10])[0]
        reg     = start + timedelta(days=random.randint(0, 729))
        disab   = random.choices([0,1], weights=[88,12])[0]
        hhsize  = random.randint(3,12)
        w.writerow([f"BEN-{bid:05d}", country, region, sector, donor,
                    gender, age_grp, vuln, str(reg), disab, hhsize])
        bid += 1

# ── 3. nutrition_screening.csv — clinical data ──────────────
with open("data/nutrition_screening.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["ScreenID","Country","Region","Organization","ScreenDate",
                "AgeMonths","Gender","MUAC_cm","WeightKg","HeightCm",
                "Oedema","NutritionStatus","Referred"])
    sid = 1
    start = date(2023, 1, 1)
    for _ in range(800):
        country = random.choice(COUNTRIES)
        region  = random.choice(REGIONS[country])
        org     = random.choice(ORGS)
        screen_d= start + timedelta(days=random.randint(0, 729))
        age_mo  = random.randint(6, 59)
        gender  = random.choice(["M","F"])
        muac    = max(7.5, min(20.0, round(random.gauss(12.8, 2.1), 1)))
        weight  = round(random.gauss(8.5, 2.8), 2)
        height  = round(random.gauss(78, 14), 1)
        oedema  = random.choices(["No","Yes"], weights=[93,7])[0]
        status  = ("SAM" if muac < 11.5 or oedema == "Yes"
                   else "MAM" if muac < 12.5 else "Normal")
        referred= "Yes" if status in ["SAM","MAM"] and random.random() > 0.3 else "No"
        w.writerow([f"SCR-{sid:05d}", country, region, org, str(screen_d),
                    age_mo, gender, muac, weight, height, oedema, status, referred])
        sid += 1

# ── 4. accountability.csv — feedback mechanism ──────────────
with open("data/accountability.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["FeedbackID","Country","Sector","FeedbackType","Channel",
                "Severity","Resolved","DaysToResolve","Date"])
    fid = 1
    types    = ["Complaint","Feedback","Request","Suggestion"]
    channels = ["Hotline","Community Meeting","Suggestion Box","Direct Staff"]
    start = date(2023, 1, 1)
    for _ in range(400):
        country  = random.choice(COUNTRIES)
        sector   = random.choice(SECTORS)
        fb_type  = random.choices(types, weights=[40,30,20,10])[0]
        channel  = random.choice(channels)
        severity = random.choices(["Low","Medium","High","Critical"],
                                   weights=[40,35,20,5])[0]
        resolved = random.choices(["Yes","No"], weights=[78,22])[0]
        days     = random.randint(1,45) if resolved == "Yes" else None
        fb_date  = start + timedelta(days=random.randint(0, 729))
        w.writerow([f"FB-{fid:04d}", country, sector, fb_type, channel,
                    severity, resolved, days if days else "", str(fb_date)])
        fid += 1

print("4 datasets generated:")
print("  indicators.csv          : 480 rows")
print("  beneficiaries.csv       : 1200 rows")
print("  nutrition_screening.csv :  800 rows")
print("  accountability.csv      :  400 rows")
