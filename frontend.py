import streamlit as st
import json
import matplotlib.pyplot as plt
import datetime

from backend import extract_text, classify_document, summarize_text
from db import init_db, add_user, check_user, reset_password


def run_app():

    init_db()

    st.set_page_config(page_title="AI Document App", layout="wide")

    # ---------------- SESSION ----------------
    if "user" not in st.session_state:
        st.session_state.user = None

    # =========================
    # LOGIN SYSTEM
    # =========================
    if st.session_state.user is None:

        st.title("🔐 Login System")

        option = st.radio("Choose", ["Login", "Register", "Forgot Password"])

        username = st.text_input("Username")

        if option != "Forgot Password":
            password = st.text_input("Password", type="password")

        # ---------------- REGISTER ----------------
        if option == "Register":
            if st.button("Create Account"):
                if username == "" or password == "":
                    st.error("Fill all fields ❌")
                elif add_user(username, password):
                    st.success("Account created ✅")
                else:
                    st.error("User already exists ❌")

        # ---------------- LOGIN ----------------
        elif option == "Login":
            if st.button("Login"):
                if username == "" or password == "":
                    st.error("Fill all fields ❌")
                elif check_user(username, password):
                    st.session_state.user = username
                    st.session_state.login_time = str(datetime.datetime.now())
                    st.success("Login successful ✅")
                    st.rerun()
                else:
                    st.error("Invalid credentials ❌")

        # ---------------- FORGOT PASSWORD ----------------
        elif option == "Forgot Password":
            new_password = st.text_input("New Password", type="password")

            if st.button("Reset Password"):
                if reset_password(username, new_password):
                    st.success("Password reset successful ✅")
                else:
                    st.error("User not found ❌")

        return

    # =========================
    # AFTER LOGIN
    # =========================
    st.sidebar.success(f"User: {st.session_state.user}")
    st.sidebar.info(f"Login: {st.session_state.login_time}")

    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()

    menu = st.sidebar.selectbox(
        "Menu",
        ["Upload & Analyze", "History Dashboard"]
    )

    # ---------------- HISTORY ----------------
    def load_history():
        try:
            with open("history.json", "r") as f:
                return json.load(f)
        except:
            return []

    def save_history(data):
        history = load_history()
        history.append(data)

        with open("history.json", "w") as f:
            json.dump(history, f, indent=4)

    # =========================
    # UPLOAD PAGE
    # =========================
    if menu == "Upload & Analyze":

        uploaded_file = st.file_uploader("Upload File", type=["pdf", "docx", "txt"])

        if uploaded_file:

            text = extract_text(uploaded_file)

            if st.button("Analyze"):

                category, scores = classify_document(text)
                summary = summarize_text(text)

                st.success(f"Category: {category}")
                st.info(summary)

                # PIE CHART
                labels = list(scores.keys())
                values = list(scores.values())

                filtered = [(l, v) for l, v in zip(labels, values) if v > 0]

                if filtered:
                    l, v = zip(*filtered)
                    fig, ax = plt.subplots()
                    ax.pie(v, labels=l, autopct="%1.1f%%")
                    st.pyplot(fig)

                save_history({
                    "user": st.session_state.user,
                    "category": category,
                    "summary": summary
                })

                st.download_button(
                    "📥 Download Report",
                    f"{category}\n\n{summary}",
                    file_name="report.txt"
                )

    # =========================
    # HISTORY PAGE
    # =========================
    elif menu == "History Dashboard":

        st.subheader("📊 History")

        history = load_history()

        user_history = [h for h in history if h.get("user") == st.session_state.user]

        if st.button("🗑️ Clear History"):
            with open("history.json", "w") as f:
                json.dump([], f)
            user_history = []
            st.success("History cleared ✅")

        if not user_history:
            st.warning("No history yet ⚠️")

        else:
            cats = [h["category"] for h in user_history]

            for i, h in enumerate(user_history[::-1], start=1):
                st.write(f"{i}. {h['category']}")

            count = {}
            for c in cats:
                count[c] = count.get(c, 0) + 1

            fig, ax = plt.subplots()
            ax.bar(count.keys(), count.values())
            st.pyplot(fig)