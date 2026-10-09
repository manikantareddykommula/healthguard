"""
HealthGuard Pharmaceutical Database & Persistent Storage Module.
Comprehensive healthcare platform database supporting:
- Verified medicine catalog, search, and multi-filters
- Role-based Authentication (Patient, Doctor, Administrator) with PBKDF2-HMAC-SHA256 password hashing
- Shopping cart, prescription-based verification gate, orders, and 5-stage tracking
- Doctor consultations and digital prescription issuance
- Medical reports vault (blood tests, radiology, discharge summaries)
- Health measurements / vitals recording with reference range evaluations
- Doctor appointment booking and scheduling
- Preventive healthcare and automatic annual checkup reminders
- 3D medication reminders and clinical adherence logging
- Centralized notification center and audit logs
"""

import hashlib
import json
import os
import secrets
import sqlite3
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "healthguard.db")
UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend", "uploads", "reports")
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Cryptographic password hashing helpers
def hash_password(password: str, salt: str = None) -> tuple:
    if not salt:
        salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    )
    return key.hex(), salt

def verify_password(password: str, password_hash: str, salt: str) -> bool:
    expected_hash, _ = hash_password(password, salt)
    return secrets.compare_digest(expected_hash, password_hash)

# Verified Real Pharmaceutical Catalog (Indian Pharmacopoeia)
MEDICINES_CATALOG = [
    {
        "id": "med-aug-625",
        "name": "Augmentin 625 Duo Tablet",
        "generic_name": "Amoxicillin (500mg) + Clavulanic Acid (125mg) IP",
        "brand": "Augmentin",
        "manufacturer": "GlaxoSmithKline Pharmaceuticals Ltd (GSK)",
        "dosage_form": "Tablet",
        "pack_size": "10 Tablets in 1 Strip",
        "mrp": 204.50,
        "price": 173.80,
        "discount_pct": 15,
        "availability": "In Stock",
        "stock_count": 85,
        "prescription_required": True,
        "schedule": "Schedule H1",
        "category": "Antibiotics & Anti-infectives",
        "uses": "Treatment of bacterial infections of the respiratory tract (pneumonia, bronchitis), ear, sinus, urinary tract, and soft tissue infections.",
        "warnings": "Take immediately before or at start of meals to minimize gastrointestinal discomfort. Complete the full course prescribed by your physician. Contraindicated in patients with severe penicillin allergy or history of amoxicillin-associated hepatic dysfunction.",
        "storage": "Store below 25°C in a dry place. Protect from light and excessive moisture. Keep out of reach of children.",
        "dosage_instructions": "1 tablet twice daily after food, or as directed by the physician.",
        "pregnancy_safety": "Category B - Consult doctor before use.",
        "alcohol_interaction": "Moderate - avoid alcohol as it may heighten GI sensitivity.",
        "side_effects": ["Mild nausea", "Diarrhea", "Vomiting", "Skin rash (seek doctor)"],
        "gallery": {
            "main": "/images/medicines/augmentin_main.svg",
            "packaging": "/images/medicines/augmentin_pack.svg",
            "dosage_view": "/images/medicines/augmentin_tablet.svg",
            "back_view": "/images/medicines/augmentin_back.svg"
        },
        "rating": 4.8,
        "reviews_count": 342
    },
    {
        "id": "med-dolo-650",
        "name": "Dolo 650 Tablet",
        "generic_name": "Paracetamol / Acetaminophen (650mg) IP",
        "brand": "Dolo",
        "manufacturer": "Micro Labs Ltd",
        "dosage_form": "Tablet",
        "pack_size": "15 Tablets in 1 Strip",
        "mrp": 34.00,
        "price": 28.90,
        "discount_pct": 15,
        "availability": "In Stock",
        "stock_count": 240,
        "prescription_required": False,
        "schedule": "Over-The-Counter (OTC)",
        "category": "Pain Relief & Antipyretic",
        "uses": "Relief from mild to moderate pain including headache, toothache, muscle aches, backache, and reduction of high fever.",
        "warnings": "Do not exceed maximum daily limit of 4000 mg (approx 6 tablets in 24 hours). Overdose may cause fatal liver toxicity. Do not combine with other paracetamol-containing products. Avoid alcohol consumption.",
        "storage": "Store in a cool and dry place away from direct sunlight. Do not freeze.",
        "dosage_instructions": "1 tablet every 4 to 6 hours as needed for fever/pain. Do not exceed 4 tablets in 24 hours without medical supervision.",
        "pregnancy_safety": "Generally considered safe under doctor guidance.",
        "alcohol_interaction": "Unsafe - increases hepatic injury risk.",
        "side_effects": ["Rare allergic rash", "Mild gastric discomfort if taken without water"],
        "gallery": {
            "main": "/images/medicines/dolo_main.svg",
            "packaging": "/images/medicines/dolo_pack.svg",
            "dosage_view": "/images/medicines/dolo_tablet.svg",
            "back_view": "/images/medicines/dolo_back.svg"
        },
        "rating": 4.9,
        "reviews_count": 890
    },
    {
        "id": "med-asth-100",
        "name": "Asthalin Inhaler 100 mcg",
        "generic_name": "Salbutamol / Albuterol Sulfate (100mcg/actuation) IP",
        "brand": "Asthalin",
        "manufacturer": "Cipla Ltd",
        "dosage_form": "Inhaler",
        "pack_size": "200 Metered Actuations (Doses)",
        "mrp": 165.00,
        "price": 140.25,
        "discount_pct": 15,
        "availability": "In Stock",
        "stock_count": 60,
        "prescription_required": True,
        "schedule": "Schedule H",
        "category": "Respiratory & Asthma Care",
        "uses": "Quick relief and prevention of bronchospasm in asthma, chronic obstructive pulmonary disease (COPD), and exercise-induced asthma.",
        "warnings": "Shake well before each use. Rinse mouth with water after inhaling. If breathing worsens after inhalation, discontinue immediately and contact emergency medical services. Caution in patients with hyperthyroidism or cardiac arrhythmias.",
        "storage": "Store below 30°C. Do not puncture or incinerate canister even when empty. Protect from freezing and direct sunlight.",
        "dosage_instructions": "1 to 2 inhalations (puffs) every 4 to 6 hours as required for acute bronchospasm, or 15 minutes before exercise.",
        "pregnancy_safety": "Category C - Use if clinical benefit outweighs potential fetal risk.",
        "alcohol_interaction": "No direct interaction noted.",
        "side_effects": ["Fine tremor in hands", "Mild tachycardia / palpitations", "Headache"],
        "gallery": {
            "main": "/images/medicines/asthalin_main.svg",
            "packaging": "/images/medicines/asthalin_pack.svg",
            "dosage_view": "/images/medicines/asthalin_inhaler.svg",
            "back_view": "/images/medicines/asthalin_back.svg"
        },
        "rating": 4.85,
        "reviews_count": 420
    },
    {
        "id": "med-bena-100",
        "name": "Benadryl Cough Syrup (100ml)",
        "generic_name": "Diphenhydramine HCl (14.08mg) + Ammonium Chloride (138mg) + Sodium Citrate (57.03mg) per 5ml",
        "brand": "Benadryl",
        "manufacturer": "Johnson & Johnson Ltd",
        "dosage_form": "Syrup",
        "pack_size": "100 ml Bottle with Measuring Cup",
        "mrp": 135.00,
        "price": 114.75,
        "discount_pct": 15,
        "availability": "In Stock",
        "stock_count": 110,
        "prescription_required": False,
        "schedule": "Over-The-Counter (OTC)",
        "category": "Cough & Cold Formulations",
        "uses": "Relief from dry unproductive cough, throat irritation, tickling sensation in throat, and allergic sneezing.",
        "warnings": "May induce marked drowsiness and sedation. Do not drive, operate heavy machinery, or consume sedatives or alcohol during therapy. Not recommended for children below 2 years of age without specialist guidance.",
        "storage": "Store at ambient room temperature (15°C to 25°C). Keep tightly closed. Protect from heat and light.",
        "dosage_instructions": "Adults: 5ml to 10ml (1 to 2 measuring teaspoonsful) every 4 hours, not exceeding 4 doses in 24 hours.",
        "pregnancy_safety": "Consult physician before use during pregnancy.",
        "alcohol_interaction": "Unsafe - severely amplifies central nervous system sedation.",
        "side_effects": ["Drowsiness", "Dry mouth", "Mild dizziness", "Blurred vision"],
        "gallery": {
            "main": "/images/medicines/benadryl_main.svg",
            "packaging": "/images/medicines/benadryl_pack.svg",
            "dosage_view": "/images/medicines/benadryl_syrup.svg",
            "back_view": "/images/medicines/benadryl_back.svg"
        },
        "rating": 4.7,
        "reviews_count": 512
    },
    {
        "id": "med-glyc-500",
        "name": "Glycomet-GP 1 Tablet",
        "generic_name": "Metformin Hydrochloride (500mg SR) + Glimepiride (1mg) IP",
        "brand": "Glycomet",
        "manufacturer": "USV Private Ltd",
        "dosage_form": "Tablet",
        "pack_size": "15 Tablets in 1 Strip",
        "mrp": 118.00,
        "price": 100.30,
        "discount_pct": 15,
        "availability": "In Stock",
        "stock_count": 92,
        "prescription_required": True,
        "schedule": "Schedule H",
        "category": "Diabetes Management",
        "uses": "Management of Type 2 Diabetes Mellitus when diet, physical exercise, and single antidiabetic monotherapy do not achieve adequate glycemic control.",
        "warnings": "Must be taken with breakfast or first main meal. Risk of hypoglycemia (low blood glucose); carry sugar candy or glucose tablets. Swallow whole with water; do not crush sustained-release matrix.",
        "storage": "Store below 25°C in a dry place. Protect from moisture and light.",
        "dosage_instructions": "1 tablet once daily in the morning with breakfast, or as prescribed by the endocrinologist.",
        "pregnancy_safety": "Insulin is preferred during pregnancy; consult specialist.",
        "alcohol_interaction": "Unsafe - increases danger of severe hypoglycemia and lactic acidosis.",
        "side_effects": ["Hypoglycemia symptoms", "Mild abdominal flatulence", "Nausea", "Metallic taste"],
        "gallery": {
            "main": "/images/medicines/glycomet_main.svg",
            "packaging": "/images/medicines/glycomet_pack.svg",
            "dosage_view": "/images/medicines/glycomet_tablet.svg",
            "back_view": "/images/medicines/glycomet_back.svg"
        },
        "rating": 4.75,
        "reviews_count": 310
    },
    {
        "id": "med-pan-40",
        "name": "Pan 40 Tablet",
        "generic_name": "Pantoprazole Sodium Gastro-resistant (40mg) IP",
        "brand": "Pan",
        "manufacturer": "Alkem Laboratories Ltd",
        "dosage_form": "Tablet",
        "pack_size": "15 Tablets in 1 Strip",
        "mrp": 155.00,
        "price": 131.75,
        "discount_pct": 15,
        "availability": "In Stock",
        "stock_count": 130,
        "prescription_required": True,
        "schedule": "Schedule H",
        "category": "Gastroenterology & Antacids",
        "uses": "Gastroesophageal reflux disease (GERD), heartburn, erosive esophagitis, Zollinger-Ellison syndrome, and prevention of NSAID-induced ulcers.",
        "warnings": "Take 30-60 minutes before breakfast on an empty stomach. Swallow whole; do not chew or crush enteric coating. Prolonged use (>1 year) may decrease magnesium and vitamin B12 absorption.",
        "storage": "Store below 25°C. Keep blister strip dry and protected from light.",
        "dosage_instructions": "1 tablet daily in the morning on an empty stomach 30 minutes before food.",
        "pregnancy_safety": "Category B - Consult doctor for clinical benefit assessment.",
        "alcohol_interaction": "Moderate - alcohol exacerbates gastric acid production.",
        "side_effects": ["Headache", "Diarrhea or mild constipation", "Abdominal discomfort"],
        "gallery": {
            "main": "/images/medicines/pan40_main.svg",
            "packaging": "/images/medicines/pan40_pack.svg",
            "dosage_view": "/images/medicines/pan40_tablet.svg",
            "back_view": "/images/medicines/pan40_back.svg"
        },
        "rating": 4.88,
        "reviews_count": 670
    },
    {
        "id": "med-ator-20",
        "name": "Atorva 20 Tablet",
        "generic_name": "Atorvastatin Calcium (20mg) IP",
        "brand": "Atorva",
        "manufacturer": "Zydus Cadila",
        "dosage_form": "Tablet",
        "pack_size": "15 Tablets in 1 Strip",
        "mrp": 245.00,
        "price": 208.25,
        "discount_pct": 15,
        "availability": "In Stock",
        "stock_count": 70,
        "prescription_required": True,
        "schedule": "Schedule H",
        "category": "Cardiac & Cholesterol Care",
        "uses": "Lowering low-density lipoprotein (LDL-C) and triglycerides in hypercholesterolemia; prevention of cardiovascular disease, myocardial infarction, and strokes.",
        "warnings": "Take preferably at bedtime as hepatic cholesterol synthesis peaks at night. Promptly report any unexplained muscle tenderness, cramps, or weakness (risk of myopathy/rhabdomyolysis). Avoid grapefruit juice.",
        "storage": "Store between 20°C and 25°C. Protect from moisture and heat.",
        "dosage_instructions": "1 tablet once daily at bedtime with or without food, as directed by cardiologist.",
        "pregnancy_safety": "Category X - Strictly contraindicated in pregnant or nursing women.",
        "alcohol_interaction": "Caution - high alcohol intake elevates risk of liver enzyme abnormalities.",
        "side_effects": ["Joint pain", "Nasal congestion", "Mild indigestion", "Muscle ache"],
        "gallery": {
            "main": "/images/medicines/atorva_main.svg",
            "packaging": "/images/medicines/atorva_pack.svg",
            "dosage_view": "/images/medicines/atorva_tablet.svg",
            "back_view": "/images/medicines/atorva_back.svg"
        },
        "rating": 4.8,
        "reviews_count": 280
    },
    {
        "id": "med-beco-z",
        "name": "Becosules Z Capsules",
        "generic_name": "B-Complex (B1, B2, B6, B12, Niacinamide, Calcium Pantothenate, Folic Acid) + Vitamin C (50mg) + Zinc Sulfate (41.4mg)",
        "brand": "Becosules",
        "manufacturer": "Pfizer Ltd",
        "dosage_form": "Capsule",
        "pack_size": "20 Capsules in 1 Strip",
        "mrp": 52.00,
        "price": 44.20,
        "discount_pct": 15,
        "availability": "In Stock",
        "stock_count": 310,
        "prescription_required": False,
        "schedule": "Over-The-Counter (OTC)",
        "category": "Vitamins & Nutritional Supplements",
        "uses": "Treatment and prophylaxis of Vitamin B-complex, Vitamin C, and Zinc deficiencies; management of recurrent mouth aphthous ulcers; convalescence after fever.",
        "warnings": "Urine may turn intense bright yellow due to riboflavin (Vitamin B2) excretion, which is harmless. Take after a meal to prevent mild zinc-associated nausea.",
        "storage": "Store in a dry and cool place below 25°C. Keep container tightly sealed.",
        "dosage_instructions": "1 capsule daily after breakfast or lunch with plenty of water.",
        "pregnancy_safety": "Safe and recommended when used at dietary requirement levels.",
        "alcohol_interaction": "Safe - but heavy alcohol consumption degrades vitamin absorption.",
        "side_effects": ["Benign yellow urine discoloration", "Occasional mild stomach fullness"],
        "gallery": {
            "main": "/images/medicines/becosules_main.svg",
            "packaging": "/images/medicines/becosules_pack.svg",
            "dosage_view": "/images/medicines/becosules_capsule.svg",
            "back_view": "/images/medicines/becosules_back.svg"
        },
        "rating": 4.92,
        "reviews_count": 1150
    },
    {
        "id": "med-voli-50",
        "name": "Volini Pain Relief Gel (50g)",
        "generic_name": "Diclofenac Diethylamine (1.16% w/w) + Virgin Linseed Oil (3% w/w) + Methyl Salicylate (10% w/w) + Menthol (5% w/w)",
        "brand": "Volini",
        "manufacturer": "Sun Pharmaceutical Industries Ltd",
        "dosage_form": "Cream",
        "pack_size": "50 g Laminated Tube",
        "mrp": 170.00,
        "price": 144.50,
        "discount_pct": 15,
        "availability": "In Stock",
        "stock_count": 88,
        "prescription_required": False,
        "schedule": "Over-The-Counter (OTC)",
        "category": "Pain Relief & Muscle Recovery",
        "uses": "Targeted topical relief from lower back pain, knee joint stiffness, muscular strains, sprains, sports injuries, and frozen shoulder.",
        "warnings": "For external topical dermatological use only. Do not apply on open cuts, broken skin, eyes, or mucous membranes. Wash hands thoroughly after application unless hands are the treatment site. Do not occlude with airtight bandages.",
        "storage": "Store below 30°C. Do not freeze. Keep tube tightly capped after use.",
        "dosage_instructions": "Apply 2g to 4g gently over the affected area 3 to 4 times daily. Do not rub excessively.",
        "pregnancy_safety": "Avoid in third trimester of pregnancy.",
        "alcohol_interaction": "No systemic interaction with topical application.",
        "side_effects": ["Mild localized skin tingling", "Transient erythema/redness"],
        "gallery": {
            "main": "/images/medicines/volini_main.svg",
            "packaging": "/images/medicines/volini_pack.svg",
            "dosage_view": "/images/medicines/volini_gel.svg",
            "back_view": "/images/medicines/volini_back.svg"
        },
        "rating": 4.84,
        "reviews_count": 780
    },
    {
        "id": "med-cipl-10",
        "name": "Ciplox Eye/Ear Drops 10ml",
        "generic_name": "Ciprofloxacin Hydrochloride (0.3% w/v) Sterile Ophthalmic/Otic Solution IP",
        "brand": "Ciplox",
        "manufacturer": "Cipla Ltd",
        "dosage_form": "Drops",
        "pack_size": "10 ml Sterile Dropper Bottle",
        "mrp": 21.00,
        "price": 17.85,
        "discount_pct": 15,
        "availability": "In Stock",
        "stock_count": 140,
        "prescription_required": True,
        "schedule": "Schedule H",
        "category": "Eye & Ear Care",
        "uses": "Bacterial corneal ulcers, acute purulent conjunctivitis, external otitis, and bacterial ear canal infections.",
        "warnings": "Sterile solution. Do not touch nozzle tip to eyelids, fingers, or any exterior surface to prevent microbial contamination. Discard bottle 30 days after opening seal. Remove contact lenses prior to instillation.",
        "storage": "Store in a cool place protected from light. Do not freeze.",
        "dosage_instructions": "Instill 1 to 2 drops into affected eye/ear every 4 hours, or as directed by ophthalmologist/ENT specialist.",
        "pregnancy_safety": "Category C - Consult doctor before ocular/otic instillation.",
        "alcohol_interaction": "No direct ocular interaction.",
        "side_effects": ["Transient mild eye stinging or burning", "Temporary blurred vision"],
        "gallery": {
            "main": "/images/medicines/ciplox_main.svg",
            "packaging": "/images/medicines/ciplox_pack.svg",
            "dosage_view": "/images/medicines/ciplox_drops.svg",
            "back_view": "/images/medicines/ciplox_back.svg"
        },
        "rating": 4.7,
        "reviews_count": 210
    },
    {
        "id": "med-alle-120",
        "name": "Allegra 120 mg Tablet",
        "generic_name": "Fexofenadine Hydrochloride (120mg) IP",
        "brand": "Allegra",
        "manufacturer": "Sanofi India Ltd",
        "dosage_form": "Tablet",
        "pack_size": "10 Tablets in 1 Strip",
        "mrp": 218.00,
        "price": 185.30,
        "discount_pct": 15,
        "availability": "In Stock",
        "stock_count": 95,
        "prescription_required": True,
        "schedule": "Schedule H",
        "category": "Allergy & Antihistamines",
        "uses": "Second-generation non-sedating relief from seasonal allergic rhinitis (hay fever), persistent sneezing, itchy runny nose, itchy palate, and chronic idiopathic urticaria (hives).",
        "warnings": "Take with water only. Do not take with fruit juices (such as grapefruit, orange, or apple juice) as they decrease absorption significantly. Antacids containing aluminum or magnesium should not be taken within 2 hours.",
        "storage": "Store at controlled room temperature below 25°C away from excessive moisture.",
        "dosage_instructions": "1 tablet (120mg) once daily before meals with plain water.",
        "pregnancy_safety": "Category C - Consult doctor before use.",
        "alcohol_interaction": "Non-sedating antihistamine, but alcohol avoidance is advised.",
        "side_effects": ["Mild headache", "Drowsiness (rare)", "Dry throat"],
        "gallery": {
            "main": "/images/medicines/allegra_main.svg",
            "packaging": "/images/medicines/allegra_pack.svg",
            "dosage_view": "/images/medicines/allegra_tablet.svg",
            "back_view": "/images/medicines/allegra_back.svg"
        },
        "rating": 4.86,
        "reviews_count": 490
    },
    {
        "id": "med-shel-500",
        "name": "Shelcal 500 Tablet",
        "generic_name": "Elemental Calcium (500mg from Oyster Shell) + Vitamin D3 (Cholecalciferol 250 IU) IP",
        "brand": "Shelcal",
        "manufacturer": "Torrent Pharmaceuticals Ltd",
        "dosage_form": "Tablet",
        "pack_size": "15 Tablets in 1 Strip",
        "mrp": 131.00,
        "price": 111.35,
        "discount_pct": 15,
        "availability": "In Stock",
        "stock_count": 180,
        "prescription_required": False,
        "schedule": "Over-The-Counter (OTC)",
        "category": "Vitamins & Nutritional Supplements",
        "uses": "Treatment and prevention of calcium and Vitamin D deficiencies; management of osteoporosis, osteomalacia, rickets, and bone mineral density support in elderly.",
        "warnings": "Take with or immediately after meals for optimal gastrointestinal absorption. Drink plenty of water throughout the day. Contraindicated in severe hypercalcemia or nephrolithiasis (kidney stones).",
        "storage": "Store below 30°C in a dry place. Protect from direct heat, sunlight, and moisture.",
        "dosage_instructions": "1 tablet once or twice daily after meals, or as directed by the orthopedic consultant.",
        "pregnancy_safety": "Safe and routinely recommended in pregnancy and lactation under doctor guidance.",
        "alcohol_interaction": "Moderate - excessive alcohol impairs calcium homeostasis.",
        "side_effects": ["Occasional mild constipation", "Gas/flatulence if taken without food"],
        "gallery": {
            "main": "/images/medicines/shelcal_main.svg",
            "packaging": "/images/medicines/shelcal_pack.svg",
            "dosage_view": "/images/medicines/shelcal_tablet.svg",
            "back_view": "/images/medicines/shelcal_back.svg"
        },
        "rating": 4.89,
        "reviews_count": 920
    }
]

# Educational AI Assistant Knowledge Base for Diagnostic Parameters
AI_MEDICAL_TERMS = {
    "hemoglobin": {
        "term": "Hemoglobin (Hb)",
        "standard_range": "13.5 - 17.5 g/dL (Male) / 12.0 - 15.5 g/dL (Female)",
        "meaning": "An iron-rich protein in red blood cells that transports oxygen from your lungs to the tissues throughout your body.",
        "context": "Lower recorded values may be noted in anemia or nutritional iron deficiency. Higher values can be associated with dehydration or chronic smoking."
    },
    "fasting glucose": {
        "term": "Fasting Blood Glucose",
        "standard_range": "70 - 99 mg/dL (Normal fasting)",
        "meaning": "Measures circulating glucose levels after an overnight fast (minimum 8 hours). Primary baseline screening marker for metabolic health.",
        "context": "Values 100-125 mg/dL suggest pre-diabetes; values 126+ mg/dL indicate potential diabetes, requiring confirmation by a medical professional."
    },
    "hba1c": {
        "term": "Glycated Hemoglobin (HbA1c)",
        "standard_range": "< 5.7% (Normal), 5.7% - 6.4% (Prediabetes), 6.5%+ (Diabetes)",
        "meaning": "Reflects your average blood sugar concentration over the past 2 to 3 months by measuring glucose bound to red blood cells.",
        "context": "Used to monitor long-term glycemic management in diabetic and metabolic wellness programs."
    },
    "blood pressure": {
        "term": "Blood Pressure (Systolic / Diastolic)",
        "standard_range": "< 120/80 mmHg (Optimal resting)",
        "meaning": "The lateral hydrostatic pressure exerted by circulating blood upon the arterial vessel walls.",
        "context": "Systolic reflects peak ventricular contraction; Diastolic reflects resting arterial pressure between beats."
    },
    "lipid panel": {
        "term": "Lipid Profile (Total Cholesterol / LDL / HDL)",
        "standard_range": "Total < 200 mg/dL, LDL < 100 mg/dL, HDL > 40 mg/dL (M) / > 50 mg/dL (F)",
        "meaning": "A panel measuring various circulating lipoproteins and triglycerides involved in cardiovascular health.",
        "context": "Elevated LDL ('bad cholesterol') is a cardiovascular risk factor; elevated HDL ('good cholesterol') plays a protective role."
    },
    "creatinine": {
        "term": "Serum Creatinine",
        "standard_range": "0.74 - 1.35 mg/dL (Male) / 0.59 - 1.04 mg/dL (Female)",
        "meaning": "A waste byproduct of normal muscle metabolism that is filtered out of the blood exclusively by the kidneys.",
        "context": "Elevated values indicate reduced renal glomerular filtration efficiency, requiring professional clinical evaluation."
    }
}

class HealthGuardDB:
    def __init__(self):
        self.init_database()

    def get_connection(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        conn = self.get_connection()
        cur = conn.cursor()

        # 1. Users Table (RBAC)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                role TEXT NOT NULL, -- 'patient', 'doctor', 'admin'
                name TEXT NOT NULL,
                phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 2. Patients Profile Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                user_id TEXT PRIMARY KEY,
                age INTEGER,
                gender TEXT,
                blood_group TEXT,
                allergies TEXT,
                emergency_contact TEXT,
                address TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # 3. Doctors Profile Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS doctors (
                user_id TEXT PRIMARY KEY,
                specialization TEXT NOT NULL,
                reg_number TEXT NOT NULL,
                hospital TEXT NOT NULL,
                experience_years INTEGER,
                bio TEXT,
                consultation_fee REAL,
                availability_hours TEXT,
                verified_status TEXT DEFAULT 'Approved', -- 'Pending', 'Approved', 'Rejected'
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # 4. Cart Items Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS cart_items (
                medicine_id TEXT PRIMARY KEY,
                quantity INTEGER NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 5. Orders Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                user_id TEXT,
                data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 6. Prescriptions Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS prescriptions (
                prescription_id TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 7. Adherence Logs Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS adherence_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 8. Reminders Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 9. Notifications Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                data TEXT NOT NULL,
                is_read INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 10. Medical Reports Vault Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS medical_reports (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                report_type TEXT NOT NULL, -- 'Blood Test', 'X-Ray', 'MRI', 'CT', 'ECG', 'Lab Report', 'Discharge Summary'
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size_kb REAL,
                doctor_lab TEXT,
                report_date TEXT NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 11. Health Measurements / Vitals Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS health_measurements (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                measurement_type TEXT NOT NULL, -- 'blood_pressure', 'glucose', 'heart_rate', 'spo2', 'weight', 'temperature'
                value_primary REAL NOT NULL,
                value_secondary REAL, -- For Diastolic BP
                unit TEXT NOT NULL,
                context TEXT, -- 'Fasting', 'Post-Prandial', 'Resting', etc.
                alert_flag INTEGER DEFAULT 0,
                notes TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 12. Appointments Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id TEXT PRIMARY KEY,
                patient_id TEXT NOT NULL,
                patient_name TEXT NOT NULL,
                doctor_id TEXT NOT NULL,
                doctor_name TEXT NOT NULL,
                appointment_date TEXT NOT NULL,
                time_slot TEXT NOT NULL,
                status TEXT DEFAULT 'Scheduled', -- 'Scheduled', 'Completed', 'Cancelled'
                reason TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 13. Preventive Care & Checkups Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS checkups (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                category TEXT NOT NULL, -- 'Annual Health Checkup', 'Dental', 'Eye Exam', 'Vaccination', 'Cardiac Screening'
                last_completed_date TEXT,
                next_due_date TEXT NOT NULL,
                reminder_enabled INTEGER DEFAULT 1,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 14. Health Timeline Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS health_timeline (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                event_type TEXT NOT NULL, -- 'prescription', 'report', 'vitals', 'appointment', 'purchase', 'reminder'
                event_title TEXT NOT NULL,
                event_desc TEXT,
                ref_id TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 15. Audit Logs Table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                action TEXT NOT NULL,
                ip_address TEXT,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()

        # Seed pre-configured demo users if empty
        self._seed_demo_users(cur)
        # Seed pre-configured initial dataset
        self._seed_initial_data(cur)

        conn.commit()
        conn.close()

    def _seed_demo_users(self, cur):
        cur.execute("SELECT count(*) as cnt FROM users")
        if cur.fetchone()["cnt"] == 0:
            demo_users = [
                # 1. Patient Demo
                {
                    "id": "usr-patient-1",
                    "email": "patient@healthguard.com",
                    "password": "Patient@123",
                    "role": "patient",
                    "name": "Manik Sharma",
                    "phone": "+91 98765 43210",
                    "patient_profile": {
                        "age": 28,
                        "gender": "Male",
                        "blood_group": "B+",
                        "allergies": "Mild Dust Allergy, Penicillin-tolerant",
                        "emergency_contact": "+91 98111 22334 (Brother)",
                        "address": "Flat 402, Green Valley Heights, Sector 14, New Delhi - 110001"
                    }
                },
                # 2. Doctor Demo (Dr. Priya Nair)
                {
                    "id": "usr-doctor-1",
                    "email": "doctor@healthguard.com",
                    "password": "Doctor@123",
                    "role": "doctor",
                    "name": "Dr. Priya Nair, MD",
                    "phone": "+91 98450 12345",
                    "doctor_profile": {
                        "specialization": "Senior Pulmonologist & Critical Care",
                        "reg_number": "MCI-48920",
                        "hospital": "HealthGuard Premier Medical Center",
                        "experience_years": 14,
                        "bio": "Specialist in acute respiratory illnesses, asthma control regimens, and chronic cough management.",
                        "consultation_fee": 800.0,
                        "availability_hours": "Mon-Sat: 09:00 AM - 02:00 PM, 05:00 PM - 08:00 PM",
                        "verified_status": "Approved"
                    }
                },
                # 3. Doctor Demo 2 (Dr. Rajesh Sharma)
                {
                    "id": "usr-doctor-2",
                    "email": "rajesh@healthguard.com",
                    "password": "Doctor@123",
                    "role": "doctor",
                    "name": "Dr. Rajesh Sharma, MD, DM",
                    "phone": "+91 98220 54321",
                    "doctor_profile": {
                        "specialization": "Consultant Cardiologist & Diabetologist",
                        "reg_number": "MCI-31205",
                        "hospital": "HealthGuard Heart & Endocrine Institute",
                        "experience_years": 18,
                        "bio": "Cardiovascular prevention, metabolic management, hypertension, and preventive lipidology.",
                        "consultation_fee": 1000.0,
                        "availability_hours": "Tue-Sun: 10:00 AM - 04:00 PM",
                        "verified_status": "Approved"
                    }
                },
                # 4. Admin Demo
                {
                    "id": "usr-admin-1",
                    "email": "admin@healthguard.com",
                    "password": "Admin@123",
                    "role": "admin",
                    "name": "Administrator (HealthGuard HQ)",
                    "phone": "+91 11 2345 6789"
                }
            ]

            for u in demo_users:
                p_hash, salt = hash_password(u["password"])
                cur.execute(
                    "INSERT INTO users (id, email, password_hash, salt, role, name, phone) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (u["id"], u["email"], p_hash, salt, u["role"], u["name"], u["phone"])
                )
                if u["role"] == "patient" and "patient_profile" in u:
                    p = u["patient_profile"]
                    cur.execute(
                        "INSERT INTO patients (user_id, age, gender, blood_group, allergies, emergency_contact, address) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (u["id"], p["age"], p["gender"], p["blood_group"], p["allergies"], p["emergency_contact"], p["address"])
                    )
                elif u["role"] == "doctor" and "doctor_profile" in u:
                    d = u["doctor_profile"]
                    cur.execute(
                        "INSERT INTO doctors (user_id, specialization, reg_number, hospital, experience_years, bio, consultation_fee, availability_hours, verified_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (u["id"], d["specialization"], d["reg_number"], d["hospital"], d["experience_years"], d["bio"], d["consultation_fee"], d["availability_hours"], d["verified_status"])
                    )

    def _seed_initial_data(self, cur):
        # Seed Orders
        cur.execute("SELECT count(*) as cnt FROM orders")
        if cur.fetchone()["cnt"] == 0:
            init_order = {
                "order_id": "HG-89412",
                "order_date": "2026-10-03 14:22",
                "status": "Shipped",
                "stage_index": 3,
                "estimated_delivery": "Tomorrow by 2:00 PM",
                "tracking_number": "HG-EXP-994218",
                "courier": "HealthGuard ColdChain Express",
                "delivery_address": "Flat 402, Green Valley Heights, Sector 14, New Delhi - 110001",
                "prescription_id": "RX-2026-9041",
                "pharmacist_reviewer": "Dr. Shalini Verma (Reg #PHA-DL-8492)",
                "items": [
                    {
                        "id": "med-aug-625",
                        "name": "Augmentin 625 Duo Tablet",
                        "generic_name": "Amoxicillin (500mg) + Clavulanic Acid (125mg) IP",
                        "dosage_form": "Tablet",
                        "pack_size": "10 Tablets in 1 Strip",
                        "price": 173.80,
                        "quantity": 2,
                        "image": "/images/medicines/augmentin_main.svg"
                    },
                    {
                        "id": "med-dolo-650",
                        "name": "Dolo 650 Tablet",
                        "generic_name": "Paracetamol / Acetaminophen (650mg) IP",
                        "dosage_form": "Tablet",
                        "pack_size": "15 Tablets in 1 Strip",
                        "price": 28.90,
                        "quantity": 1,
                        "image": "/images/medicines/dolo_main.svg"
                    }
                ],
                "subtotal": 376.50,
                "discount": 0.00,
                "delivery_fee": 0.00,
                "total": 376.50,
                "payment_method": "HealthGuard Pay / UPI"
            }
            cur.execute("INSERT INTO orders (order_id, user_id, data) VALUES (?, ?, ?)", ("HG-89412", "usr-patient-1", json.dumps(init_order)))

        # Seed Prescriptions
        cur.execute("SELECT count(*) as cnt FROM prescriptions")
        if cur.fetchone()["cnt"] == 0:
            sample_prescriptions = [
                {
                    "prescription_id": "RX-2026-9041",
                    "consultation_id": "CNS-2026-8801",
                    "doctor_name": "Dr. Priya Nair, MD",
                    "doctor_reg": "MCI-48920",
                    "patient_name": "Manik Sharma",
                    "date": "2026-10-04",
                    "medicine_id": "med-aug-625",
                    "medicine_name": "Augmentin 625 Duo Tablet",
                    "dosage": "1 tablet twice daily (Morning 8:00 AM, Night 8:00 PM)",
                    "duration": "5 Days",
                    "instructions": "Take with food to minimize GI discomfort",
                    "status": "Approved",
                    "recommended_tests": "Chest X-Ray PA view, Routine Blood Count",
                    "verification_notes": "Clinically verified by authorized pharmacist. Valid for 5 days.",
                    "pharmacist_name": "Dr. Shalini Verma, B.Pharm, PharmD (Reg #PHA-DL-8492)"
                },
                {
                    "prescription_id": "RX-2026-9042",
                    "consultation_id": "CNS-2026-8801",
                    "doctor_name": "Dr. Priya Nair, MD",
                    "doctor_reg": "MCI-48920",
                    "patient_name": "Manik Sharma",
                    "date": "2026-10-04",
                    "medicine_id": "med-asth-100",
                    "medicine_name": "Asthalin Inhaler 100 mcg",
                    "dosage": "2 puffs as needed for acute wheezing / dyspnea",
                    "duration": "30 Days PRN",
                    "instructions": "Shake canister well, rinse mouth with water after inhaling",
                    "status": "Approved",
                    "recommended_tests": "Peak Expiratory Flow (PEF) diary",
                    "verification_notes": "Clinically verified for acute bronchodilation.",
                    "pharmacist_name": "Dr. Shalini Verma, B.Pharm, PharmD (Reg #PHA-DL-8492)"
                }
            ]
            for rx in sample_prescriptions:
                cur.execute(
                    "INSERT INTO prescriptions (prescription_id, data, status) VALUES (?, ?, ?)",
                    (rx["prescription_id"], json.dumps(rx), rx["status"])
                )

        # Seed Reminders
        cur.execute("SELECT count(*) as cnt FROM reminders")
        if cur.fetchone()["cnt"] == 0:
            sample_reminders = [
                {
                    "id": "rem-1",
                    "medicine_id": "med-aug-625",
                    "medicine_name": "Augmentin 625 Duo Tablet",
                    "dosage_form": "Tablet",
                    "scheduled_time": "08:00 AM",
                    "meal_timing": "After Breakfast",
                    "frequency": "Twice Daily",
                    "prescription_ref": "RX-2026-9041",
                    "instructions": "Take with full glass of water after food",
                    "active": True
                },
                {
                    "id": "rem-2",
                    "medicine_id": "med-asth-100",
                    "medicine_name": "Asthalin Inhaler 100 mcg",
                    "dosage_form": "Inhaler",
                    "scheduled_time": "02:00 PM",
                    "meal_timing": "Mid-day Dose",
                    "frequency": "As Needed / 2 Puffs",
                    "prescription_ref": "RX-2026-9042",
                    "instructions": "Shake canister well, 2 actuations, rinse mouth",
                    "active": True
                },
                {
                    "id": "rem-3",
                    "medicine_id": "med-bena-100",
                    "medicine_name": "Benadryl Cough Syrup (100ml)",
                    "dosage_form": "Syrup",
                    "scheduled_time": "09:00 PM",
                    "meal_timing": "Before Sleep",
                    "frequency": "Once at Night",
                    "prescription_ref": "OTC-DIRECT",
                    "instructions": "10 ml measuring cup, avoid driving afterwards",
                    "active": True
                },
                {
                    "id": "rem-4",
                    "medicine_id": "med-beco-z",
                    "medicine_name": "Becosules Z Capsules",
                    "dosage_form": "Capsule",
                    "scheduled_time": "01:00 PM",
                    "meal_timing": "After Lunch",
                    "frequency": "Daily Once",
                    "prescription_ref": "OTC-DIRECT",
                    "instructions": "Swallow with water after lunch",
                    "active": True
                }
            ]
            for rem in sample_reminders:
                cur.execute("INSERT INTO reminders (id, data) VALUES (?, ?)", (rem["id"], json.dumps(rem)))

        # Seed Adherence Logs
        cur.execute("SELECT count(*) as cnt FROM adherence_logs")
        if cur.fetchone()["cnt"] == 0:
            sample_adherence = [
                {"day": "Monday", "date": "2026-09-28", "medicine_name": "Augmentin 625 Duo Tablet", "scheduled_time": "08:00 AM", "actual_time": "08:06 AM", "status": "Taken", "prescription_ref": "RX-2026-9041", "notes": "Taken with warm water"},
                {"day": "Tuesday", "date": "2026-09-29", "medicine_name": "Augmentin 625 Duo Tablet", "scheduled_time": "08:00 AM", "actual_time": "08:12 AM", "status": "Taken", "prescription_ref": "RX-2026-9041", "notes": "Dose confirmed on time"},
                {"day": "Wednesday", "date": "2026-09-30", "medicine_name": "Augmentin 625 Duo Tablet", "scheduled_time": "08:00 AM", "actual_time": "--", "status": "Missed", "prescription_ref": "RX-2026-9041", "notes": "Missed due to transit"},
                {"day": "Thursday", "date": "2026-10-01", "medicine_name": "Augmentin 625 Duo Tablet", "scheduled_time": "08:00 AM", "actual_time": "08:15 AM", "status": "Taken", "prescription_ref": "RX-2026-9041", "notes": "Taken after breakfast"},
                {"day": "Friday", "date": "2026-10-02", "medicine_name": "Augmentin 625 Duo Tablet", "scheduled_time": "08:00 AM", "actual_time": "08:05 AM", "status": "Taken", "prescription_ref": "RX-2026-9041", "notes": "Taken on time"},
                {"day": "Saturday", "date": "2026-10-03", "medicine_name": "Augmentin 625 Duo Tablet", "scheduled_time": "08:00 AM", "actual_time": "08:20 AM", "status": "Taken", "prescription_ref": "RX-2026-9041", "notes": "Weekend dose logged"},
                {"day": "Sunday", "date": "2026-10-04", "medicine_name": "Augmentin 625 Duo Tablet", "scheduled_time": "08:00 AM", "actual_time": "08:08 AM", "status": "Taken", "prescription_ref": "RX-2026-9041", "notes": "Completed morning dose"}
            ]
            for adh in sample_adherence:
                cur.execute("INSERT INTO adherence_logs (data) VALUES (?)", (json.dumps(adh),))

        # Seed Health Vitals / Measurements
        cur.execute("SELECT count(*) as cnt FROM health_measurements")
        if cur.fetchone()["cnt"] == 0:
            sample_vitals = [
                ("vm-1", "usr-patient-1", "blood_pressure", 120.0, 80.0, "mmHg", "Resting morning", 0, "Normal resting BP"),
                ("vm-2", "usr-patient-1", "glucose", 98.0, None, "mg/dL", "Fasting", 0, "Optimal fasting glycemic index"),
                ("vm-3", "usr-patient-1", "heart_rate", 72.0, None, "BPM", "Resting pulse", 0, "Regular sinus rhythm"),
                ("vm-4", "usr-patient-1", "spo2", 98.0, None, "%", "Room air", 0, "Healthy arterial oxygenation"),
                ("vm-5", "usr-patient-1", "weight", 70.5, None, "kg", "Morning weigh-in", 0, "BMI: 23.4 (Normal range)"),
                ("vm-6", "usr-patient-1", "temperature", 98.4, None, "°F", "Oral basal", 0, "Afebrile")
            ]
            for v in sample_vitals:
                cur.execute(
                    "INSERT INTO health_measurements (id, user_id, measurement_type, value_primary, value_secondary, unit, context, alert_flag, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    v
                )

        # Seed Medical Reports
        cur.execute("SELECT count(*) as cnt FROM medical_reports")
        if cur.fetchone()["cnt"] == 0:
            sample_reports = [
                ("rep-1", "usr-patient-1", "Complete Blood Count & Metabolic Panel", "Blood Test", "CBC_Metabolic_Report_2026.pdf", "/uploads/reports/cbc_sample.pdf", 450.0, "HealthGuard Central PathLab", "2026-10-02", "Hemoglobin 14.8 g/dL, Fasting Sugar 98 mg/dL, Normal renal function."),
                ("rep-2", "usr-patient-1", "Chest Radiograph PA View", "X-Ray", "Chest_XRay_PA_View.jpg", "/uploads/reports/xray_sample.jpg", 1200.0, "Apex Diagnostic Imaging", "2026-10-04", "Clear lung fields, no focal consolidation, normal cardiac shadow.")
            ]
            for r in sample_reports:
                cur.execute(
                    "INSERT INTO medical_reports (id, user_id, title, report_type, file_name, file_path, file_size_kb, doctor_lab, report_date, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    r
                )

        # Seed Appointments
        cur.execute("SELECT count(*) as cnt FROM appointments")
        if cur.fetchone()["cnt"] == 0:
            sample_appts = [
                ("apt-1", "usr-patient-1", "Manik Sharma", "usr-doctor-1", "Dr. Priya Nair, MD", "2026-10-14", "10:30 AM", "Scheduled", "10-day post-antibiotic pulmonary follow-up and spirometry check", "Clinic Room 304"),
                ("apt-2", "usr-patient-1", "Manik Sharma", "usr-doctor-2", "Dr. Rajesh Sharma, MD, DM", "2026-11-28", "11:00 AM", "Scheduled", "Routine metabolic & lipid monitoring consultation", "Cardiology Suite B")
            ]
            for a in sample_appts:
                cur.execute(
                    "INSERT INTO appointments (id, patient_id, patient_name, doctor_id, doctor_name, appointment_date, time_slot, status, reason, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    a
                )

        # Seed Preventive Care / Annual Checkups
        cur.execute("SELECT count(*) as cnt FROM checkups")
        if cur.fetchone()["cnt"] == 0:
            now = datetime.now()
            last_checkup = (now - timedelta(days=320)).strftime("%Y-%m-%d")
            next_annual = (datetime.strptime(last_checkup, "%Y-%m-%d") + timedelta(days=365)).strftime("%Y-%m-%d")
            sample_checkups = [
                ("chk-1", "usr-patient-1", "Comprehensive Annual Health Checkup", "Annual Health Checkup", last_checkup, next_annual, 1, "Includes full blood panel, lipid profile, ECG, liver & renal functions."),
                ("chk-2", "usr-patient-1", "Routine Dental Clean & Prophylaxis", "Dental", (now - timedelta(days=120)).strftime("%Y-%m-%d"), (now + timedelta(days=60)).strftime("%Y-%m-%d"), 1, "Twice yearly preventative oral hygiene."),
                ("chk-3", "usr-patient-1", "Seasonal Influenza Vaccination", "Vaccination", (now - timedelta(days=200)).strftime("%Y-%m-%d"), (now + timedelta(days=165)).strftime("%Y-%m-%d"), 1, "Annual quadrivalent influenza immunisation.")
            ]
            for c in sample_checkups:
                cur.execute(
                    "INSERT INTO checkups (id, user_id, title, category, last_completed_date, next_due_date, reminder_enabled, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    c
                )

        # Seed Unified Health Timeline
        cur.execute("SELECT count(*) as cnt FROM health_timeline")
        if cur.fetchone()["cnt"] == 0:
            events = [
                ("evt-1", "usr-patient-1", "appointment", "Doctor Consultation Completed", "Consulted Dr. Priya Nair, MD for acute bronchospasm.", "CNS-2026-8801", "2026-10-04 11:30:00"),
                ("evt-2", "usr-patient-1", "prescription", "Digital Prescription Issued", "Prescription #RX-2026-9041 created for Augmentin 625 & Asthalin.", "RX-2026-9041", "2026-10-04 11:45:00"),
                ("evt-3", "usr-patient-1", "report", "Diagnostic Chest X-Ray Uploaded", "Apex Diagnostic Imaging confirmed clear lung fields.", "rep-2", "2026-10-04 13:00:00"),
                ("evt-4", "usr-patient-1", "purchase", "Medicine Order #HG-89412 Dispatched", "Ordered Augmentin 625 & Dolo 650 with pharmacist clearance.", "HG-89412", "2026-10-04 14:22:00"),
                ("evt-5", "usr-patient-1", "reminder", "Medication Reminder Triggered", "Morning 8:00 AM dose taken and verified in 3D reminder.", "rem-1", "2026-10-04 08:08:00"),
                ("evt-6", "usr-patient-1", "vitals", "Health Vitals Recorded", "Resting BP: 120/80 mmHg, SpO2: 98%, Heart Rate: 72 BPM.", "vm-1", "2026-10-04 08:15:00")
            ]
            for ev in events:
                cur.execute(
                    "INSERT INTO health_timeline (id, user_id, event_type, event_title, event_desc, ref_id, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    ev
                )

        # Seed Notifications
        cur.execute("SELECT count(*) as cnt FROM notifications")
        if cur.fetchone()["cnt"] == 0:
            sample_notifs = [
                ("notif-1", "usr-patient-1", json.dumps({
                    "id": "notif-1",
                    "type": "medicine_reminder",
                    "title": "💊 Medication Reminder: Augmentin 625 Duo",
                    "message": "It is time for your scheduled 8:00 AM morning dose. Take 1 tablet with water after breakfast.",
                    "time": "Just now",
                    "read": False,
                    "action": "open_3d_reminder",
                    "target_medicine_id": "med-aug-625"
                }), 0),
                ("notif-2", "usr-patient-1", json.dumps({
                    "id": "notif-2",
                    "type": "prescription_approval",
                    "title": "✅ Prescription Approved by Pharmacist",
                    "message": "Prescription #RX-2026-9041 from Dr. Priya Nair has been clinically approved by Licensed Pharmacist Dr. Shalini Verma (Reg #PHA-DL-8492).",
                    "time": "2 hours ago",
                    "read": False,
                    "action": "view_prescription",
                    "target_prescription_id": "RX-2026-9041"
                }), 0),
                ("notif-3", "usr-patient-1", json.dumps({
                    "id": "notif-3",
                    "type": "order_shipment",
                    "title": "🚚 Order #HG-89412 Dispatched",
                    "message": "Your medicine package is out for delivery with HealthGuard ColdChain Express.",
                    "time": "Yesterday",
                    "read": True,
                    "action": "view_order",
                    "target_order_id": "HG-89412"
                }), 1),
                ("notif-4", "usr-patient-1", json.dumps({
                    "id": "notif-4",
                    "type": "doctor_appointment",
                    "title": "🩺 Doctor Follow-up Scheduled",
                    "message": "Clinical follow-up with Dr. Priya Nair scheduled for 2026-10-14 at 10:30 AM.",
                    "time": "3 days ago",
                    "read": True,
                    "action": "view_appointments"
                }), 1)
            ]
            for n in sample_notifs:
                cur.execute("INSERT INTO notifications (id, user_id, data, is_read) VALUES (?, ?, ?, ?)", n)

    # ==========================================
    # AUTHENTICATION & USER MANAGEMENT
    # ==========================================
    def authenticate_user(self, email, password):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE lower(email) = lower(?)", (email.strip(),))
        row = cur.fetchone()
        conn.close()

        if not row:
            return {"error": "Invalid email or password"}

        if not verify_password(password, row["password_hash"], row["salt"]):
            return {"error": "Invalid email or password"}

        user = dict(row)
        del user["password_hash"]
        del user["salt"]

        # Fetch corresponding profile
        profile = self.get_user_profile(user["id"], user["role"])
        user["profile"] = profile

        # Log audit entry
        self.log_audit_event(user["id"], "LOGIN", f"User logged in as {user['role']}")

        return {"user": user, "token": f"hg_token_{user['id']}_{int(datetime.now().timestamp())}"}

    def register_user(self, email, password, role, name, phone="", profile_data=None):
        role = role.lower()
        if role not in ("patient", "doctor", "admin"):
            return {"error": "Invalid role specified"}

        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE lower(email) = lower(?)", (email.strip(),))
        if cur.fetchone():
            conn.close()
            return {"error": "An account with this email already exists"}

        user_id = f"usr-{role}-{secrets.token_hex(4)}"
        p_hash, salt = hash_password(password)

        cur.execute(
            "INSERT INTO users (id, email, password_hash, salt, role, name, phone) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, email.strip().lower(), p_hash, salt, role, name.strip(), phone.strip())
        )

        # Profile insertion
        profile_data = profile_data or {}
        if role == "patient":
            cur.execute(
                "INSERT INTO patients (user_id, age, gender, blood_group, allergies, emergency_contact, address) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (user_id, profile_data.get("age", 25), profile_data.get("gender", "Not Specified"), profile_data.get("blood_group", "O+"), profile_data.get("allergies", "None"), profile_data.get("emergency_contact", ""), profile_data.get("address", ""))
            )
        elif role == "doctor":
            cur.execute(
                "INSERT INTO doctors (user_id, specialization, reg_number, hospital, experience_years, bio, consultation_fee, availability_hours, verified_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (user_id, profile_data.get("specialization", "General Medicine"), profile_data.get("reg_number", "MCI-PENDING"), profile_data.get("hospital", "HealthGuard Clinic"), profile_data.get("experience_years", 5), profile_data.get("bio", ""), profile_data.get("consultation_fee", 500.0), profile_data.get("availability_hours", "Mon-Fri: 10AM - 4PM"), "Pending")
            )

        conn.commit()
        conn.close()

        self.log_audit_event(user_id, "REGISTER", f"New user registered with role {role}")
        return self.authenticate_user(email, password)

    def get_user_by_id(self, user_id):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, email, role, name, phone, created_at FROM users WHERE id = ?", (user_id,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        user = dict(row)
        user["profile"] = self.get_user_profile(user["id"], user["role"])
        return user

    def get_user_profile(self, user_id, role):
        conn = self.get_connection()
        cur = conn.cursor()
        if role == "patient":
            cur.execute("SELECT * FROM patients WHERE user_id = ?", (user_id,))
            row = cur.fetchone()
            conn.close()
            return dict(row) if row else {}
        elif role == "doctor":
            cur.execute("SELECT * FROM doctors WHERE user_id = ?", (user_id,))
            row = cur.fetchone()
            conn.close()
            return dict(row) if row else {}
        conn.close()
        return {}

    def update_patient_profile(self, user_id, age, gender, blood_group, allergies, emergency_contact, address):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO patients (user_id, age, gender, blood_group, allergies, emergency_contact, address)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                age=excluded.age,
                gender=excluded.gender,
                blood_group=excluded.blood_group,
                allergies=excluded.allergies,
                emergency_contact=excluded.emergency_contact,
                address=excluded.address
        """, (user_id, age, gender, blood_group, allergies, emergency_contact, address))
        conn.commit()
        conn.close()
        return self.get_user_profile(user_id, "patient")

    def list_all_users(self):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, email, role, name, phone, created_at FROM users ORDER BY created_at DESC")
        rows = cur.fetchall()
        conn.close()
        users = []
        for r in rows:
            u = dict(r)
            u["profile"] = self.get_user_profile(u["id"], u["role"])
            users.append(u)
        return users

    # ==========================================
    # DOCTORS & APPOINTMENTS
    # ==========================================
    def get_doctors(self, specialization=None):
        conn = self.get_connection()
        cur = conn.cursor()
        query = """
            SELECT u.id, u.name, u.email, u.phone, d.specialization, d.reg_number,
                   d.hospital, d.experience_years, d.bio, d.consultation_fee,
                   d.availability_hours, d.verified_status
            FROM users u
            JOIN doctors d ON u.id = d.user_id
            WHERE 1=1
        """
        params = []
        if specialization and specialization.lower() != "all":
            query += " AND lower(d.specialization) LIKE ?"
            params.append(f"%{specialization.lower()}%")

        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def update_doctor_verification(self, doctor_id, status):
        status = status.capitalize()
        if status not in ("Approved", "Rejected", "Pending"):
            return {"error": "Invalid verification status"}
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE doctors SET verified_status = ? WHERE user_id = ?", (status, doctor_id))
        conn.commit()
        conn.close()
        self.log_audit_event("admin", "DOCTOR_VERIFY", f"Doctor {doctor_id} status set to {status}")
        return {"status": "ok", "doctor_id": doctor_id, "verified_status": status}

    def get_appointments(self, user_id=None, role="patient"):
        conn = self.get_connection()
        cur = conn.cursor()
        if user_id:
            if role == "doctor":
                cur.execute("SELECT * FROM appointments WHERE doctor_id = ? ORDER BY appointment_date ASC", (user_id,))
            else:
                cur.execute("SELECT * FROM appointments WHERE patient_id = ? ORDER BY appointment_date ASC", (user_id,))
        else:
            cur.execute("SELECT * FROM appointments ORDER BY appointment_date ASC")
        rows = cur.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def create_appointment(self, patient_id, patient_name, doctor_id, doctor_name, date_str, time_slot, reason=""):
        apt_id = f"apt-{int(datetime.now().timestamp()) % 100000:05d}"
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO appointments (id, patient_id, patient_name, doctor_id, doctor_name, appointment_date, time_slot, status, reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'Scheduled', ?)
        """, (apt_id, patient_id, patient_name, doctor_id, doctor_name, date_str, time_slot, reason))

        # Add to patient's health timeline
        self.add_timeline_event(
            user_id=patient_id,
            event_type="appointment",
            event_title=f"Appointment Booked with {doctor_name}",
            event_desc=f"Scheduled on {date_str} at {time_slot}. Reason: {reason}",
            ref_id=apt_id
        )

        # Notify patient
        self.create_notification(
            user_id=patient_id,
            notif_type="appointment_reminder",
            title=f"🩺 Appointment Confirmed with {doctor_name}",
            message=f"Your consultation is booked for {date_str} at {time_slot}.",
            action="view_appointments"
        )

        conn.commit()
        conn.close()
        return {"id": apt_id, "status": "Scheduled", "date": date_str, "time": time_slot}

    def update_appointment_status(self, apt_id, new_status, notes=""):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE appointments SET status = ?, notes = ? WHERE id = ?", (new_status, notes, apt_id))
        conn.commit()
        conn.close()
        return {"status": "ok", "appointment_id": apt_id, "new_status": new_status}

    # ==========================================
    # HEALTH MONITORING & VITALS
    # ==========================================
    def add_health_measurement(self, user_id, measurement_type, val_primary, val_secondary=None, unit="", context="", notes=""):
        meas_id = f"vm-{int(datetime.now().timestamp()) % 100000:05d}"

        # Clinical Reference Range Evaluation (Strictly neutral phrasing)
        alert_flag = 0
        guidance = "Recorded value is within standard reference ranges."

        if measurement_type == "blood_pressure":
            unit = unit or "mmHg"
            systolic = val_primary
            diastolic = val_secondary or 80.0
            if systolic > 140 or diastolic > 90 or systolic < 90 or diastolic < 60:
                alert_flag = 1
                guidance = "Your recorded blood pressure is outside the configured reference range. Consider contacting your healthcare professional."
                if systolic >= 180 or diastolic >= 120:
                    guidance = "Recorded value indicates significant elevation. If accompanied by chest pain, shortness of breath, or numbness, please seek immediate emergency medical evaluation."
        elif measurement_type == "glucose":
            unit = unit or "mg/dL"
            if val_primary > 140 or val_primary < 70:
                alert_flag = 1
                guidance = "Your recorded glucose value is outside the configured reference range. Consider contacting your healthcare professional."
                if val_primary < 55:
                    guidance = "Low glucose detected. Consume rapid-acting carbohydrate if conscious and seek urgent medical evaluation if symptoms persist."
        elif measurement_type == "spo2":
            unit = unit or "%"
            if val_primary < 95:
                alert_flag = 1
                guidance = "Your recorded oxygen saturation is outside the standard reference range (>95%). If shortness of breath is present, seek immediate professional medical evaluation."
        elif measurement_type == "heart_rate":
            unit = unit or "BPM"
            if val_primary > 100 or val_primary < 50:
                alert_flag = 1
                guidance = "Recorded heart rate is outside the standard resting range (50-100 BPM). Consider resting and contacting a healthcare provider if sustained."

        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO health_measurements (id, user_id, measurement_type, value_primary, value_secondary, unit, context, alert_flag, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (meas_id, user_id, measurement_type, val_primary, val_secondary, unit, context, alert_flag, notes or guidance))

        # Add to timeline
        self.add_timeline_event(
            user_id=user_id,
            event_type="vitals",
            event_title=f"Recorded {measurement_type.replace('_', ' ').title()}",
            event_desc=f"{val_primary}{('/' + str(val_secondary)) if val_secondary else ''} {unit} ({context or 'Resting'}). {guidance}",
            ref_id=meas_id
        )

        conn.commit()
        conn.close()

        return {
            "id": meas_id,
            "type": measurement_type,
            "value_primary": val_primary,
            "value_secondary": val_secondary,
            "unit": unit,
            "alert_flag": alert_flag,
            "guidance": guidance
        }

    def get_health_measurements(self, user_id, measurement_type=None, days_limit=30):
        conn = self.get_connection()
        cur = conn.cursor()
        query = "SELECT * FROM health_measurements WHERE user_id = ?"
        params = [user_id]
        if measurement_type:
            query += " AND measurement_type = ?"
            params.append(measurement_type)
        query += " ORDER BY timestamp DESC"
        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_latest_vitals_summary(self, user_id):
        # Fetch the most recent reading for each measurement type
        types = ["blood_pressure", "glucose", "heart_rate", "spo2", "weight", "temperature"]
        summary = {}
        for t in types:
            records = self.get_health_measurements(user_id, measurement_type=t, days_limit=30)
            if records:
                summary[t] = records[0]
            else:
                summary[t] = None
        return summary

    # ==========================================
    # MEDICAL REPORTS VAULT & AI ASSISTANT
    # ==========================================
    def add_medical_report(self, user_id, title, report_type, file_name, file_path, file_size_kb, doctor_lab, report_date, notes=""):
        rep_id = f"rep-{int(datetime.now().timestamp()) % 100000:05d}"
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO medical_reports (id, user_id, title, report_type, file_name, file_path, file_size_kb, doctor_lab, report_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (rep_id, user_id, title, report_type, file_name, file_path, file_size_kb, doctor_lab, report_date, notes))

        # Add to timeline
        self.add_timeline_event(
            user_id=user_id,
            event_type="report",
            event_title=f"Uploaded Medical Report: {title}",
            event_desc=f"{report_type} issued by {doctor_lab} on {report_date}.",
            ref_id=rep_id
        )

        # Notify
        self.create_notification(
            user_id=user_id,
            notif_type="report_upload",
            title="📄 Medical Report Saved",
            message=f"'{title}' was securely vaulted in your health records.",
            action="view_reports"
        )

        conn.commit()
        conn.close()
        return {"id": rep_id, "title": title, "status": "Uploaded"}

    def get_medical_reports(self, user_id):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM medical_reports WHERE user_id = ? ORDER BY report_date DESC", (user_id,))
        rows = cur.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def delete_medical_report(self, report_id, user_id):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM medical_reports WHERE id = ? AND user_id = ?", (report_id, user_id))
        conn.commit()
        conn.close()
        return {"status": "ok"}

    def explain_medical_term_or_report(self, query_term):
        term_clean = query_term.lower().strip()
        matched = None
        for key, item in AI_MEDICAL_TERMS.items():
            if key in term_clean or term_clean in key:
                matched = item
                break

        disclaimer = "⚠️ DISCLAIMER: This explanation is for educational purposes only and does NOT replace professional medical advice, clinical diagnosis, or treatment. Do not discontinue, adjust, or start any medications based on this summary."

        if matched:
            return {
                "term": matched["term"],
                "standard_range": matched["standard_range"],
                "educational_meaning": matched["meaning"],
                "clinical_context": matched["context"],
                "disclaimer": disclaimer
            }

        return {
            "term": query_term,
            "standard_range": "Varies by clinical laboratory and patient demographic",
            "educational_meaning": f"The term '{query_term}' refers to a specialized diagnostic test or physiological marker.",
            "clinical_context": "Individual lab ranges vary depending on reference reagents, gender, age, and pre-existing medical conditions. Please discuss your specific test values directly with your physician.",
            "disclaimer": disclaimer
        }

    # ==========================================
    # PREVENTIVE HEALTHCARE & CHECKUPS
    # ==========================================
    def get_checkups(self, user_id):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM checkups WHERE user_id = ? ORDER BY next_due_date ASC", (user_id,))
        rows = cur.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def add_or_update_checkup(self, user_id, title, category, last_completed_date=None, next_due_date=None, notes=""):
        chk_id = f"chk-{secrets.token_hex(3)}"
        if last_completed_date and not next_due_date:
            # Auto-calculate ~1 year for annual checkups
            try:
                dt = datetime.strptime(last_completed_date, "%Y-%m-%d")
                next_due_date = (dt + timedelta(days=365)).strftime("%Y-%m-%d")
            except Exception:
                next_due_date = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")

        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO checkups (id, user_id, title, category, last_completed_date, next_due_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (chk_id, user_id, title, category, last_completed_date, next_due_date, notes))
        conn.commit()
        conn.close()
        return {"id": chk_id, "title": title, "next_due_date": next_due_date}

    # ==========================================
    # UNIFIED HEALTH TIMELINE
    # ==========================================
    def get_health_timeline(self, user_id, event_type=None):
        conn = self.get_connection()
        cur = conn.cursor()
        query = "SELECT * FROM health_timeline WHERE user_id = ?"
        params = [user_id]
        if event_type and event_type.lower() != "all":
            query += " AND event_type = ?"
            params.append(event_type.lower())
        query += " ORDER BY timestamp DESC"
        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def add_timeline_event(self, user_id, event_type, event_title, event_desc="", ref_id=""):
        evt_id = f"evt-{int(datetime.now().timestamp()) % 100000:05d}"
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO health_timeline (id, user_id, event_type, event_title, event_desc, ref_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (evt_id, user_id, event_type, event_title, event_desc, ref_id))
        conn.commit()
        conn.close()

    # ==========================================
    # NOTIFICATIONS & AUDIT LOGS
    # ==========================================
    def create_notification(self, user_id, notif_type, title, message, action="view", target_id=""):
        notif_id = f"notif-{int(datetime.now().timestamp() * 1000) % 1000000}"
        notif_data = {
            "id": notif_id,
            "type": notif_type,
            "title": title,
            "message": message,
            "time": "Just now",
            "read": False,
            "action": action,
            "target_id": target_id
        }
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO notifications (id, user_id, data, is_read) VALUES (?, ?, ?, 0)",
            (notif_id, user_id, json.dumps(notif_data))
        )
        conn.commit()
        conn.close()
        return notif_data

    def get_notifications(self, user_id=None):
        conn = self.get_connection()
        cur = conn.cursor()
        if user_id:
            cur.execute("SELECT data, is_read FROM notifications WHERE user_id = ? OR user_id IS NULL ORDER BY created_at DESC", (user_id,))
        else:
            cur.execute("SELECT data, is_read FROM notifications ORDER BY created_at DESC")
        rows = cur.fetchall()
        conn.close()
        items = []
        for row in rows:
            data = json.loads(row["data"])
            data["read"] = bool(row["is_read"])
            items.append(data)
        return items

    def mark_notification_read(self, notif_id):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE notifications SET is_read = 1 WHERE id = ?", (notif_id,))
        conn.commit()
        conn.close()
        return {"status": "ok"}

    def log_audit_event(self, user_id, action, details=""):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO audit_logs (user_id, action, details) VALUES (?, ?, ?)",
            (user_id, action, details)
        )
        conn.commit()
        conn.close()

    def get_audit_logs(self, limit=50):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT ?", (limit,))
        rows = cur.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_system_stats(self):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM users")
        u_count = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM doctors")
        d_count = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM orders")
        o_count = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM prescriptions")
        p_count = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM medical_reports")
        r_count = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM appointments")
        a_count = cur.fetchone()[0]
        conn.close()

        return {
            "total_users": u_count,
            "total_doctors": d_count,
            "total_medicines": len(MEDICINES_CATALOG),
            "total_orders": o_count,
            "total_prescriptions": p_count,
            "total_reports": r_count,
            "total_appointments": a_count,
            "system_uptime": "99.98%",
            "database_size_kb": round(os.path.getsize(DB_PATH) / 1024, 1) if os.path.exists(DB_PATH) else 0
        }

    # ==========================================
    # PRESERVED EXISTING METHODS (MEDICINES, CART, ORDERS, ADHERENCE)
    # ==========================================
    def get_medicines(self, search="", category="", dosage_form="", prescription_req=None, min_price=None, max_price=None, sort_by=None):
        results = []
        search_lower = search.lower().strip() if search else ""
        cat_lower = category.lower().strip() if category else ""
        form_lower = dosage_form.lower().strip() if dosage_form else ""

        for med in MEDICINES_CATALOG:
            if search_lower:
                match = (
                    search_lower in med["name"].lower() or
                    search_lower in med["generic_name"].lower() or
                    search_lower in med["brand"].lower() or
                    search_lower in med["manufacturer"].lower() or
                    search_lower in med["category"].lower() or
                    search_lower in med["uses"].lower()
                )
                if not match:
                    continue

            if cat_lower and cat_lower != "all":
                if cat_lower not in med["category"].lower():
                    continue

            if form_lower and form_lower != "all":
                if form_lower not in med["dosage_form"].lower():
                    continue

            if prescription_req is not None:
                if med["prescription_required"] != prescription_req:
                    continue

            if min_price is not None and med["price"] < min_price:
                continue
            if max_price is not None and med["price"] > max_price:
                continue

            results.append(med)

        if sort_by == "price_asc":
            results.sort(key=lambda m: m["price"])
        elif sort_by == "price_desc":
            results.sort(key=lambda m: m["price"], reverse=True)
        elif sort_by == "name_asc":
            results.sort(key=lambda m: m["name"])

        return results

    def get_medicine_by_id(self, med_id):
        for med in MEDICINES_CATALOG:
            if med["id"] == med_id:
                return med
        return None

    def get_cart(self):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT medicine_id, quantity FROM cart_items")
        rows = cur.fetchall()
        conn.close()

        items = []
        subtotal = 0.0
        rx_required_in_cart = False

        for row in rows:
            med = self.get_medicine_by_id(row["medicine_id"])
            if med:
                item_total = round(med["price"] * row["quantity"], 2)
                subtotal += item_total
                if med["prescription_required"]:
                    rx_required_in_cart = True
                items.append({
                    "medicine": med,
                    "quantity": row["quantity"],
                    "item_total": item_total
                })

        subtotal = round(subtotal, 2)
        delivery = 0.0 if subtotal >= 500 or subtotal == 0 else 49.0
        total = round(subtotal + delivery, 2)

        return {
            "items": items,
            "subtotal": subtotal,
            "delivery_fee": delivery,
            "total": total,
            "rx_required": rx_required_in_cart,
            "free_delivery_threshold": 500.0,
            "amount_for_free_delivery": max(0.0, round(500.0 - subtotal, 2))
        }

    def add_to_cart(self, medicine_id, quantity=1):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT quantity FROM cart_items WHERE medicine_id = ?", (medicine_id,))
        row = cur.fetchone()
        if row:
            new_qty = row["quantity"] + quantity
            cur.execute("UPDATE cart_items SET quantity = ? WHERE medicine_id = ?", (new_qty, medicine_id))
        else:
            cur.execute("INSERT INTO cart_items (medicine_id, quantity) VALUES (?, ?)", (medicine_id, quantity))
        conn.commit()
        conn.close()
        return self.get_cart()

    def update_cart_quantity(self, medicine_id, quantity):
        conn = self.get_connection()
        cur = conn.cursor()
        if quantity <= 0:
            cur.execute("DELETE FROM cart_items WHERE medicine_id = ?", (medicine_id,))
        else:
            cur.execute("UPDATE cart_items SET quantity = ? WHERE medicine_id = ?", (quantity, medicine_id))
        conn.commit()
        conn.close()
        return self.get_cart()

    def clear_cart(self):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM cart_items")
        conn.commit()
        conn.close()

    def create_order(self, delivery_address, prescription_id=None, coupon_code="", user_id="usr-patient-1"):
        cart = self.get_cart()
        if not cart["items"]:
            return {"error": "Cart is empty"}

        subtotal = cart["subtotal"]
        discount = 0.0
        delivery_fee = cart["delivery_fee"]

        if coupon_code.upper() == "HEALTH20":
            discount = round(subtotal * 0.20, 2)
        elif coupon_code.upper() == "FIRSTMED":
            discount = min(subtotal, 100.0)
        elif coupon_code.upper() == "FREESHIP":
            delivery_fee = 0.0

        final_total = max(0.0, round(subtotal - discount + delivery_fee, 2))
        order_id = f"HG-{int(datetime.now().timestamp()) % 100000:05d}"
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

        order_items = []
        for item in cart["items"]:
            order_items.append({
                "id": item["medicine"]["id"],
                "name": item["medicine"]["name"],
                "generic_name": item["medicine"]["generic_name"],
                "dosage_form": item["medicine"]["dosage_form"],
                "pack_size": item["medicine"]["pack_size"],
                "price": item["medicine"]["price"],
                "quantity": item["quantity"],
                "image": item["medicine"]["gallery"]["main"]
            })

        order_data = {
            "order_id": order_id,
            "order_date": now_str,
            "status": "Confirmed",
            "stage_index": 1,
            "estimated_delivery": (datetime.now() + timedelta(days=1)).strftime("%b %d, %Y by 2:00 PM"),
            "tracking_number": f"HG-EXP-{int(datetime.now().timestamp()) % 1000000:06d}",
            "courier": "HealthGuard ColdChain Express",
            "delivery_address": delivery_address,
            "prescription_id": prescription_id or "Not Required (OTC)",
            "pharmacist_reviewer": "Dr. Shalini Verma (Reg #PHA-DL-8492)" if prescription_id else "OTC Direct Verification",
            "items": order_items,
            "subtotal": subtotal,
            "discount": discount,
            "coupon_code": coupon_code.upper() if coupon_code else None,
            "delivery_fee": delivery_fee,
            "total": final_total,
            "payment_method": "HealthGuard Instant Pay / UPI"
        }

        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO orders (order_id, user_id, data) VALUES (?, ?, ?)",
            (order_id, user_id, json.dumps(order_data))
        )
        cur.execute("DELETE FROM cart_items")

        # Notification & Timeline
        self.create_notification(
            user_id=user_id,
            notif_type="order_confirmation",
            title=f"🎉 Order Confirmed #{order_id}",
            message=f"Order of {len(order_items)} item(s) total ₹{final_total} confirmed and queued for dispatch.",
            action="view_order",
            target_id=order_id
        )

        self.add_timeline_event(
            user_id=user_id,
            event_type="purchase",
            event_title=f"Order Placed #{order_id}",
            event_desc=f"{len(order_items)} items total ₹{final_total}. Courier: HealthGuard ColdChain Express.",
            ref_id=order_id
        )

        # Auto-schedule 3D medicine reminders for purchased items
        for item in cart["items"]:
            med = item["medicine"]
            rem_id = f"rem-auto-{med['id']}"
            cur.execute("SELECT id FROM reminders WHERE id = ?", (rem_id,))
            if not cur.fetchone():
                rem_data = {
                    "id": rem_id,
                    "medicine_id": med["id"],
                    "medicine_name": med["name"],
                    "dosage_form": med["dosage_form"],
                    "scheduled_time": "08:00 AM",
                    "meal_timing": "Morning Dose",
                    "frequency": "Daily",
                    "prescription_ref": prescription_id or "OTC-ORDER",
                    "instructions": med["dosage_instructions"],
                    "active": True
                }
                cur.execute("INSERT INTO reminders (id, data) VALUES (?, ?)", (rem_id, json.dumps(rem_data)))

        conn.commit()
        conn.close()

        return order_data

    def get_orders(self, user_id=None):
        conn = self.get_connection()
        cur = conn.cursor()
        if user_id:
            cur.execute("SELECT data FROM orders WHERE user_id = ? OR user_id IS NULL ORDER BY created_at DESC", (user_id,))
        else:
            cur.execute("SELECT data FROM orders ORDER BY created_at DESC")
        rows = cur.fetchall()
        conn.close()
        return [json.loads(row["data"]) for row in rows]

    def update_order_status(self, order_id, new_stage_index):
        stages = ["Placed", "Confirmed", "Packed", "Shipped", "Delivered"]
        if new_stage_index < 0 or new_stage_index >= len(stages):
            return {"error": "Invalid stage"}
        status_name = stages[new_stage_index]

        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT data FROM orders WHERE order_id = ?", (order_id,))
        row = cur.fetchone()
        if not row:
            conn.close()
            return {"error": "Order not found"}

        order_data = json.loads(row["data"])
        order_data["stage_index"] = new_stage_index
        order_data["status"] = status_name
        cur.execute("UPDATE orders SET data = ? WHERE order_id = ?", (json.dumps(order_data), order_id))

        self.create_notification(
            user_id="usr-patient-1",
            notif_type=f"order_{status_name.lower()}",
            title=f"📦 Order #{order_id} is now {status_name}",
            message=f"Your package status updated to: {status_name}.",
            action="view_order",
            target_id=order_id
        )

        conn.commit()
        conn.close()
        return order_data

    def get_prescriptions(self):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT data FROM prescriptions ORDER BY created_at DESC")
        rows = cur.fetchall()
        conn.close()
        return [json.loads(row["data"]) for row in rows]

    def upload_prescription(self, doctor_name, patient_name, medicine_id, medicine_name, file_name="prescription_scan.pdf", notes=""):
        rx_id = f"RX-{datetime.now().year}-{int(datetime.now().timestamp()) % 10000:04d}"
        rx_data = {
            "prescription_id": rx_id,
            "consultation_id": "DIRECT-UPLOAD",
            "doctor_name": doctor_name or "Dr. External Physician",
            "doctor_reg": "REG-EXT-2024",
            "patient_name": patient_name or "Manik Sharma",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "medicine_id": medicine_id,
            "medicine_name": medicine_name,
            "dosage": "As per uploaded medical slip",
            "duration": "10 Days",
            "instructions": notes or "Take as directed",
            "file_name": file_name,
            "status": "Pending Review",
            "verification_notes": "Awaiting review by certified HealthGuard pharmacist.",
            "pharmacist_name": "Pending Assignment"
        }

        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO prescriptions (prescription_id, data, status) VALUES (?, ?, ?)",
            (rx_id, json.dumps(rx_data), "Pending Review")
        )

        self.create_notification(
            user_id="usr-patient-1",
            notif_type="prescription_pending",
            title=f"📋 Prescription {rx_id} Uploaded",
            message=f"Prescription for {medicine_name} is under review by the licensed pharmacy team.",
            action="view_prescription",
            target_id=rx_id
        )

        conn.commit()
        conn.close()
        return rx_data

    def create_doctor_prescription(self, doctor_name, doctor_reg, patient_name, medicine_name, dosage, frequency, duration, instructions, follow_up_date="", recommended_tests="", notes=""):
        rx_id = f"RX-{datetime.now().year}-{secrets.token_hex(2).upper()}"
        med = None
        for m in MEDICINES_CATALOG:
            if m["name"].lower() == medicine_name.lower():
                med = m
                break

        rx_data = {
            "prescription_id": rx_id,
            "consultation_id": f"CNS-{secrets.token_hex(3).upper()}",
            "doctor_name": doctor_name,
            "doctor_reg": doctor_reg,
            "patient_name": patient_name,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "medicine_id": med["id"] if med else "med-custom",
            "medicine_name": medicine_name,
            "dosage": f"{dosage} ({frequency})",
            "duration": duration,
            "instructions": instructions,
            "follow_up_date": follow_up_date,
            "recommended_tests": recommended_tests,
            "notes": notes,
            "status": "Approved",
            "verification_notes": f"Digitally issued by licensed practitioner {doctor_name} ({doctor_reg}).",
            "pharmacist_name": "Authorized Clinical Pharmacy"
        }

        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO prescriptions (prescription_id, data, status) VALUES (?, ?, ?)",
            (rx_id, json.dumps(rx_data), "Approved")
        )

        # Add to timeline
        self.add_timeline_event(
            user_id="usr-patient-1",
            event_type="prescription",
            event_title=f"Doctor Issued Prescription #{rx_id}",
            event_desc=f"{doctor_name} prescribed {medicine_name} - {duration}.",
            ref_id=rx_id
        )

        self.create_notification(
            user_id="usr-patient-1",
            notif_type="prescription_approved",
            title=f"📜 New Prescription #{rx_id}",
            message=f"{doctor_name} has issued an electronic prescription for {medicine_name}.",
            action="view_prescription",
            target_id=rx_id
        )

        conn.commit()
        conn.close()
        return rx_data

    def review_prescription(self, prescription_id, action, pharmacist_notes=""):
        new_status = "Approved" if action.lower() == "approve" else "Rejected"
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT data FROM prescriptions WHERE prescription_id = ?", (prescription_id,))
        row = cur.fetchone()
        if not row:
            conn.close()
            return {"error": "Prescription not found"}

        rx_data = json.loads(row["data"])
        rx_data["status"] = new_status
        rx_data["pharmacist_name"] = "Dr. Shalini Verma, B.Pharm, PharmD (Reg #PHA-DL-8492)"
        rx_data["verification_notes"] = pharmacist_notes or ("Clinically verified against state medical council database. Meets all safety guidelines." if new_status == "Approved" else "Rejected: Prescribing details or dosage could not be verified.")

        cur.execute(
            "UPDATE prescriptions SET data = ?, status = ? WHERE prescription_id = ?",
            (json.dumps(rx_data), new_status, prescription_id)
        )

        self.create_notification(
            user_id="usr-patient-1",
            notif_type="prescription_approval" if new_status == "Approved" else "prescription_rejection",
            title=f"{'✅' if new_status == 'Approved' else '❌'} Prescription {prescription_id} {new_status}",
            message=rx_data["verification_notes"],
            action="view_prescription",
            target_id=prescription_id
        )

        conn.commit()
        conn.close()
        return rx_data

    def get_reminders(self):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT data FROM reminders")
        rows = cur.fetchall()
        conn.close()
        return [json.loads(row["data"]) for row in rows]

    def get_adherence_logs(self):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT data FROM adherence_logs ORDER BY id DESC")
        rows = cur.fetchall()
        conn.close()
        logs = [json.loads(row["data"]) for row in rows]

        total = len(logs)
        taken_count = sum(1 for l in logs if l.get("status") == "Taken")
        missed_count = sum(1 for l in logs if l.get("status") == "Missed")
        skipped_count = sum(1 for l in logs if l.get("status") == "Skipped")
        snoozed_count = sum(1 for l in logs if l.get("status") == "Snoozed")
        adherence_rate = round((taken_count / total * 100), 1) if total > 0 else 100.0

        return {
            "logs": logs,
            "total_doses": total,
            "taken": taken_count,
            "missed": missed_count,
            "skipped": skipped_count,
            "snoozed": snoozed_count,
            "adherence_rate": adherence_rate,
            "current_streak_days": 5
        }

    def record_adherence(self, medicine_name, scheduled_time, status, prescription_ref="", notes=""):
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        day_str = now.strftime("%A")
        actual_time = now.strftime("%I:%M %p") if status in ("Taken", "Snoozed") else "--"

        entry = {
            "id": f"adh-{int(now.timestamp())}",
            "day": day_str,
            "date": date_str,
            "medicine_name": medicine_name,
            "scheduled_time": scheduled_time,
            "actual_time": actual_time,
            "status": status,
            "prescription_ref": prescription_ref or "RX-GENERAL",
            "notes": notes or f"Dose marked as {status} by user."
        }

        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO adherence_logs (data) VALUES (?)", (json.dumps(entry),))

        if status == "Missed":
            self.create_notification(
                user_id="usr-patient-1",
                notif_type="missed_medicine",
                title=f"⚠️ Missed Medication: {medicine_name}",
                message=f"You missed your scheduled {scheduled_time} dose of {medicine_name}. Please consult catch-up guidelines.",
                action="open_adherence"
            )

        self.add_timeline_event(
            user_id="usr-patient-1",
            event_type="reminder",
            event_title=f"Medication Dose: {status}",
            event_desc=f"{medicine_name} scheduled at {scheduled_time}. Action: {status}.",
            ref_id=entry["id"]
        )

        conn.commit()
        conn.close()
        return self.get_adherence_logs()

    def get_consultations(self):
        # Build live consultations with current doctors
        docs = self.get_doctors()
        consultations = []
        for i, d in enumerate(docs):
            consultations.append({
                "consultation_id": f"CNS-2026-880{i+1}",
                "doctor_name": d["name"],
                "specialization": d["specialization"],
                "reg_number": d["reg_number"],
                "hospital": d["hospital"],
                "patient_name": "Manik Sharma",
                "patient_age": 28,
                "patient_gender": "Male",
                "date": (datetime.now() - timedelta(days=i*4)).strftime("%Y-%m-%d"),
                "diagnosis": "Clinical evaluation & treatment regimen",
                "clinical_notes": d["bio"],
                "prescriptions": [
                    {
                        "prescription_id": f"RX-2026-904{i+1}",
                        "medicine_id": "med-aug-625" if i==0 else "med-ator-20",
                        "medicine_name": "Augmentin 625 Duo Tablet" if i==0 else "Atorva 20 Tablet",
                        "dosage": "1 tablet daily with meals",
                        "duration": "10 Days",
                        "food_relation": "With food",
                        "quantity": 1,
                        "dosage_form": "Tablet",
                        "status": "Active"
                    }
                ],
                "follow_up_date": (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d"),
                "follow_up_notes": "Clinical review and resolution assessment in 10 days."
            })
        return consultations

# Singleton Database Instance
db = HealthGuardDB()
