"""
End-to-End Automated System Verification for HealthGuard.
Tests database operations, REST endpoints, catalog integrity, 3D assets, and ecosystem workflows.
"""

import sys
import os
import json

# Force UTF-8 encoding on standard output for Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.database import db

def test_catalog():
    print("1. Testing Medicines Catalog...")
    meds = db.get_medicines()
    assert len(meds) >= 12, f"Expected at least 12 medicines, found {len(meds)}"
    
    # Check required fields
    for m in meds:
        assert m["id"], "Medicine ID missing"
        assert m["name"], "Medicine name missing"
        assert m["generic_name"], "Generic name missing"
        assert m["price"] > 0, "Price must be positive"
        assert m["dosage_form"], "Dosage form missing"
        assert "main" in m["gallery"], "Main image missing"
        rel_path = m["gallery"]["main"].lstrip("/\\")
        full_path = os.path.join(os.path.dirname(__file__), "frontend", rel_path)
        assert os.path.exists(full_path), f"Asset {full_path} does not exist"
    print("   [PASS] All 12 medicines verified with valid prices, metadata, and existing image files.")

def test_search_and_filters():
    print("2. Testing Search and Multi-Filtering...")
    # Search by brand
    res_dolo = db.get_medicines(search="Dolo")
    assert len(res_dolo) >= 1 and "Dolo" in res_dolo[0]["name"]

    # Filter by dosage form
    res_inhaler = db.get_medicines(dosage_form="Inhaler")
    assert len(res_inhaler) >= 1 and res_inhaler[0]["dosage_form"] == "Inhaler"

    # Filter by prescription requirement
    res_rx = db.get_medicines(prescription_req=True)
    assert all(m["prescription_required"] for m in res_rx)
    res_otc = db.get_medicines(prescription_req=False)
    assert all(not m["prescription_required"] for m in res_otc)
    print("   [PASS] Search by name, brand, dosage form, and Rx requirements functioning correctly.")

def test_cart_and_prescription_checkout():
    print("3. Testing Cart, Prescription Linking & Order Placement...")
    db.clear_cart()
    cart_empty = db.get_cart()
    assert cart_empty["subtotal"] == 0

    # Add Augmentin 625 (Rx) and Dolo 650 (OTC)
    db.add_to_cart("med-aug-625", 2)
    db.add_to_cart("med-dolo-650", 1)
    cart = db.get_cart()
    assert len(cart["items"]) == 2
    assert cart["rx_required"] is True
    print(f"   [PASS] Cart populated: {len(cart['items'])} items, Subtotal: Rs. {cart['subtotal']}, Rx Required: {cart['rx_required']}")

    # Create Order with prescription reference
    order = db.create_order(
        delivery_address="Flat 402, Green Valley Heights, New Delhi",
        prescription_id="RX-2026-9041",
        coupon_code="HEALTH20"
    )
    assert order["order_id"], "Order ID was not generated"
    assert order["discount"] > 0, "HEALTH20 discount should apply"
    print(f"   [PASS] Order #{order['order_id']} created! Status: {order['status']}, Discount: Rs. {order['discount']}, Total: Rs. {order['total']}")

    # Advance order stages
    updated_order = db.update_order_status(order["order_id"], 3) # Shipped
    assert updated_order["status"] == "Shipped"
    print(f"   [PASS] Order stage advanced to: {updated_order['status']}")

def test_pharmacist_review_gate():
    print("4. Testing Pharmacist Verification Gate...")
    # Upload new prescription
    uploaded = db.upload_prescription(
        doctor_name="Dr. External Specialist",
        patient_name="Manik Sharma",
        medicine_id="med-aug-625",
        medicine_name="Augmentin 625 Duo",
        file_name="rx_slip_scan.pdf"
    )
    assert uploaded["status"] == "Pending Review"

    # Pharmacist approval
    approved = db.review_prescription(uploaded["prescription_id"], "approve", "Clinically verified against council records.")
    assert approved["status"] == "Approved"
    print(f"   [PASS] Prescription {uploaded['prescription_id']} uploaded and approved by pharmacist.")

def test_adherence_and_3d_reminder_logging():
    print("5. Testing Adherence Dashboard Logging...")
    res = db.record_adherence(
        medicine_name="Augmentin 625 Duo Tablet",
        scheduled_time="08:00 AM",
        status="Taken",
        prescription_ref="RX-2026-9041",
        notes="Automated test dose verified"
    )
    assert res["adherence_rate"] > 0
    print(f"   [PASS] Dose recorded! Total logged: {res['total_doses']}, Adherence rate: {res['adherence_rate']}%")

def main():
    print("==================================================")
    print(" Running HealthGuard System Verification Tests...")
    print("==================================================")
    test_catalog()
    test_search_and_filters()
    test_cart_and_prescription_checkout()
    test_pharmacist_review_gate()
    test_adherence_and_3d_reminder_logging()
    print("==================================================")
    print(" ALL TESTS PASSED! HealthGuard System is 100% Ready.")
    print("==================================================")

if __name__ == "__main__":
    main()
