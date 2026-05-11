"""
Smart Campus ANPR – Admin Dashboard  v4
Run: python -m streamlit run web_app.py
"""

import base64
import io
import datetime
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from streamlit_autorefresh import st_autorefresh

load_dotenv(dotenv_path=Path(__file__).parent / ".env", override=True)

st.set_page_config(
    page_title="Smart Campus ANPR",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', sans-serif;
    background-color: #07090f;
    color: #c9d1e0;
}
[data-testid="stAppViewContainer"]   { background: #07090f; }
[data-testid="stHeader"]             { background: transparent !important; height: 0; }
[data-testid="collapsedControl"]     { top: 12px !important; }
#MainMenu, footer, [data-testid="stToolbar"] { display: none !important; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a0d15 0%, #0d1117 100%);
    border-right: 1px solid #1a2030;
}
[data-testid="stSidebar"] * { color: #94a3b8 !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] strong { color: #e2e8f0 !important; }
[data-testid="stSidebar"] [data-testid="stRadio"] label { font-weight: 600 !important; font-size: 14px !important; }

[data-testid="metric-container"] {
    background: #0d1117; border: 1px solid #1a2030;
    border-radius: 14px; padding: 18px 22px;
    transition: transform .2s, box-shadow .2s;
}
[data-testid="metric-container"]:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,.5); }
[data-testid="metric-container"] > label { color: #334155 !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: .08em; font-weight: 600 !important; }
[data-testid="metric-container"] > div > div { color: #f1f5f9 !important; font-size: 28px !important; font-weight: 800 !important; }

.stButton > button {
    border-radius: 9px; border: none; font-weight: 700; font-size: 13px;
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
    color: #fff; padding: 9px 20px; transition: all .2s;
    box-shadow: 0 2px 8px rgba(37,99,235,.3);
}
.stButton > button:hover { background: linear-gradient(135deg, #3b82f6, #2563eb); transform: translateY(-1px); color: #fff; }

.stTextInput > div > div > input,
.stSelectbox > div > div,
.stTextArea textarea {
    background: #0d1117 !important; border: 1px solid #1a2030 !important;
    border-radius: 9px !important; color: #e2e8f0 !important; font-size: 14px !important;
}
.stTextInput > div > div > input:focus { border-color: #3b82f6 !important; }

.stTabs [data-baseweb="tab-list"] { background: #0d1117; border-radius: 10px 10px 0 0; gap: 3px; padding: 5px; border: 1px solid #1a2030; border-bottom: none; }
.stTabs [data-baseweb="tab"]      { border-radius: 7px; color: #475569; font-weight: 600; padding: 7px 16px; font-size: 13px; }
.stTabs [aria-selected="true"]    { background: #1a2030 !important; color: #e2e8f0 !important; }
.stTabs [data-baseweb="tab-panel"]{ background: #0d1117; border: 1px solid #1a2030; border-radius: 0 0 10px 10px; padding: 20px; }

[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; border: 1px solid #1a2030; }
hr { border-color: #0f1520; }

.dot { display:inline-block; width:8px; height:8px; border-radius:50%; }
.dot-g { background:#22c55e; animation: blink 1.5s infinite; }
.dot-r { background:#ef4444; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.3} }

.badge { display:inline-flex; align-items:center; gap:4px; border-radius:6px; padding:3px 9px; font-size:11px; font-weight:700; letter-spacing:.04em; }
.b-auth    { background:rgba(20,83,45,.9);  color:#4ade80; }
.b-unauth  { background:rgba(69,10,10,.9);  color:#f87171; }
.b-suspect { background:rgba(124,45,18,.9); color:#fb923c; border:1px solid #c2410c; }
.b-ok      { background:rgba(20,83,45,.9);  color:#4ade80; }
.b-fix     { background:rgba(30,64,175,.9); color:#93c5fd; }
.b-pend    { background:rgba(71,60,0,.9);   color:#fbbf24; }

.review-card {
    background: #0d1117; border: 1px solid #1a2030;
    border-radius: 14px; margin-bottom: 16px;
    overflow: hidden; transition: border-color .2s;
}
.review-card:hover { border-color: #1e2d45; }
.review-card.pend  { border-left: 4px solid #f59e0b; }
.review-card.ok    { border-left: 4px solid #22c55e; }
.review-card.fix   { border-left: 4px solid #3b82f6; }
.rc-header {
    padding: 12px 18px; background: #0a0d15;
    border-bottom: 1px solid #1a2030;
    display: flex; align-items: center; justify-content: space-between;
}
.rc-plate { font-size: 22px; font-weight: 900; color: #f1f5f9; letter-spacing: .1em; }
.rc-meta  { font-size: 12px; color: #334155; margin-top: 3px; }
.rc-img-placeholder {
    background: #0a0d15; border: 1px dashed #1a2030;
    border-radius: 8px; height: 60px;
    display: flex; align-items: center; justify-content: center;
    color: #1e293b; font-size: 12px;
}
.page-title { font-size: 26px; font-weight: 800; color: #f1f5f9; margin: 0 0 4px; letter-spacing: -.02em; }
.page-sub   { font-size: 13px; color: #334155; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# DB connection
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource(ttl=0)
def get_db():
    from database.db_manager import DBManager
    return DBManager()


db = get_db()

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def access_badge(status: str) -> str:
    s = status.upper()
    if s == "AUTHORIZED":              return '<span class="badge b-auth">✓ AUTHORIZED</span>'
    if s in ("SUSPICIOUS", "ŞÜPHELİ"):return '<span class="badge b-suspect">⚠ SUSPICIOUS</span>'
    return '<span class="badge b-unauth">✗ UNAUTHORIZED</span>'

def review_badge(status: str) -> str:
    if status == "onaylandi":  return '<span class="badge b-ok">✓ Approved</span>'
    if status == "duzeltildi": return '<span class="badge b-fix">✎ Corrected</span>'
    return '<span class="badge b-pend">⏳ Pending</span>'

def show_image(b64: str | None):
    if b64:
        try:
            st.image(base64.b64decode(b64), use_container_width=True)
        except Exception:
            st.markdown('<div class="rc-img-placeholder">Failed to load image</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="rc-img-placeholder">📷 No image</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Sidebar – navigation
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:16px 0 20px">
        <div style="font-size:26px;margin-bottom:4px">🎯</div>
        <div style="font-size:18px;font-weight:800;color:#e2e8f0">Smart Campus</div>
        <div style="font-size:12px;color:#334155;margin-top:2px">ANPR Admin Panel</div>
    </div>
    """, unsafe_allow_html=True)

    db_dot = '<span class="dot dot-g"></span>' if db.collection is not None else '<span class="dot dot-r"></span>'
    db_lbl = "MongoDB Connected"  if db.collection is not None else "DB Disconnected"
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:8px;padding:8px 0;font-size:13px;'
        f'font-weight:600;color:#64748b;margin-bottom:16px">{db_dot}{db_lbl}</div>',
        unsafe_allow_html=True,
    )

    page = st.radio(
        "Page",
        ["📊 Dashboard", "🔍 Plates", "🔐 Access Control", "⚠️ Suspicious Plates"],
        label_visibility="collapsed",
    )

    st.divider()
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()
    st.divider()
    st.caption("Smart Campus ANPR v4 © 2026")

# Auto-refresh every 30 seconds
st_autorefresh(interval=30_000, key="auto_refresh")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: Dashboard
# ─────────────────────────────────────────────────────────────────────────────
if page == "📊 Dashboard":
    st.markdown('<p class="page-title">📊 Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">System-wide overview and recent activity</p>', unsafe_allow_html=True)

    logs = db.son_kayitlari_getir(limit=100)
    total  = len(logs)
    auth   = sum(1 for p, d, t in logs if d == "AUTHORIZED")
    unauth = sum(1 for p, d, t in logs if d == "UNAUTHORIZED")

    plates_data = db.plaka_gorsellerini_getir(limit=200)
    pend = sum(1 for r in plates_data if r["duzeltme_durumu"] == "beklemede")
    appr = sum(1 for r in plates_data if r["duzeltme_durumu"] == "onaylandi")
    corr = sum(1 for r in plates_data if r["duzeltme_durumu"] == "duzeltildi")

    m1, m2, m3, m4, m5 = st.columns(5)
    with m1: st.metric("📊 Total Records",    total)
    with m2: st.metric("✅ Authorized",        auth)
    with m3: st.metric("🚫 Unauthorized",      unauth)
    with m4: st.metric("⏳ Pending Review",    pend)
    with m5: st.metric("✎ Corrected",          corr)

    st.divider()

    col_tbl, col_info = st.columns([2, 1], gap="large")

    with col_tbl:
        st.markdown("**Recent Detections**")
        if logs:
            df = pd.DataFrame(logs, columns=["Plate", "Status", "Time"])
            def _style(val):
                if val == "AUTHORIZED":  return "color:#4ade80;font-weight:700"
                if val == "SUSPICIOUS":  return "color:#fb923c;font-weight:700"
                return "color:#f87171;font-weight:700"
            st.dataframe(
                df.style.map(_style, subset=["Status"]),
                use_container_width=True, height=420, hide_index=True,
            )
        else:
            st.info("No records yet. Run the desktop application to start capturing plates.")

    with col_info:
        st.markdown("**Review Summary**")
        st.markdown(f"""
        <div style="background:#0d1117;border:1px solid #1a2030;border-radius:12px;padding:18px;margin-bottom:12px">
            <div style="display:flex;flex-direction:column;gap:14px">
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <span style="color:#475569;font-size:13px">⏳ Pending</span>
                    <span style="font-size:22px;font-weight:800;color:#fbbf24">{pend}</span>
                </div>
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <span style="color:#475569;font-size:13px">✓ Approved</span>
                    <span style="font-size:22px;font-weight:800;color:#4ade80">{appr}</span>
                </div>
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <span style="color:#475569;font-size:13px">✎ Corrected</span>
                    <span style="font-size:22px;font-weight:800;color:#93c5fd">{corr}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if pend > 0:
            st.warning(f"⏳ **{pend}** plate(s) are waiting for review. Go to the **Plates** page.")

        st.markdown("**Quick Guide**")
        st.markdown("""
        <div style="background:#0d1117;border:1px solid #1a2030;border-radius:12px;padding:14px;font-size:13px;color:#475569;line-height:2">
            🔍 Review plate images on the <strong style="color:#93c5fd">Plates</strong> page.<br>
            🔐 Manage authorized vehicles in <strong style="color:#4ade80">Access Control</strong>.<br>
            ⚠️ Define flagged vehicles under <strong style="color:#fb923c">Suspicious Plates</strong>.
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: Plates (Image Review)
# ─────────────────────────────────────────────────────────────────────────────
elif page == "🔍 Plates":
    st.markdown('<p class="page-title">🔍 Plate Review</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">Compare the model\'s reading against the plate image and correct any errors</p>', unsafe_allow_html=True)

    fcol1, fcol2, fcol3 = st.columns([2, 2, 1])
    with fcol1:
        filtre = st.selectbox(
            "Review status",
            ["All", "Pending", "Approved", "Corrected"],
            label_visibility="collapsed",
        )
    with fcol2:
        search = st.text_input("Search plate", placeholder="34ABC123", label_visibility="collapsed")
    with fcol3:
        limit = st.selectbox("Limit", [20, 50, 100], label_visibility="collapsed")

    filtre_map = {"All": None, "Pending": "beklemede", "Approved": "onaylandi", "Corrected": "duzeltildi"}
    records = db.plaka_gorsellerini_getir(limit=limit, duzeltme_filtre=filtre_map[filtre])

    if search:
        records = [r for r in records if search.upper() in r["plaka_no"].upper()]

    if not records:
        st.info("No records found. Run the desktop application to start capturing plates.")
    else:
        st.markdown(
            f'<p style="color:#334155;font-size:13px;margin-bottom:16px">Showing {len(records)} record(s)</p>',
            unsafe_allow_html=True,
        )

        for rec in records:
            doc_id     = rec["id"]
            plate      = rec["plaka_no"]
            time_str   = rec["tarih_saat"]
            access     = rec["erisim_durumu"]
            image_b64  = rec["plaka_gorseli"]
            rev_status = rec["duzeltme_durumu"]
            corrected  = rec["duzeltilmis_plaka"]

            card_cls = {"beklemede": "pend", "onaylandi": "ok", "duzeltildi": "fix"}.get(rev_status, "pend")

            with st.container():
                st.markdown(f'<div class="review-card {card_cls}">', unsafe_allow_html=True)

                st.markdown(f"""
                <div class="rc-header">
                    <div>
                        <div class="rc-plate">{plate}</div>
                        <div class="rc-meta">{time_str} &nbsp;·&nbsp; {access_badge(access)} &nbsp;·&nbsp; {review_badge(rev_status)}</div>
                    </div>
                    {"<div style='font-size:13px;color:#334155'>✎ Corrected to: <strong style=color:#93c5fd>" + corrected + "</strong></div>" if corrected else ""}
                </div>
                """, unsafe_allow_html=True)

                img_col, info_col = st.columns([1, 2], gap="medium")

                with img_col:
                    st.markdown('<div style="padding:12px 0 12px 16px">', unsafe_allow_html=True)
                    show_image(image_b64)
                    st.markdown("</div>", unsafe_allow_html=True)

                with info_col:
                    st.markdown('<div style="padding:12px 16px 12px 0">', unsafe_allow_html=True)
                    st.markdown(
                        f'<div style="font-size:13px;color:#475569;margin-bottom:10px">'
                        f'Model reading: <strong style="color:#f1f5f9;font-size:18px;letter-spacing:.08em">{plate}</strong></div>',
                        unsafe_allow_html=True,
                    )

                    if rev_status == "beklemede":
                        corrected_input = st.text_input(
                            "Corrected plate",
                            value=plate,
                            key=f"inp_{doc_id}",
                            label_visibility="collapsed",
                            placeholder="Enter correct plate number…",
                        )
                        b1, b2 = st.columns(2)
                        with b1:
                            if st.button("✓ Approve", key=f"appr_{doc_id}", use_container_width=True):
                                db.plaka_onayla(doc_id)
                                st.success("Approved!")
                                st.rerun()
                        with b2:
                            if st.button("✎ Correct & Save", key=f"corr_{doc_id}", use_container_width=True):
                                if corrected_input.strip() and corrected_input.strip() != plate:
                                    db.plaka_duzelt(doc_id, corrected_input.strip())
                                    st.success(f"Corrected: {plate} → {corrected_input.upper()}")
                                    st.rerun()
                                else:
                                    st.warning("Enter a different plate number, or click Approve.")
                    else:
                        msg = "✓ This record has been approved." if rev_status == "onaylandi" else f"✎ Corrected to → **{corrected}**"
                        st.markdown(f'<div style="color:#475569;font-size:13px;padding-top:4px">{msg}</div>', unsafe_allow_html=True)
                        if st.button("↺ Reset to Pending", key=f"reset_{doc_id}"):
                            try:
                                from bson import ObjectId
                                db.collection.update_one(
                                    {"_id": ObjectId(doc_id)},
                                    {"$set": {"duzeltme_durumu": "beklemede", "duzeltilmis_plaka": None}},
                                )
                                st.rerun()
                            except Exception as e:
                                st.error(str(e))

                    st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: Access Control
# ─────────────────────────────────────────────────────────────────────────────
elif page == "🔐 Access Control":
    st.markdown('<p class="page-title">🔐 Access Control</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">Manage authorized vehicles, blacklist, and owner lookup</p>', unsafe_allow_html=True)

    tab_auth, tab_bl, tab_query = st.tabs(["✅ Authorized List", "🚫 Blacklist", "🔍 Owner Lookup"])

    with tab_auth:
        ca, cb, cc, cd = st.columns([2, 2, 1, 1])
        with ca:  ap  = st.text_input("Plate",      key="ap",  placeholder="34ABC123")
        with cb:  asn = st.text_input("Owner Name", key="asn", placeholder="Full Name")
        with cc:
            if st.button("Add / Update", key="btn_aa", use_container_width=True):
                if ap.strip():
                    ok = db.plaka_listesine_ekle(ap.strip(), "authorized", asn.strip())
                    st.success(f"{ap.upper()} added to authorized list.") if ok else st.error("Failed to add.")
                else:
                    st.warning("Please enter a plate number.")
        with cd:
            if st.button("Revoke Access", key="btn_ar", use_container_width=True):
                if ap.strip():
                    ok = db.plaka_listesinden_cikar(ap.strip(), "authorized")
                    st.success(f"{ap.upper()} removed.") if ok else st.error("Failed to remove.")
                else:
                    st.warning("Please enter a plate number.")

    with tab_bl:
        bc1, bc2, bc3 = st.columns([3, 1, 1])
        with bc1: blp = st.text_input("Plate", key="blp", placeholder="34ABC123")
        with bc2:
            if st.button("Add to Blacklist", key="btn_bla", use_container_width=True):
                if blp.strip():
                    ok = db.plaka_listesine_ekle(blp.strip(), "blacklist")
                    st.success(f"{blp.upper()} added to blacklist.") if ok else st.error("Failed to add.")
                else:
                    st.warning("Please enter a plate number.")
        with bc3:
            if st.button("Remove", key="btn_blr", use_container_width=True):
                if blp.strip():
                    ok = db.plaka_listesinden_cikar(blp.strip(), "blacklist")
                    st.success(f"{blp.upper()} removed.") if ok else st.error("Failed to remove.")
                else:
                    st.warning("Please enter a plate number.")

    with tab_query:
        qc1, qc2 = st.columns([3, 1])
        with qc1: qp = st.text_input("Plate to look up", key="qp", placeholder="34ABC123")
        with qc2:
            if st.button("Search", key="btn_q", use_container_width=True):
                if qp.strip():
                    info   = db.sahip_bilgisi_getir(qp.strip())
                    status = db.erisim_durumu_getir(qp.strip())
                    if info:
                        st.success(
                            f"**{info['plaka_no']}** · Owner: **{info['sahip_adi']}** "
                            f"· Type: {info['tip']} · Status: **{status}**"
                        )
                    else:
                        st.warning(f"No registered owner found. Access status: **{status}**")
                else:
                    st.warning("Please enter a plate number.")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: Suspicious Plates
# ─────────────────────────────────────────────────────────────────────────────
elif page == "⚠️ Suspicious Plates":
    st.markdown('<p class="page-title">⚠️ Suspicious Plates</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">Plates flagged here will trigger a red alert in the desktop application</p>', unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#0a0500;border:1px solid #431407;border-radius:10px;padding:12px 16px;margin-bottom:20px;color:#f97316;font-size:13px">
        ⚠️ Plates added to this list will be highlighted with a red bounding box and an alarm in the desktop application.
        They are stored in the <code>blacklist_plates</code> collection in MongoDB.
    </div>
    """, unsafe_allow_html=True)

    sc1, sc2, sc3 = st.columns([3, 1, 1])
    with sc1: sp_in = st.text_input("Plate", key="sp_in", placeholder="34ABC123")
    with sc2:
        if st.button("Flag as Suspicious", key="btn_spa", use_container_width=True):
            if sp_in.strip():
                ok = db.plaka_listesine_ekle(sp_in.strip(), "blacklist")
                st.success(f"{sp_in.upper()} flagged as suspicious.") if ok else st.error("Failed.")
            else:
                st.warning("Please enter a plate number.")
    with sc3:
        if st.button("Remove Flag", key="btn_spr", use_container_width=True):
            if sp_in.strip():
                ok = db.plaka_listesinden_cikar(sp_in.strip(), "blacklist")
                st.success(f"{sp_in.upper()} flag removed.") if ok else st.error("Failed.")
            else:
                st.warning("Please enter a plate number.")

    st.divider()
    st.markdown("**Currently Flagged Plates**")
    if db.blacklist_collection is not None:
        try:
            docs = list(db.blacklist_collection.find({"aktif": True}))
            if docs:
                cols = st.columns(min(len(docs), 5))
                for i, doc in enumerate(docs):
                    with cols[i % 5]:
                        st.markdown(
                            f'<div style="background:#431407;border:1px solid #7c2d12;border-radius:10px;'
                            f'padding:12px;text-align:center;color:#fb923c;font-weight:900;font-size:15px;'
                            f'letter-spacing:.1em;margin-bottom:8px">{doc.get("plaka_no","")}</div>',
                            unsafe_allow_html=True,
                        )
            else:
                st.info("No suspicious plates defined.")
        except Exception as e:
            st.error(str(e))
    else:
        st.warning("MongoDB is not connected.")
