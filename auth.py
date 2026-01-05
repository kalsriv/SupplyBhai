# # auth.py

# import streamlit as st
# import stripe

# # Initialize Stripe
# stripe.api_key = st.secrets["STRIPE_SECRET_KEY"]

# # -----------------------------
# # 1. Customer helpers
# # -----------------------------
# def get_or_create_customer(email: str):
#     """Return existing Stripe customer or create a new one."""
#     customers = stripe.Customer.list(email=email, limit=1).data
#     if customers:
#         return customers[0]
#     return stripe.Customer.create(email=email)


# def customer_has_active_subscription(customer_id: str) -> bool:
#     """Check if a customer has an active subscription."""
#     subs = stripe.Subscription.list(
#         customer=customer_id,
#         status="active",
#         limit=1,
#     ).data
#     return len(subs) > 0


# # -----------------------------
# # 2. Checkout session
# # -----------------------------
# def create_checkout_session(email: str):
#     """Create a Stripe Checkout session for subscription."""
#     customer = get_or_create_customer(email)

#     session = stripe.checkout.Session.create(
#         customer=customer.id,
#         payment_method_types=["card"],
#         mode="subscription",
#         line_items=[{
#             "price": st.secrets["STRIPE_PRICE_ID"],
#             "quantity": 1,
#         }],
#         success_url=f'{st.secrets["BASE_URL"]}?session_id={{CHECKOUT_SESSION_ID}}',
#         cancel_url=f'{st.secrets["BASE_URL"]}?canceled=true',
#     )
#     return session.url


# # -----------------------------
# # 3. Main paywall function
# # -----------------------------
# def require_subscription():
#     """
#     Main paywall logic.
#     Call this at the top of app.py.
#     Blocks access until user is subscribed.
#     """

#     # Initialize session state
#     if "email" not in st.session_state:
#         st.session_state.email = None
#     if "is_subscribed" not in st.session_state:
#         st.session_state.is_subscribed = False

#     # Handle Stripe redirect success
#     session_id = st.query_params.get("session_id", [None])[0] if hasattr(st, "query_params") else None
#     if session_id and st.session_state.email:
#         try:
#             checkout_session = stripe.checkout.Session.retrieve(session_id)
#             customer_id = checkout_session.customer
#             if customer_has_active_subscription(customer_id):
#                 st.session_state.is_subscribed = True
#         except Exception:
#             pass

#     # If subscribed → allow access
#     if st.session_state.is_subscribed:
#         return

#     # Otherwise → show login + subscribe UI
#     st.title("SupplyBhai Pro")
#     st.write("Enter your email to continue or subscribe.")

#     email = st.text_input("Work email", value=st.session_state.email or "")

#     col1, col2 = st.columns(2)

#     with col1:
#         if st.button("Continue (I already subscribed)"):
#             if not email:
#                 st.warning("Please enter your email.")
#                 st.stop()
#             st.session_state.email = email
#             customer = get_or_create_customer(email)
#             if customer_has_active_subscription(customer.id):
#                 st.session_state.is_subscribed = True
#                 return
#             else:
#                 st.warning("No active subscription found for this email.")
#                 st.stop()

#     with col2:
#         if st.button("Subscribe now"):
#             if not email:
#                 st.warning("Please enter your email before subscribing.")
#                 st.stop()
#             st.session_state.email = email
#             checkout_url = create_checkout_session(email)
#             st.markdown(f"[Click here to complete payment]({checkout_url})")
#             st.stop()

#     st.stop()

# auth.py

import streamlit as st
import stripe

# Initialize Stripe
stripe.api_key = st.secrets["STRIPE_SECRET_KEY"]

# -----------------------------
# 1. Customer helpers
# -----------------------------
def get_or_create_customer(email: str):
    """Return existing Stripe customer or create a new one."""
    customers = stripe.Customer.list(email=email, limit=1).data
    if customers:
        return customers[0]
    return stripe.Customer.create(email=email)


def customer_subscription_status(customer_id: str):
    """
    Returns one of:
    - 'active'
    - 'trialing'
    - 'past_due'
    - 'canceled'
    - 'incomplete'
    - 'incomplete_expired'
    - 'unpaid'
    - 'none'
    """
    subs = stripe.Subscription.list(
        customer=customer_id,
        limit=1,
    ).data

    if not subs:
        return "none"

    return subs[0].status


# -----------------------------
# 2. Checkout session (with free trial)
# -----------------------------
def create_checkout_session(email: str):
    """Create a Stripe Checkout session for subscription with free trial."""
    customer = get_or_create_customer(email)

    session = stripe.checkout.Session.create(
        customer=customer.id,
        payment_method_types=["card"],
        mode="subscription",
        line_items=[{
            "price": st.secrets["STRIPE_PRICE_ID"],
            "quantity": 1,
        }],
        subscription_data={
            "trial_period_days": st.secrets.get("TRIAL_DAYS", 7)
        },
        success_url=f'{st.secrets["BASE_URL"]}?session_id={{CHECKOUT_SESSION_ID}}',
        cancel_url=f'{st.secrets["BASE_URL"]}?canceled=true',
    )
    return session.url


# -----------------------------
# 3. Customer Portal
# -----------------------------
def create_customer_portal(email: str):
    customer = get_or_create_customer(email)
    session = stripe.billing_portal.Session.create(
        customer=customer.id,
        return_url=st.secrets["BASE_URL"]
    )
    return session.url


# -----------------------------
# 4. Logout
# -----------------------------
def logout():
    st.session_state.clear()
    st.experimental_rerun()


# -----------------------------
# 5. Main paywall logic
# -----------------------------
def require_subscription():
    """
    Main paywall logic.
    Call this at the top of app.py.
    Blocks access until user is subscribed or trialing.
    """

    # Initialize session state
    if "email" not in st.session_state:
        st.session_state.email = None
    if "is_subscribed" not in st.session_state:
        st.session_state.is_subscribed = False

    # Handle Stripe redirect success
    session_id = st.query_params.get("session_id", [None])[0] if hasattr(st, "query_params") else None
    if session_id and st.session_state.email:
        try:
            checkout_session = stripe.checkout.Session.retrieve(session_id)
            customer_id = checkout_session.customer
            status = customer_subscription_status(customer_id)
            if status in ["active", "trialing"]:
                st.session_state.is_subscribed = True
        except Exception:
            pass

    # If subscribed → allow access
    if st.session_state.is_subscribed:
        return

    # Otherwise → show login + subscribe UI
    st.title("SupplyBhai Pro")
    st.write("Enter your email to continue or start your free trial.")

    email = st.text_input("Work email", value=st.session_state.email or "")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Continue (I already subscribed)"):
            if not email:
                st.warning("Please enter your email.")
                st.stop()
            st.session_state.email = email
            customer = get_or_create_customer(email)
            status = customer_subscription_status(customer.id)
            if status in ["active", "trialing"]:
                st.session_state.is_subscribed = True
                return
            else:
                st.warning("No active subscription found for this email.")
                st.stop()

    with col2:
        if st.button(f"Start Free Trial ({st.secrets.get('TRIAL_DAYS', 7)} days)"):
            if not email:
                st.warning("Please enter your email before subscribing.")
                st.stop()
            st.session_state.email = email
            checkout_url = create_checkout_session(email)
            st.markdown(f"[Click here to start your trial]({checkout_url})")
            st.stop()

    st.stop()
