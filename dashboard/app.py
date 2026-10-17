from pathlib import Path
import sys
import json

import pandas as pd
import streamlit as st

# Project paths
DASHBOARD_DIR = Path(__file__).resolve().parent
DATA_DIR = DASHBOARD_DIR / "data"
ALERTS_PATH = DASHBOARD_DIR / "sample_alerts.csv"
VAULT_PATH = DATA_DIR / "vault_alerts.json"
AUDIT_PATH = DATA_DIR / "audit_log.jsonl"

# Keep the AES key outside the repository.
KEY_PATH = Path.home() / "Downloads" / "aes.key"

# vault.py is inside dashboard/data/
sys.path.insert(0, str(DATA_DIR))
from vault import load_vault, load_key, reidentify


st.set_page_config(
    page_title="The STARK Paradox",
    page_icon="🔐",
    layout="wide",
)

st.title("🔐 The STARK Paradox")
st.caption(
    "IBM Z Datathon | Privacy-Preserving Transaction Risk Review"
)


@st.cache_data
def load_alerts(path, modified_time):
    return pd.read_csv(path)


def read_audit_log():
    if not AUDIT_PATH.exists():
        return pd.DataFrame(
            columns=["time", "reviewer", "token", "reason", "result"]
        )

    records = []
    with AUDIT_PATH.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                records.append(json.loads(line))

    return pd.DataFrame(records)


# Load sample alerts
if not ALERTS_PATH.exists():
    st.error(f"Could not find sample alerts file: {ALERTS_PATH}")
    st.stop()

alerts = load_alerts(
    str(ALERTS_PATH),
    ALERTS_PATH.stat().st_mtime,
)

required_columns = [
    "tx_id",
    "token_customer",
    "token_counterparty",
    "amount",
    "type",
    "risk_score",
    "top_reason",
    "timestamp",
]

missing = [
    column for column in required_columns
    if column not in alerts.columns
]

if missing:
    st.error(f"Missing CSV columns: {', '.join(missing)}")
    st.stop()

# Ensure scores are numeric
alerts["risk_score"] = pd.to_numeric(
    alerts["risk_score"], errors="coerce"
)
alerts = alerts.dropna(subset=["risk_score"]).copy()

# Role selection
st.sidebar.header("Access")
role = st.sidebar.radio("Select role", ["Analyst", "Reviewer"])

st.sidebar.caption(
    "Demo role selector only. Production access requires authenticated roles."
)

# Filters
st.sidebar.header("Filters")

transaction_types = sorted(
    alerts["type"].dropna().astype(str).unique().tolist()
)

selected_types = st.sidebar.multiselect(
    "Transaction type",
    transaction_types,
    default=transaction_types,
)

minimum = float(alerts["risk_score"].min())
maximum = float(alerts["risk_score"].max())

if minimum == maximum:
    score_range = (minimum, maximum)
else:
    score_range = st.sidebar.slider(
        "Risk score range",
        min_value=minimum,
        max_value=maximum,
        value=(minimum, maximum),
    )

filtered = alerts[
    alerts["type"].astype(str).isin(selected_types)
    & alerts["risk_score"].between(
        score_range[0], score_range[1]
    )
].copy()

# Rank filtered rows by score; scores are not probabilities.
filtered = filtered.sort_values(
    "risk_score", ascending=False
).copy()

filtered["alert_rank"] = range(1, len(filtered) + 1)


def rank_band(rank):
    if rank <= 100:
        return "Top 100"
    elif rank <= 300:
        return "101–300"
    elif rank <= 1000:
        return "301–1,000"
    return "Remaining"


filtered["rank_band"] = filtered["alert_rank"].apply(rank_band)

# Show reasons only for the top 1,000 ranked rows.
filtered["top_reason"] = filtered["top_reason"].where(
    filtered["alert_rank"] <= 1000,
    "",
)

display_columns = [
    "tx_id",
    "token_customer",
    "token_counterparty",
    "amount",
    "type",
    "risk_score",
    "rank_band",
    "top_reason",
    "timestamp",
]

st.subheader(f"{role} Dashboard")

c1, c2, c3 = st.columns(3)
c1.metric("Total rows", len(filtered))
c2.metric("Top 100 ranked rows", min(len(filtered), 100))
c3.metric(
    "Average risk score (ranking only)",
    f"{filtered['risk_score'].mean():.2f}"
    if not filtered.empty else "N/A",
)

st.dataframe(
    filtered[display_columns],
    use_container_width=True,
    hide_index=True,
)

# Reviewer workflow
if role == "Reviewer":
    st.divider()
    review_tab, audit_tab = st.tabs(
        ["Re-identify", "Audit Log"]
    )

    with review_tab:
        st.subheader("Authorized Re-identification")

        if filtered.empty:
            st.info("No rows match the selected filters.")
        else:
            token_options = (
                filtered["token_customer"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

            if not token_options:
                st.info("No customer tokens are available.")
            else:
                selected_token = st.selectbox(
                    "Select customer token",
                    token_options,
                )

                reviewer_name = st.text_input("Reviewer name")
                reason = st.text_area(
                    "Reason for re-identification",
                    placeholder=(
                        "Explain why access to the original ID is necessary."
                    ),
                )

                if st.button("Re-identify", type="primary"):
                    if not reviewer_name.strip() or not reason.strip():
                        st.error(
                            "Reviewer name and reason are required."
                        )
                    elif not KEY_PATH.is_file():
                        st.error(
                            "AES key not found. Place aes.key in your "
                            "Downloads folder, outside the repository."
                        )
                    elif not VAULT_PATH.is_file():
                        st.error("Encrypted token vault was not found.")
                    else:
                        try:
                            vault = load_vault(str(VAULT_PATH))
                            aes_key = load_key(str(KEY_PATH))

                            original_id = reidentify(
                                selected_token,
                                reviewer_name,
                                reason,
                                vault,
                                aes_key,
                                audit_path=str(AUDIT_PATH),
                            )

                            if original_id is None:
                                st.error(
                                    "Re-identification failed. Check the "
                                    "token, vault, and encryption key."
                                )
                            else:
                                st.success(
                                    "Re-identification completed."
                                )
                                st.write("Original customer ID:")
                                st.code(original_id)

                        except (ValueError, OSError, KeyError) as error:
                            st.error(
                                f"Request could not be completed: {error}"
                            )

    with audit_tab:
        st.subheader("Re-identification Audit Log")
        audit = read_audit_log()

        if audit.empty:
            st.info("No audit entries yet.")
        else:
            st.dataframe(
                audit,
                use_container_width=True,
                hide_index=True,
            )