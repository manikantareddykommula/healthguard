"""
HealthGuard HTTP Server & Comprehensive REST API.
Serves static frontend assets and provides robust REST endpoints for:
- Authentication & RBAC (Patient, Doctor, Administrator)
- Medicines Catalog, Multi-filters, Sorting, Details & Comparison
- Cart, Prescription Verification Gate, Checkout & Orders Lifecycle
- Doctor Appointments & Digital Prescription Issuance
- Medical Reports Vault (secure upload, view, delete)
- AI Report Assistant (educational terminology & lab ranges with strict disclaimers)
- Health Monitoring Vitals, Threshold Alerts & History
- Preventive Care & Automated Annual Checkup Tracking
- 3D Medicine Reminders & Medication Adherence Dashboard
- System Analytics & Administrative Audits
"""

import base64
import http.server
import json
import os
import socketserver
import urllib.parse
from datetime import datetime
from backend.database import db

PORT = 8080
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
UPLOADS_DIR = os.path.join(FRONTEND_DIR, "uploads", "reports")
os.makedirs(UPLOADS_DIR, exist_ok=True)

class HealthGuardHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FRONTEND_DIR, **kwargs)

    def _send_json(self, data, status_code=200):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
        self.wfile.write(body)

    def _parse_json_body(self):
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > 0:
            raw_body = self.rfile.read(content_length).decode("utf-8")
            try:
                return json.loads(raw_body)
            except Exception:
                return {}
        return {}

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # -----------------------------
        # AUTHENTICATION ENDPOINTS
        # -----------------------------
        if path == "/api/auth/me":
            user_id = query.get("user_id", ["usr-patient-1"])[0]
            user = db.get_user_by_id(user_id)
            if user:
                return self._send_json({"user": user})
            return self._send_json({"error": "User not found"}, 404)

        # -----------------------------
        # MEDICINES STORE & CATALOG
        # -----------------------------
        elif path == "/api/medicines":
            search = query.get("search", [""])[0]
            category = query.get("category", [""])[0]
            dosage_form = query.get("dosage_form", [""])[0]
            rx_param = query.get("prescription_required", [None])[0]
            sort_by = query.get("sort_by", [None])[0]
            rx_req = None
            if rx_param is not None:
                rx_req = rx_param.lower() in ("true", "1", "yes")

            min_price = float(query["min_price"][0]) if "min_price" in query else None
            max_price = float(query["max_price"][0]) if "max_price" in query else None

            meds = db.get_medicines(
                search=search,
                category=category,
                dosage_form=dosage_form,
                prescription_req=rx_req,
                min_price=min_price,
                max_price=max_price,
                sort_by=sort_by
            )
            return self._send_json({"medicines": meds, "count": len(meds)})

        elif path.startswith("/api/medicines/"):
            med_id = path.replace("/api/medicines/", "").strip()
            med = db.get_medicine_by_id(med_id)
            if med:
                return self._send_json({"medicine": med})
            return self._send_json({"error": "Medicine not found"}, 404)

        elif path == "/api/compare":
            ids_param = query.get("ids", [""])[0]
            if not ids_param:
                return self._send_json({"medicines": []})
            med_ids = [i.strip() for i in ids_param.split(",") if i.strip()]
            meds = [db.get_medicine_by_id(i) for i in med_ids if db.get_medicine_by_id(i)]
            return self._send_json({"medicines": meds})

        # -----------------------------
        # CART & ORDERS
        # -----------------------------
        elif path == "/api/cart":
            return self._send_json(db.get_cart())

        elif path == "/api/orders":
            user_id = query.get("user_id", [None])[0]
            return self._send_json({"orders": db.get_orders(user_id=user_id)})

        # -----------------------------
        # DOCTORS & APPOINTMENTS
        # -----------------------------
        elif path == "/api/doctors":
            spec = query.get("specialization", [None])[0]
            return self._send_json({"doctors": db.get_doctors(specialization=spec)})

        elif path == "/api/appointments":
            user_id = query.get("user_id", [None])[0]
            role = query.get("role", ["patient"])[0]
            return self._send_json({"appointments": db.get_appointments(user_id=user_id, role=role)})

        # -----------------------------
        # PRESCRIPTIONS & CONSULTATIONS
        # -----------------------------
        elif path == "/api/prescriptions":
            return self._send_json({"prescriptions": db.get_prescriptions()})

        elif path == "/api/consultations":
            return self._send_json({"consultations": db.get_consultations()})

        # -----------------------------
        # MEDICAL REPORTS
        # -----------------------------
        elif path == "/api/reports":
            user_id = query.get("user_id", ["usr-patient-1"])[0]
            return self._send_json({"reports": db.get_medical_reports(user_id=user_id)})

        # -----------------------------
        # HEALTH MONITORING & VITALS
        # -----------------------------
        elif path == "/api/vitals":
            user_id = query.get("user_id", ["usr-patient-1"])[0]
            m_type = query.get("type", [None])[0]
            days = int(query.get("days", [30])[0])
            return self._send_json({"vitals": db.get_health_measurements(user_id=user_id, measurement_type=m_type, days_limit=days)})

        elif path == "/api/vitals/summary":
            user_id = query.get("user_id", ["usr-patient-1"])[0]
            return self._send_json({"summary": db.get_latest_vitals_summary(user_id=user_id)})

        # -----------------------------
        # PREVENTIVE CARE / CHECKUPS
        # -----------------------------
        elif path == "/api/checkups":
            user_id = query.get("user_id", ["usr-patient-1"])[0]
            return self._send_json({"checkups": db.get_checkups(user_id=user_id)})

        # -----------------------------
        # HEALTH TIMELINE
        # -----------------------------
        elif path == "/api/timeline":
            user_id = query.get("user_id", ["usr-patient-1"])[0]
            ev_type = query.get("event_type", [None])[0]
            return self._send_json({"timeline": db.get_health_timeline(user_id=user_id, event_type=ev_type)})

        # -----------------------------
        # REMINDERS & ADHERENCE
        # -----------------------------
        elif path == "/api/reminders":
            return self._send_json({"reminders": db.get_reminders()})

        elif path == "/api/adherence":
            return self._send_json(db.get_adherence_logs())

        # -----------------------------
        # NOTIFICATIONS & ADMIN
        # -----------------------------
        elif path == "/api/notifications":
            user_id = query.get("user_id", [None])[0]
            return self._send_json({"notifications": db.get_notifications(user_id=user_id)})

        elif path == "/api/admin/stats":
            return self._send_json({"stats": db.get_system_stats()})

        elif path == "/api/admin/users":
            return self._send_json({"users": db.list_all_users()})

        elif path == "/api/admin/audit-logs":
            return self._send_json({"logs": db.get_audit_logs()})

        # Static files fallback
        super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        body = self._parse_json_body()

        # -----------------------------
        # AUTHENTICATION
        # -----------------------------
        if path == "/api/auth/login":
            email = body.get("email", "")
            password = body.get("password", "")
            res = db.authenticate_user(email, password)
            if "error" in res:
                return self._send_json(res, 401)
            return self._send_json(res)

        elif path == "/api/auth/register":
            email = body.get("email", "")
            password = body.get("password", "")
            role = body.get("role", "patient")
            name = body.get("name", "")
            phone = body.get("phone", "")
            profile_data = body.get("profile_data", {})
            res = db.register_user(email, password, role, name, phone, profile_data)
            if "error" in res:
                return self._send_json(res, 400)
            return self._send_json(res, 201)

        elif path == "/api/patient/profile":
            user_id = body.get("user_id", "usr-patient-1")
            age = int(body.get("age", 28))
            gender = body.get("gender", "Male")
            blood_group = body.get("blood_group", "B+")
            allergies = body.get("allergies", "None")
            emergency_contact = body.get("emergency_contact", "")
            address = body.get("address", "")
            res = db.update_patient_profile(user_id, age, gender, blood_group, allergies, emergency_contact, address)
            return self._send_json({"profile": res})

        # -----------------------------
        # CART & ORDERS
        # -----------------------------
        elif path == "/api/cart/add":
            med_id = body.get("medicine_id")
            qty = int(body.get("quantity", 1))
            if not med_id:
                return self._send_json({"error": "medicine_id required"}, 400)
            cart = db.add_to_cart(med_id, qty)
            return self._send_json(cart)

        elif path == "/api/cart/update":
            med_id = body.get("medicine_id")
            qty = int(body.get("quantity", 1))
            if not med_id:
                return self._send_json({"error": "medicine_id required"}, 400)
            cart = db.update_cart_quantity(med_id, qty)
            return self._send_json(cart)

        elif path == "/api/cart/clear":
            db.clear_cart()
            return self._send_json(db.get_cart())

        elif path == "/api/orders":
            address = body.get("delivery_address", "Flat 402, Green Valley Heights, New Delhi - 110001")
            rx_id = body.get("prescription_id")
            coupon = body.get("coupon_code", "")
            user_id = body.get("user_id", "usr-patient-1")
            res = db.create_order(delivery_address=address, prescription_id=rx_id, coupon_code=coupon, user_id=user_id)
            if "error" in res:
                return self._send_json(res, 400)
            return self._send_json(res, 201)

        elif path.startswith("/api/orders/") and path.endswith("/status"):
            order_id = path.split("/")[3]
            stage_index = int(body.get("stage_index", 0))
            res = db.update_order_status(order_id, stage_index)
            if "error" in res:
                return self._send_json(res, 400)
            return self._send_json(res)

        # -----------------------------
        # APPOINTMENTS
        # -----------------------------
        elif path == "/api/appointments":
            p_id = body.get("patient_id", "usr-patient-1")
            p_name = body.get("patient_name", "Manik Sharma")
            d_id = body.get("doctor_id", "usr-doctor-1")
            d_name = body.get("doctor_name", "Dr. Priya Nair, MD")
            date_str = body.get("appointment_date", datetime.now().strftime("%Y-%m-%d"))
            time_slot = body.get("time_slot", "10:30 AM")
            reason = body.get("reason", "Routine consultation")
            res = db.create_appointment(p_id, p_name, d_id, d_name, date_str, time_slot, reason)
            return self._send_json(res, 201)

        elif path.startswith("/api/appointments/") and path.endswith("/status"):
            apt_id = path.split("/")[3]
            new_status = body.get("status", "Completed")
            notes = body.get("notes", "")
            res = db.update_appointment_status(apt_id, new_status, notes)
            return self._send_json(res)

        # -----------------------------
        # PRESCRIPTIONS
        # -----------------------------
        elif path == "/api/prescriptions/upload":
            doc_name = body.get("doctor_name", "Dr. Priya Nair, MD")
            pat_name = body.get("patient_name", "Manik Sharma")
            med_id = body.get("medicine_id", "med-aug-625")
            med_name = body.get("medicine_name", "Augmentin 625 Duo Tablet")
            file_name = body.get("file_name", "prescription_doc_upload.pdf")
            notes = body.get("notes", "")
            rx = db.upload_prescription(doc_name, pat_name, med_id, med_name, file_name, notes)
            return self._send_json(rx, 201)

        elif path == "/api/prescriptions/create":
            doc_name = body.get("doctor_name", "Dr. Priya Nair, MD")
            doc_reg = body.get("doctor_reg", "MCI-48920")
            pat_name = body.get("patient_name", "Manik Sharma")
            med_name = body.get("medicine_name", "Augmentin 625 Duo Tablet")
            dosage = body.get("dosage", "1 tablet")
            freq = body.get("frequency", "Twice Daily")
            duration = body.get("duration", "5 Days")
            instructions = body.get("instructions", "Take after food with full glass of water.")
            follow_up = body.get("follow_up_date", "")
            tests = body.get("recommended_tests", "")
            notes = body.get("notes", "")
            rx = db.create_doctor_prescription(doc_name, doc_reg, pat_name, med_name, dosage, freq, duration, instructions, follow_up, tests, notes)
            return self._send_json(rx, 201)

        elif path.startswith("/api/prescriptions/") and path.endswith("/review"):
            rx_id = path.split("/")[3]
            action = body.get("action", "approve")
            notes = body.get("notes", "")
            res = db.review_prescription(rx_id, action, notes)
            if "error" in res:
                return self._send_json(res, 400)
            return self._send_json(res)

        # -----------------------------
        # HEALTH MONITORING & VITALS
        # -----------------------------
        elif path == "/api/vitals":
            user_id = body.get("user_id", "usr-patient-1")
            m_type = body.get("measurement_type", "blood_pressure")
            val1 = float(body.get("value_primary", 120))
            val2 = float(body.get("value_secondary", 80)) if body.get("value_secondary") is not None else None
            unit = body.get("unit", "")
            context = body.get("context", "Resting")
            notes = body.get("notes", "")
            res = db.add_health_measurement(user_id, m_type, val1, val2, unit, context, notes)
            return self._send_json(res, 201)

        # -----------------------------
        # MEDICAL REPORTS VAULT & AI EXPLAINER
        # -----------------------------
        elif path == "/api/reports/upload":
            user_id = body.get("user_id", "usr-patient-1")
            title = body.get("title", "Clinical Diagnostic Report")
            report_type = body.get("report_type", "Blood Test")
            file_name = body.get("file_name", "report.pdf")
            doctor_lab = body.get("doctor_lab", "HealthGuard Central PathLab")
            report_date = body.get("report_date", datetime.now().strftime("%Y-%m-%d"))
            notes = body.get("notes", "")
            file_data_b64 = body.get("file_data_base64", "")

            # Security check & file save
            clean_name = os.path.basename(file_name)
            allowed_exts = ('.pdf', '.jpg', '.jpeg', '.png')
            if not any(clean_name.lower().endswith(ext) for ext in allowed_exts):
                clean_name += ".pdf"

            file_path = f"/uploads/reports/{int(datetime.now().timestamp())}_{clean_name}"
            disk_path = os.path.join(FRONTEND_DIR, file_path.lstrip("/\\"))

            file_size_kb = 120.0
            if file_data_b64:
                try:
                    raw_bytes = base64.b64decode(file_data_b64.split(",")[-1])
                    file_size_kb = round(len(raw_bytes) / 1024, 1)
                    with open(disk_path, "wb") as f:
                        f.write(raw_bytes)
                except Exception:
                    pass

            res = db.add_medical_report(user_id, title, report_type, clean_name, file_path, file_size_kb, doctor_lab, report_date, notes)
            return self._send_json(res, 201)

        elif path == "/api/ai/explain":
            query_term = body.get("term", "")
            res = db.explain_medical_term_or_report(query_term)
            return self._send_json(res)

        # -----------------------------
        # PREVENTIVE CARE / CHECKUPS
        # -----------------------------
        elif path == "/api/checkups":
            user_id = body.get("user_id", "usr-patient-1")
            title = body.get("title", "Routine Screening")
            category = body.get("category", "General Checkup")
            last_date = body.get("last_completed_date", None)
            next_date = body.get("next_due_date", None)
            notes = body.get("notes", "")
            res = db.add_or_update_checkup(user_id, title, category, last_date, next_date, notes)
            return self._send_json(res, 201)

        # -----------------------------
        # REMINDERS & ADHERENCE
        # -----------------------------
        elif path == "/api/adherence/record":
            med_name = body.get("medicine_name", "Augmentin 625 Duo")
            time_str = body.get("scheduled_time", "08:00 AM")
            status = body.get("status", "Taken")
            rx_ref = body.get("prescription_ref", "")
            notes = body.get("notes", "")
            logs = db.record_adherence(med_name, time_str, status, rx_ref, notes)
            return self._send_json(logs)

        # -----------------------------
        # NOTIFICATIONS & ADMIN
        # -----------------------------
        elif path.startswith("/api/notifications/") and path.endswith("/read"):
            notif_id = path.split("/")[3]
            res = db.mark_notification_read(notif_id)
            return self._send_json(res)

        elif path == "/api/admin/verify-doctor":
            d_id = body.get("doctor_id")
            st = body.get("status", "Approved")
            res = db.update_doctor_verification(d_id, st)
            return self._send_json(res)

        return self._send_json({"error": "Endpoint not found"}, 404)

    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path.startswith("/api/reports/"):
            report_id = path.replace("/api/reports/", "").strip()
            user_id = query.get("user_id", ["usr-patient-1"])[0]
            res = db.delete_medical_report(report_id, user_id)
            return self._send_json(res)

        return self._send_json({"error": "Endpoint not found"}, 404)

def run_server(port=PORT):
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", port), HealthGuardHandler) as httpd:
        print(f"=====================================================")
        print(f" HealthGuard Healthcare Platform & Digital Ecosystem")
        print(f" URL: http://localhost:{port}")
        print(f" Directory: {FRONTEND_DIR}")
        print(f"=====================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server gracefully...")
            httpd.server_close()

if __name__ == "__main__":
    run_server()
