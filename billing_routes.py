from flask import Blueprint, request, jsonify
import stripe
import os
import logging

billing_routes = Blueprint("billing_routes", __name__)
logger = logging.getLogger(__name__)

# ✅ Load Stripe API Key Securely from Environment
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# ✅ Function to Charge Users via Stripe
def charge_user(user_id, overage_units):
    """Charges users for exceeding API usage limits."""
    customer_id = get_customer_id(user_id)
    if not customer_id:
        return {"error": "Stripe customer ID not found"}

    charge_amount = int(overage_units * 0.06 * 100)  # Assuming $0.06 per overage unit

    invoice_item = stripe.InvoiceItem.create(
        customer=customer_id,
        amount=charge_amount,
        currency="usd",
        description=f"Overage charge for {overage_units} additional API lookups"
    )

    invoice = stripe.Invoice.create(customer=customer_id)
    stripe.Invoice.finalize_invoice(invoice.id)

    return {"status": "success", "invoice_id": invoice.id}

# ✅ Get Stripe Customer ID
def get_customer_id(user_id):
    try:
        customers = stripe.Customer.list(email=f"{user_id}@example.com").data
        if customers:
            return customers[0].id
        return None
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        return None

# ✅ API Endpoint: Charge Overages
@billing_routes.route("/charge", methods=["POST"])
def charge():
    data = request.json
    user_id = data.get("user_id")
    overage_units = data.get("overage_units")

    if not user_id or not overage_units:
        return jsonify({"error": "Missing parameters"}), 400

    return jsonify(charge_user(user_id, overage_units))
