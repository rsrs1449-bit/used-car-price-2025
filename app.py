import streamlit as st
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from datetime import datetime

# =========================
# 1) إعداد الصفحة (شكل عام)
# =========================
st.set_page_config(
    page_title="توقع سعر السيارة المستعملة",
    page_icon="🚗",
    layout="wide"
)

# =========================
# 2) CSS بسيط لتحسين الشكل
# =========================
CUSTOM_CSS = """
<style>
    .block-container { padding-top: 1.2rem; padding-bottom: 2rem; }
    .title-box {
        padding: 16px 18px;
        border-radius: 14px;
        background: rgba(240, 242, 246, 0.7);
        border: 1px solid rgba(0,0,0,0.06);
        margin-bottom: 12px;
    }
    .metric-card {
        padding: 14px 16px;
        border-radius: 14px;
        border: 1px solid rgba(0,0,0,0.08);
        background: rgba(255,255,255,0.6);
    }
    .small-muted { color: rgba(0,0,0,0.55); font-size: 0.9rem; }
    .hr { margin: 12px 0 6px; border-top: 1px solid rgba(0,0,0,0.07); }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# =========================
# 3) تحميل الموديل (مرة واحدة)
# =========================
@st.cache_resource
def load_model():
    model_path = Path(__file__).parent / "model.pkl"
    if not model_path.exists():
        raise FileNotFoundError("ملف model.pkl غير موجود بجانب app.py")
    return joblib.load(model_path)

model = load_model()

# =========================
# 4) قوائم الخيارات (عدّليها حسب بياناتك)
# =========================
# مهم: الأفضل تخليها مطابقة لبيانات التدريب
BRAND_OPTIONS = [
    "Toyota", "Hyundai", "Kia", "Nissan", "Honda", "Mazda", "Ford",
    "Chevrolet", "BMW", "Mercedes", "Lexus", "Audi", "Volkswagen", "Other"
]

TYPE_OPTIONS = ["Sedan", "SUV", "Hatchback", "Coupe", "Pickup", "Van", "Other"]
GEAR_OPTIONS = ["Automatic", "Manual"]
FUEL_OPTIONS = ["Gasoline", "Diesel", "Hybrid", "Electric", "Other"]
CITY_OPTIONS = ["Riyadh", "Jeddah", "Dammam", "Makkah", "Madinah", "Abha", "Qassim", "Other"]
CONDITION_OPTIONS = ["Excellent", "Very Good", "Good", "Fair", "Needs Work"]

COLOR_OPTIONS = ["White", "Black", "Silver", "Gray", "Blue", "Red", "Beige", "Other"]

# =========================
# 5) دوال مساعدة
# =========================
def format_sar(x: float) -> str:
    if x is None or np.isnan(x):
        return "-"
    return f"{x:,.0f} ريال"

def build_input_df(inputs: dict) -> pd.DataFrame:
    """تحويل المدخلات لصف DataFrame واحد بنفس أسماء الأعمدة المستخدمة بالتدريب."""
    return pd.DataFrame([inputs])

def safe_predict(input_df: pd.DataFrame) -> float:
    """
    يتوقع السعر.
    ملاحظة: الأفضل يكون model.pkl عبارة عن Pipeline (preprocess + model)
    """
    pred = model.predict(input_df)
    # model.predict يرجع array
    return float(pred[0])

def add_to_history(row: dict):
    if "history" not in st.session_state:
        st.session_state.history = []
    st.session_state.history.insert(0, row)  # آخر شي يطلع فوق

# =========================
# 6) الهيدر (عنوان + وصف)
# =========================
st.markdown(
    """
    <div class="title-box">
        <h2 style="margin:0;">🚗 توقع سعر السيارة المستعملة</h2>
        <div class="small-muted">أدخلي بيانات السيارة وراح يعطيك السعر المتوقع (باستخدام model.pkl).</div>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================
# 7) Sidebar (إعدادات + تلميحات)
# =========================
with st.sidebar:
    st.header("⚙️ إعدادات")
    show_input_details = st.toggle("عرض تفاصيل الإدخال", value=True)
    show_history = st.toggle("عرض سجل التوقعات", value=True)
    enable_sanity_checks = st.toggle("تفعيل فحص منطقي للمدخلات", value=True)
    st.markdown("<div class='hr'></div>", unsafe_allow_html=True)
    st.caption("💡 إذا تغيّر شكل/أسماء الأعمدة في التدريب، لازم تغيّرينها هنا بنفس الاسم بالضبط.")

# =========================
# 8) Tabs (مدخلات / نتائج / معلومات)
# =========================
tab1, tab2, tab3 = st.tabs(["🧾 إدخال البيانات", "📈 النتائج", "ℹ️ معلومات"])

# ================
# TAB 1: إدخال البيانات
# ================
with tab1:
    st.subheader("المدخلات")

    # نموذج إدخال - مرتب على 3 أعمدة
    with st.form("car_form", clear_on_submit=False):
        c1, c2, c3 = st.columns(3)

        # -------- العمود 1: أساسيات رقمية --------
        with c1:
            year = st.slider("سنة الصنع", 1990, 2026, 2018, 1)
            mileage = st.slider("الممشى (كم)", 0, 500_000, 80_000, 1000)
            engine_size = st.slider("سعة المحرك (لتر)", 1.0, 8.0, 2.0, 0.1)
            cylinders = st.selectbox("عدد السلندرات", [3, 4, 5, 6, 8, 10, 12], index=1)

        # -------- العمود 2: مواصفات --------
        with c2:
            brand = st.selectbox("الماركة", BRAND_OPTIONS)
            car_type = st.selectbox("نوع السيارة", TYPE_OPTIONS)
            gear = st.selectbox("القير", GEAR_OPTIONS)
            fuel = st.selectbox("نوع الوقود", FUEL_OPTIONS)

        # -------- العمود 3: سوق/حالة --------
        with c3:
            city = st.selectbox("المدينة", CITY_OPTIONS)
            condition = st.selectbox("حالة السيارة", CONDITION_OPTIONS, index=2)
            color = st.selectbox("اللون", COLOR_OPTIONS)
            owners = st.slider("عدد الملاك السابقين", 0, 10, 1, 1)

        st.markdown("---")

        # قسم إضافي: اختياري
        st.markdown("### خيارات إضافية (اختيارية)")
        c4, c5, c6 = st.columns(3)
        with c4:
            has_accidents = st.selectbox("هل عليها حوادث؟", ["No", "Yes"])
            warranty = st.selectbox("هل عليها ضمان؟", ["No", "Yes"])
        with c5:
            transmission_notes = st.text_input("ملاحظات بسيطة (اختياري)", placeholder="مثال: صيانة وكالة")
        with c6:
            market_segment = st.selectbox("فئة السوق", ["Economy", "Mid", "Luxury"], index=1)

        # زر التوقع
        submitted = st.form_submit_button("🔮 توقّع السعر الآن")

    # ------------- فحص منطقي للمدخلات -------------
    warnings = []
    if enable_sanity_checks:
        current_year = datetime.now().year
        if year > current_year + 1:
            warnings.append("سنة الصنع تبدو أعلى من المتوقع.")
        if mileage > 350_000 and condition in ["Excellent", "Very Good"]:
            warnings.append("الممشى عالي جدًا مقارنة بالحالة المختارة.")
        if engine_size >= 6.0 and fuel == "Electric":
            warnings.append("سعة المحرك مع كهرباء ممكن غير منطقي حسب بياناتك.")

    if warnings:
        for w in warnings:
            st.warning(w)

    # ------------- عند الضغط على توقع -------------
    if submitted:
        # مهم: أسماء الأعمدة تحت لازم تطابق التدريب
        inputs = {
            "year": year,
            "mileage": mileage,
            "engine_size": engine_size,
            "cylinders": cylinders,

            "brand": brand,
            "type": car_type,
            "gear": gear,
            "fuel": fuel,

            "city": city,
            "condition": condition,
            "color": color,
            "owners": owners,

            "has_accidents": has_accidents,
            "warranty": warranty,
            "market_segment": market_segment,

            # نصي: إذا تدريبك ما يدعم نصوص، احذفيه أو لا ترسلينه
            "notes": transmission_notes.strip() if transmission_notes else ""
        }

        X = build_input_df(inputs)

        try:
            pred_price = safe_predict(X)

            # تخزين النتائج في session_state عشان تظهر في Tab النتائج
            st.session_state.last_pred = pred_price
            st.session_state.last_input = X

            # سجل
            add_to_history({
                "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "brand": brand,
                "type": car_type,
                "city": city,
                "year": year,
                "mileage": mileage,
                "pred_price": pred_price
            })

            st.success(f"✅ تم التوقع! انتقلي لتبويب **النتائج** 👈")

        except Exception as e:
            st.error("صار خطأ أثناء التوقع. غالبًا أسماء الأعمدة غير مطابقة للتدريب أو model.pkl ليس Pipeline.")
            st.exception(e)

    if show_input_details and "last_input" in st.session_state:
        st.markdown("### آخر إدخال تم استخدامه")
        st.dataframe(st.session_state.last_input, use_container_width=True)

# ================
# TAB 2: النتائج
# ================
with tab2:
    st.subheader("النتيجة")

    if "last_pred" not in st.session_state:
        st.info("أدخلي بيانات السيارة من تبويب **إدخال البيانات** ثم اضغطي توقّع.")
    else:
        pred_price = st.session_state.last_pred

        # عرض النتيجة بشكل جميل
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("💰 السعر المتوقع", format_sar(pred_price))
            st.markdown("</div>", unsafe_allow_html=True)

        # “مؤشر ثقة” شكلي (اختياري) — إذا ما عندك موديل يعطي uncertainty
        # مجرد تقريب: يقل مع ممشى عالي، يزيد مع سنة أحدث (تقدير شكلي)
        last_input = st.session_state.last_input.iloc[0].to_dict()
        mileage = float(last_input.get("mileage", 0))
        year = int(last_input.get("year", 2015))
        year_score = np.clip((year - 1990) / (2026 - 1990), 0, 1)
        mileage_score = 1 - np.clip(mileage / 400000, 0, 1)
        confidence = 0.35 + 0.35 * year_score + 0.30 * mileage_score
        confidence = float(np.clip(confidence, 0.30, 0.95))

        with m2:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("📌 مؤشر الثقة (تقريبي)", f"{confidence*100:.0f}%")
            st.caption("ملاحظة: هذا مؤشر شكلي لتحسين تجربة العرض، وليس قيمة علمية من النموذج.")
            st.markdown("</div>", unsafe_allow_html=True)

        with m3:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("⏱️ وقت آخر توقع", datetime.now().strftime("%H:%M"))
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")

        # عرض تفاصيل الإدخال
        if show_input_details and "last_input" in st.session_state:
            with st.expander("عرض تفاصيل الإدخال (آخر مرة)"):
                st.dataframe(st.session_state.last_input, use_container_width=True)

        # سجل التوقعات
        if show_history:
            st.markdown("### سجل آخر التوقعات")
            hist = st.session_state.get("history", [])
            if not hist:
                st.caption("لا يوجد سجل بعد.")
            else:
                st.dataframe(pd.DataFrame(hist), use_container_width=True)

# ================
# TAB 3: معلومات
# ================
with tab3:
    st.subheader("معلومات مهمة عشان كل شيء يشتغل بدون مشاكل")

    st.markdown("""
**✅ لازم model.pkl يكون Pipeline جاهز** (Preprocess + Model) عشان يقبل الأعمدة النصية مثل: brand, city, fuel …

**✅ أسماء الأعمدة هنا لازم تطابق التدريب 100%**  
مثال: إذا في التدريب اسم العمود `mileage_km` بدل `mileage` لازم تغيّرينه هنا.

**✅ requirements.txt واحد فقط** (في جذر المشروع)

**✅ مكان الملفات**  
- app.py  
- model.pkl  
- requirements.txt  
بنفس المجلد الرئيسي (Root)

---

### مثال requirements.txt
```txt
streamlit
pandas
numpy
scikit-learn
joblib
