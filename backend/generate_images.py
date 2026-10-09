"""
Generate high-fidelity SVG pharmaceutical product images with realistic medical packaging,
macro dosage views, outer carton designs, and back composition layouts.
"""

import os

IMAGE_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend", "images", "medicines")
os.makedirs(IMAGE_DIR, exist_ok=True)

MEDICINE_VISUALS = {
    "augmentin": {
        "brand": "Augmentin 625 Duo",
        "generic": "Amoxicillin & Potassium Clavulanate Tablets IP",
        "strength": "500 mg + 125 mg",
        "company": "GlaxoSmithKline (GSK)",
        "badge": "SCHEDULE H1 PRESCRIPTION DRUG",
        "primary_color": "#D32F2F",     # GSK Red
        "secondary_color": "#1976D2",   # Clinical Blue
        "form": "tablet",
        "pill_color": "#FAFAFA",
        "score_line": True,
        "emboss": "625",
        "pack_style": "alu_strip"
    },
    "dolo": {
        "brand": "Dolo 650",
        "generic": "Paracetamol Tablets IP",
        "strength": "650 mg",
        "company": "Micro Labs Limited",
        "badge": "FAST FEVER & PAIN RELIEF",
        "primary_color": "#005696",     # Micro Labs Blue
        "secondary_color": "#F39C12",   # Yellow/Orange
        "form": "tablet",
        "pill_color": "#FFFFFF",
        "score_line": True,
        "emboss": "DOLO 650",
        "pack_style": "blister"
    },
    "asthalin": {
        "brand": "Asthalin Inhaler",
        "generic": "Salbutamol Inhalation Aerosol IP",
        "strength": "100 mcg / actuation",
        "company": "Cipla Ltd",
        "badge": "SCHEDULE H PRESCRIPTION DRUG",
        "primary_color": "#007791",     # Cipla Teal/Cyan
        "secondary_color": "#003B46",
        "form": "inhaler",
        "pill_color": "#00A8B5",
        "score_line": False,
        "emboss": "200 DOSES",
        "pack_style": "aerosol"
    },
    "benadryl": {
        "brand": "Benadryl Cough Syrup",
        "generic": "Diphenhydramine HCl, Ammonium Cl & Sod. Citrate",
        "strength": "100 ml Oral Solution",
        "company": "Johnson & Johnson Ltd",
        "badge": "DOCTOR TRUSTED COUGH RELIEF",
        "primary_color": "#C0392B",     # Benadryl Red
        "secondary_color": "#78281F",
        "form": "syrup",
        "pill_color": "#8E1600",
        "score_line": False,
        "emboss": "100 ml",
        "pack_style": "bottle"
    },
    "glycomet": {
        "brand": "Glycomet-GP 1",
        "generic": "Metformin HCl (SR) & Glimepiride Tablets IP",
        "strength": "500 mg / 1 mg",
        "company": "USV Private Ltd",
        "badge": "SCHEDULE H PRESCRIPTION DRUG",
        "primary_color": "#16A085",     # USV Green
        "secondary_color": "#2C3E50",
        "form": "tablet",
        "pill_color": "#FDFEFE",
        "score_line": True,
        "emboss": "GP 1",
        "pack_style": "alu_strip"
    },
    "pan40": {
        "brand": "Pan 40",
        "generic": "Pantoprazole Gastro-resistant Tablets IP",
        "strength": "40 mg",
        "company": "Alkem Laboratories Ltd",
        "badge": "SCHEDULE H PRESCRIPTION DRUG",
        "primary_color": "#E67E22",     # Alkem Orange
        "secondary_color": "#2E4053",
        "form": "tablet",
        "pill_color": "#FAD7A0",        # Enteric yellow/apricot
        "score_line": False,
        "emboss": "PAN 40",
        "pack_style": "alu_strip"
    },
    "atorva": {
        "brand": "Atorva 20",
        "generic": "Atorvastatin Tablets IP",
        "strength": "20 mg",
        "company": "Zydus Cadila",
        "badge": "SCHEDULE H PRESCRIPTION DRUG",
        "primary_color": "#2980B9",     # Zydus Blue
        "secondary_color": "#1A5276",
        "form": "tablet",
        "pill_color": "#FFFFFF",
        "score_line": True,
        "emboss": "AT 20",
        "pack_style": "alu_strip"
    },
    "becosules": {
        "brand": "Becosules Z",
        "generic": "B-Complex Forte with Vitamin C & Zinc",
        "strength": "20 Capsules Strip",
        "company": "Pfizer Limited",
        "badge": "DAILY NUTRITIONAL VITALITY",
        "primary_color": "#922B21",     # Maroon
        "secondary_color": "#B7950B",   # Gold
        "form": "capsule",
        "pill_color": "#922B21",
        "cap_color": "#196F3D",
        "score_line": False,
        "emboss": "BECO-Z",
        "pack_style": "blister"
    },
    "volini": {
        "brand": "Volini Pain Relief Gel",
        "generic": "Diclofenac Diethylamine Gel with Linseed Oil & Menthol",
        "strength": "50 g Net Wt",
        "company": "Sun Pharma Industries Ltd",
        "badge": "RAPID PAIN RECOVERY FORMULA",
        "primary_color": "#D35400",     # Volini Bright Orange
        "secondary_color": "#2C3E50",
        "form": "cream",
        "pill_color": "#ECF0F1",
        "score_line": False,
        "emboss": "VOLINI",
        "pack_style": "tube"
    },
    "ciplox": {
        "brand": "Ciplox Eye/Ear Drops",
        "generic": "Ciprofloxacin Ophthalmic Solution IP",
        "strength": "0.3% w/v - 10 ml",
        "company": "Cipla Ltd",
        "badge": "STERILE OPHTHALMIC / OTIC",
        "primary_color": "#27AE60",     # Cipla Green
        "secondary_color": "#145A32",
        "form": "drops",
        "pill_color": "#E8F8F5",
        "score_line": False,
        "emboss": "10 ml",
        "pack_style": "dropper"
    },
    "allegra": {
        "brand": "Allegra 120 mg",
        "generic": "Fexofenadine HCl Tablets IP",
        "strength": "120 mg",
        "company": "Sanofi India Ltd",
        "badge": "SCHEDULE H PRESCRIPTION DRUG",
        "primary_color": "#6C3483",     # Sanofi Purple
        "secondary_color": "#4A235A",
        "form": "tablet",
        "pill_color": "#F5EEF8",
        "score_line": False,
        "emboss": "012",
        "pack_style": "blister"
    },
    "shelcal": {
        "brand": "Shelcal 500",
        "generic": "Calcium & Vitamin D3 Tablets IP",
        "strength": "500 mg + 250 IU",
        "company": "Torrent Pharmaceuticals Ltd",
        "badge": "BONES & JOINT STRENGTH",
        "primary_color": "#1E8449",     # Torrent Green
        "secondary_color": "#114B27",
        "form": "tablet",
        "pill_color": "#FFFFFF",
        "score_line": True,
        "emboss": "SHELCAL",
        "pack_style": "blister"
    }
}

def generate_svg_main(key, info):
    # Professional product card image
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 320" width="100%" height="100%">
  <defs>
    <linearGradient id="bgGrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#F8FAFC" />
      <stop offset="100%" stop-color="#EDF2F7" />
    </linearGradient>
    <linearGradient id="primaryGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{info['primary_color']}" />
      <stop offset="100%" stop-color="{info['secondary_color']}" />
    </linearGradient>
    <filter id="cardShadow" x="-10%" y="-10%" width="120%" height="130%">
      <feDropShadow dx="0" dy="8" stdDeviation="12" flood-color="#0F172A" flood-opacity="0.12" />
    </filter>
    <filter id="pillGlow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000000" flood-opacity="0.15" />
    </filter>
  </defs>

  <!-- Clean Studio Background -->
  <rect width="400" height="320" rx="16" fill="url(#bgGrad)" />
  <circle cx="200" cy="150" r="110" fill="#FFFFFF" opacity="0.6" />

  <!-- Pharmacy Cross Watermark subtle -->
  <path d="M 190 40 h 20 v 30 h 30 v 20 h -30 v 30 h -20 v -30 h -30 v -20 h 30 Z" fill="{info['primary_color']}" opacity="0.04" />

  <!-- Outer Carton / Main Presentation Box -->
  <g filter="url(#cardShadow)">
    <!-- Box Front Surface -->
    <rect x="70" y="55" width="260" height="190" rx="10" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1.5" />
    <!-- Header Color Accent Band -->
    <rect x="70" y="55" width="260" height="42" rx="10" fill="url(#primaryGrad)" />
    <rect x="70" y="87" width="260" height="10" fill="url(#primaryGrad)" />
    
    <!-- Rx / OTC Tag -->
    <rect x="85" y="65" width="34" height="22" rx="4" fill="#FFFFFF" />
    <text x="102" y="81" font-family="Arial, sans-serif" font-weight="900" font-size="13" fill="{info['primary_color']}" text-anchor="middle">Rx</text>
    
    <!-- Brand Label -->
    <text x="130" y="82" font-family="'Segoe UI', Roboto, sans-serif" font-weight="800" font-size="16" fill="#FFFFFF">{info['brand']}</text>
    
    <!-- Generic Scientific Formulation -->
    <text x="85" y="122" font-family="'Segoe UI', Roboto, sans-serif" font-weight="600" font-size="11" fill="#475569">{info['generic'][:42]}</text>
    <text x="85" y="137" font-family="'Segoe UI', Roboto, sans-serif" font-weight="600" font-size="11" fill="#64748B">{info['generic'][42:80]}</text>
    
    <!-- Strength & Form Badges -->
    <rect x="85" y="152" width="110" height="22" rx="6" fill="#F1F5F9" />
    <text x="140" y="167" font-family="Arial, sans-serif" font-weight="700" font-size="11" fill="#1E293B" text-anchor="middle">{info['strength']}</text>
    
    <rect x="202" y="152" width="70" height="22" rx="6" fill="#EFF6FF" stroke="#BFDBFE" stroke-width="0.8" />
    <text x="237" y="167" font-family="Arial, sans-serif" font-weight="700" font-size="10" fill="#1D4ED8" text-anchor="middle">{info['form'].upper()}</text>

    <!-- Manufacturer Seal -->
    <line x1="85" y1="192" x2="315" y2="192" stroke="#F1F5F9" stroke-width="1.5" />
    <circle cx="97" cy="214" r="10" fill="{info['primary_color']}" opacity="0.12" />
    <text x="97" y="218" font-family="Arial, sans-serif" font-weight="900" font-size="10" fill="{info['primary_color']}" text-anchor="middle">✓</text>
    <text x="115" y="214" font-family="'Segoe UI', Roboto, sans-serif" font-weight="700" font-size="11" fill="#0F172A">{info['company']}</text>
    <text x="115" y="226" font-family="'Segoe UI', Roboto, sans-serif" font-weight="500" font-size="9" fill="#94A3B8">Authentic Verified Quality</text>
  </g>

  <!-- Foreground Dosage Graphic Representation -->
  <g filter="url(#pillGlow)">
    {"<!-- 3D Tablet Presentation -->" if info['form'] == 'tablet' else ""}
    {f'''
    <!-- Tablet Rendering -->
    <ellipse cx="285" cy="205" rx="36" ry="18" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="1.5" />
    <ellipse cx="285" cy="203" rx="34" ry="16" fill="{info['pill_color']}" />
    {"<line x1='270' y1='203' x2='300' y2='203' stroke='#94A3B8' stroke-width='1.5' />" if info['score_line'] else ""}
    <text x="285" y="200" font-family="Arial, sans-serif" font-weight="800" font-size="7" fill="#64748B" text-anchor="middle">{info['emboss']}</text>
    ''' if info['form'] == 'tablet' else ""}

    {f'''
    <!-- Capsule Rendering -->
    <rect x="255" y="194" width="60" height="24" rx="12" fill="{info['cap_color'] if 'cap_color' in info else '#E2E8F0'}" stroke="#94A3B8" stroke-width="1" />
    <rect x="285" y="194" width="30" height="24" rx="12" fill="{info['primary_color']}" />
    <line x1="285" y1="194" x2="285" y2="218" stroke="#FFFFFF" stroke-width="1.2" opacity="0.7" />
    ''' if info['form'] == 'capsule' else ""}

    {f'''
    <!-- Syrup Bottle Representation -->
    <rect x="260" y="180" width="44" height="60" rx="6" fill="#78350F" opacity="0.9" />
    <rect x="272" y="172" width="20" height="10" rx="2" fill="#E2E8F0" />
    <rect x="264" y="195" width="36" height="28" fill="#FFFFFF" rx="2" />
    <text x="282" y="212" font-family="Arial, sans-serif" font-weight="800" font-size="7" fill="#B91C1C" text-anchor="middle">100ml</text>
    ''' if info['form'] == 'syrup' else ""}

    {f'''
    <!-- Inhaler Representation -->
    <path d="M 270 170 h 24 v 40 h 20 v 22 h -44 Z" rx="4" fill="#0284C7" stroke="#0369A1" stroke-width="1" />
    <rect x="272" y="162" width="20" height="10" rx="3" fill="#E2E8F0" />
    <circle cx="282" cy="195" r="4" fill="#FFFFFF" opacity="0.8" />
    ''' if info['form'] == 'inhaler' else ""}

    {f'''
    <!-- Cream Tube Representation -->
    <polygon points="255,225 265,185 305,185 315,225" fill="#EA580C" />
    <rect x="275" y="225" width="20" height="10" rx="2" fill="#FFFFFF" stroke="#CBD5E1" />
    <text x="285" y="205" font-family="Arial, sans-serif" font-weight="800" font-size="7" fill="#FFFFFF" text-anchor="middle">50g</text>
    ''' if info['form'] == 'cream' else ""}

    {f'''
    <!-- Dropper Bottle Representation -->
    <rect x="268" y="185" width="34" height="48" rx="6" fill="#F8FAFC" stroke="#64748B" stroke-width="1" />
    <path d="M 278 185 L 285 168 L 292 185 Z" fill="#0EA5E9" />
    <rect x="272" y="198" width="26" height="22" fill="#10B981" rx="2" />
    <text x="285" y="212" font-family="Arial, sans-serif" font-weight="800" font-size="7" fill="#FFFFFF" text-anchor="middle">10ml</text>
    ''' if info['form'] == 'drops' else ""}
  </g>

  <!-- Bottom Quality Ribbon -->
  <rect x="0" y="306" width="400" height="14" fill="{info['primary_color']}" />
</svg>"""

def generate_svg_pack(key, info):
    # Packaging view / Blister pack or outer carton
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 320" width="100%" height="100%">
  <defs>
    <linearGradient id="packGrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#FFFFFF" />
      <stop offset="100%" stop-color="#E2E8F0" />
    </linearGradient>
    <filter id="shadow">
      <feDropShadow dx="0" dy="6" stdDeviation="10" flood-color="#000000" flood-opacity="0.15" />
    </filter>
  </defs>
  <rect width="400" height="320" rx="16" fill="#F8FAFC" />
  
  <!-- Packaging Carton / Blister Tray -->
  <g filter="url(#shadow)">
    <rect x="50" y="40" width="300" height="240" rx="12" fill="url(#packGrad)" stroke="#CBD5E1" stroke-width="1.5" />
    
    <!-- Security Tamper Evident Hologram Seal -->
    <rect x="280" y="55" width="50" height="30" rx="4" fill="url(#packGrad)" stroke="#38BDF8" stroke-width="1" />
    <text x="305" y="73" font-family="Arial, sans-serif" font-size="8" font-weight="900" fill="#0284C7" text-anchor="middle">GENUINE</text>
    <text x="305" y="81" font-family="Arial, sans-serif" font-size="6" fill="#64748B" text-anchor="middle">SEALED</text>

    <!-- Header bar -->
    <rect x="50" y="40" width="300" height="38" rx="12" fill="{info['primary_color']}" />
    <rect x="50" y="66" width="300" height="12" fill="{info['primary_color']}" />
    <text x="75" y="65" font-family="'Segoe UI', Roboto, sans-serif" font-size="16" font-weight="800" fill="#FFFFFF">{info['brand']}</text>
    <text x="75" y="75" font-family="'Segoe UI', Roboto, sans-serif" font-size="9" font-weight="600" fill="#F8FAFC">{info['company']}</text>

    <!-- Packaging Information Specs -->
    <text x="75" y="115" font-family="'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#1E293B">Packaging &amp; Presentation Specification</text>
    <text x="75" y="135" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" fill="#475569">Formula: {info['generic']}</text>
    <text x="75" y="152" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" fill="#475569">Dosage Form: {info['form'].capitalize()}</text>
    <text x="75" y="169" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" fill="#475569">Strength: {info['strength']}</text>
    <text x="75" y="186" font-family="'Segoe UI', Roboto, sans-serif" font-size="10" fill="#475569">Pack Spec: Sealed Pharmaceutical Grade Aluminum/PVC Packaging</text>

    <!-- Barcode & Batch Details -->
    <rect x="75" y="210" width="130" height="45" fill="#FFFFFF" stroke="#E2E8F0" rx="4" />
    <!-- Barcode lines -->
    <path d="M 85 218 v 24 M 90 218 v 24 M 94 218 v 24 M 100 218 v 24 M 104 218 v 24 M 110 218 v 24 M 116 218 v 24 M 120 218 v 24 M 126 218 v 24 M 132 218 v 24 M 138 218 v 24 M 145 218 v 24 M 152 218 v 24 M 160 218 v 24 M 168 218 v 24 M 174 218 v 24 M 182 218 v 24 M 190 218 v 24" stroke="#0F172A" stroke-width="2" />
    <text x="140" y="250" font-family="monospace" font-size="7" fill="#64748B" text-anchor="middle">8901234 567890</text>

    <!-- Batch details -->
    <text x="225" y="222" font-family="monospace" font-size="9" fill="#1E293B">B.No: HG-26A09</text>
    <text x="225" y="236" font-family="monospace" font-size="9" fill="#1E293B">MFG: 08/2026</text>
    <text x="225" y="250" font-family="monospace" font-size="9" fill="#B91C1C">EXP: 07/2028</text>
  </g>
</svg>"""

def generate_svg_dosage(key, info):
    # Macro dosage view (Tablet/Capsule/Syrup/Inhaler closeup)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 320" width="100%" height="100%">
  <defs>
    <radialGradient id="pillShine" cx="35%" cy="35%" r="65%">
      <stop offset="0%" stop-color="#FFFFFF" />
      <stop offset="40%" stop-color="{info['pill_color']}" />
      <stop offset="100%" stop-color="#CBD5E1" />
    </radialGradient>
    <filter id="macroShadow">
      <feDropShadow dx="0" dy="12" stdDeviation="16" flood-color="#0F172A" flood-opacity="0.2" />
    </filter>
  </defs>
  <rect width="400" height="320" rx="16" fill="#F1F5F9" />
  
  <!-- Dosage Measurement Grid in background -->
  <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
    <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#E2E8F0" stroke-width="0.8" />
  </pattern>
  <rect width="400" height="320" fill="url(#grid)" />

  <text x="200" y="45" font-family="'Segoe UI', Roboto, sans-serif" font-weight="700" font-size="14" fill="#334155" text-anchor="middle">MACRO PHARMACEUTICAL DOSAGE VIEW</text>
  <text x="200" y="65" font-family="'Segoe UI', Roboto, sans-serif" font-weight="500" font-size="11" fill="#64748B" text-anchor="middle">{info['brand']} — {info['strength']}</text>

  <!-- Macro Central Dose Graphic -->
  <g filter="url(#macroShadow)">
    {f'''
    <!-- Macro Tablet -->
    <g transform="translate(200, 170)">
      <ellipse cx="0" cy="15" rx="100" ry="50" fill="#94A3B8" opacity="0.4" />
      <ellipse cx="0" cy="5" rx="95" ry="46" fill="#CBD5E1" />
      <ellipse cx="0" cy="0" rx="90" ry="44" fill="url(#pillShine)" stroke="#94A3B8" stroke-width="1.5" />
      {"<line x1='-70' y1='0' x2='70' y2='0' stroke='#94A3B8' stroke-width='3' stroke-linecap='round' />" if info['score_line'] else ""}
      <text x="0" y="-12" font-family="Arial, sans-serif" font-weight="900" font-size="16" fill="#64748B" text-anchor="middle" letter-spacing="2">{info['emboss']}</text>
    </g>
    ''' if info['form'] == 'tablet' else ""}

    {f'''
    <!-- Macro Capsule -->
    <g transform="translate(130, 140) rotate(-15)">
      <!-- Left Body -->
      <rect x="0" y="0" width="85" height="55" rx="27.5" fill="{info['cap_color'] if 'cap_color' in info else '#E2E8F0'}" stroke="#94A3B8" stroke-width="1.5" />
      <!-- Right Cap -->
      <rect x="70" y="0" width="85" height="55" rx="27.5" fill="{info['primary_color']}" stroke="{info['secondary_color']}" stroke-width="1.5" />
      <line x1="70" y1="0" x2="70" y2="55" stroke="#FFFFFF" stroke-width="2.5" />
      <!-- Specular Highlight -->
      <rect x="25" y="8" width="105" height="6" rx="3" fill="#FFFFFF" opacity="0.6" />
    </g>
    ''' if info['form'] == 'capsule' else ""}

    {f'''
    <!-- Macro Syrup Cup & Bottle -->
    <g transform="translate(160, 110)">
      <!-- Measuring cup -->
      <polygon points="120,40 145,110 85,110 110,40" fill="#E0F2FE" opacity="0.8" stroke="#0284C7" stroke-width="1.5" />
      <!-- Liquid level -->
      <polygon points="115,65 140,105 90,105 112,65" fill="{info['primary_color']}" opacity="0.85" />
      <!-- Markings -->
      <line x1="98" y1="65" x2="115" y2="65" stroke="#0369A1" stroke-width="1" />
      <text x="94" y="68" font-family="Arial" font-size="8" font-weight="700" fill="#0369A1" text-anchor="end">10 ml</text>
      <line x1="93" y1="85" x2="110" y2="85" stroke="#0369A1" stroke-width="1" />
      <text x="89" y="88" font-family="Arial" font-size="8" font-weight="700" fill="#0369A1" text-anchor="end">5 ml</text>
      <!-- Bottle neck -->
      <rect x="-20" y="10" width="70" height="110" rx="8" fill="#78350F" opacity="0.9" />
      <rect x="0" y="-8" width="30" height="18" rx="4" fill="#F8FAFC" stroke="#CBD5E1" />
    </g>
    ''' if info['form'] == 'syrup' else ""}

    {f'''
    <!-- Macro Inhaler -->
    <g transform="translate(160, 100)">
      <path d="M 0 0 h 50 v 90 h 45 v 45 h -95 Z" fill="#0284C7" stroke="#0369A1" stroke-width="2" />
      <rect x="5" y="-18" width="40" height="20" rx="4" fill="#CBD5E1" stroke="#94A3B8" />
      <circle cx="25" cy="40" r="15" fill="#FFFFFF" opacity="0.2" />
      <!-- Mouthpiece cap -->
      <rect x="80" y="90" width="20" height="45" rx="4" fill="#0369A1" />
      <!-- Aerosol Mist puff -->
      <circle cx="115" cy="112" r="8" fill="#BAE6FD" opacity="0.6" />
      <circle cx="130" cy="108" r="14" fill="#BAE6FD" opacity="0.4" />
      <circle cx="150" cy="115" r="20" fill="#E0F2FE" opacity="0.3" />
    </g>
    ''' if info['form'] == 'inhaler' else ""}

    {f'''
    <!-- Macro Gel / Drops fallback -->
    <g transform="translate(150, 120)">
      <path d="M 20 60 Q 50 -10 80 60 Q 50 90 20 60 Z" fill="{info['primary_color']}" opacity="0.85" stroke="#FFFFFF" stroke-width="2" />
      <circle cx="45" cy="35" r="8" fill="#FFFFFF" opacity="0.7" />
    </g>
    ''' if info['form'] in ('cream', 'drops') else ""}
  </g>

  <!-- Spec details -->
  <rect x="80" y="270" width="240" height="28" rx="6" fill="#FFFFFF" stroke="#CBD5E1" />
  <text x="200" y="288" font-family="'Segoe UI', Roboto, sans-serif" font-weight="600" font-size="11" fill="#1E293B" text-anchor="middle">Form: {info['form'].upper()} | Visual Quality Verified</text>
</svg>"""

def generate_svg_back(key, info):
    # Back view / Composition & legal information
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 320" width="100%" height="100%">
  <rect width="400" height="320" rx="16" fill="#F8FAFC" />
  <rect x="40" y="30" width="320" height="260" rx="8" fill="#FFFFFF" stroke="#CBD5E1" stroke-width="1.5" />
  
  <!-- Red Warning Box for Rx if applicable -->
  <rect x="55" y="45" width="290" height="36" fill="{"#FEF2F2" if "SCHEDULE" in info["badge"] else "#EFF6FF"}" stroke="{"#EF4444" if "SCHEDULE" in info["badge"] else "#3B82F6"}" stroke-width="1" rx="4" />
  <text x="200" y="62" font-family="Arial, sans-serif" font-weight="800" font-size="10" fill="{"#B91C1C" if "SCHEDULE" in info["badge"] else "#1D4ED8"}" text-anchor="middle">{info['badge']}</text>
  <text x="200" y="74" font-family="Arial, sans-serif" font-size="8" fill="#475569" text-anchor="middle">To be sold by retail on the prescription of a Registered Medical Practitioner only.</text>

  <!-- Chemical Formulation Details -->
  <text x="60" y="105" font-family="'Segoe UI', Roboto, sans-serif" font-weight="800" font-size="11" fill="#0F172A">COMPOSITION:</text>
  <text x="60" y="122" font-family="'Segoe UI', Roboto, sans-serif" font-weight="600" font-size="10" fill="#334155">{info['brand']}</text>
  <text x="60" y="137" font-family="'Segoe UI', Roboto, sans-serif" font-size="9" fill="#475569">Each unit contains: {info['generic']}</text>
  <text x="60" y="152" font-family="'Segoe UI', Roboto, sans-serif" font-size="9" fill="#475569">Excipients: q.s. Colours: Approved Pharmacopoeia Colours added.</text>

  <!-- Storage and Dosage -->
  <text x="60" y="176" font-family="'Segoe UI', Roboto, sans-serif" font-weight="800" font-size="11" fill="#0F172A">DOSAGE &amp; STORAGE:</text>
  <text x="60" y="193" font-family="'Segoe UI', Roboto, sans-serif" font-size="9" fill="#475569">Dosage: As directed by the Physician.</text>
  <text x="60" y="208" font-family="'Segoe UI', Roboto, sans-serif" font-size="9" fill="#475569">Storage: Store below 25°C in a dry, dark place. Keep out of reach of children.</text>

  <!-- Manufacturer Credentials -->
  <line x1="55" y1="225" x2="345" y2="225" stroke="#E2E8F0" stroke-width="1" />
  <text x="60" y="244" font-family="'Segoe UI', Roboto, sans-serif" font-weight="700" font-size="10" fill="#1E293B">Manufactured in India by:</text>
  <text x="60" y="258" font-family="'Segoe UI', Roboto, sans-serif" font-weight="600" font-size="10" fill="{info['primary_color']}">{info['company']}</text>
  <text x="60" y="272" font-family="'Segoe UI', Roboto, sans-serif" font-size="8" fill="#64748B">Mfg. Lic. No.: G/25/1842 | GMP &amp; ISO 9001:2015 Certified Facility</text>
</svg>"""

def main():
    print("Generating authentic pharmaceutical SVG images...")
    count = 0
    for key, info in MEDICINE_VISUALS.items():
        # 1. Main image
        main_svg = generate_svg_main(key, info)
        with open(os.path.join(IMAGE_DIR, f"{key}_main.svg"), "w", encoding="utf-8") as f:
            f.write(main_svg)
        count += 1

        # 2. Packaging image
        pack_svg = generate_svg_pack(key, info)
        with open(os.path.join(IMAGE_DIR, f"{key}_pack.svg"), "w", encoding="utf-8") as f:
            f.write(pack_svg)
        count += 1

        # 3. Dosage closeup image
        dosage_svg = generate_svg_dosage(key, info)
        form_name = info['form'] if info['form'] in ('tablet', 'capsule', 'syrup', 'inhaler') else ('gel' if info['form'] == 'cream' else 'drops')
        with open(os.path.join(IMAGE_DIR, f"{key}_{form_name}.svg"), "w", encoding="utf-8") as f:
            f.write(dosage_svg)
        count += 1

        # 4. Back view image
        back_svg = generate_svg_back(key, info)
        with open(os.path.join(IMAGE_DIR, f"{key}_back.svg"), "w", encoding="utf-8") as f:
            f.write(back_svg)
        count += 1

    print(f"Generated {count} crisp pharmaceutical SVG assets in {IMAGE_DIR}")

if __name__ == "__main__":
    main()
