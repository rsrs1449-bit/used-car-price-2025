import streamlit as st
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from datetime import datetime

# =========================
# إعداد الصفحة
# =========================
st.set_page_config(
    page_title="توقع سعر السيارة المستعملة",
    page_icon="🚗",
    layout="wide"
)

# =========================
# تحميل الموديل
# =========================
@st.cache_resource
def load_model():
    model_path = Path(__file__).parent / "model.pkl"
    return joblib.load(model_path)

model = load_model()

# =========================
# العنوان
# =========================
st.title("🚗 توقع سعر السيارة المستعملة")
st.caption("أدخلي بيانات السيارة وسيتم توقع السعر باستخدام نموذج تعلم آلي")

# =========================
# القوائم
# =========================
BRAND_OPTIONS = [
    "Toyota", "Hyundai", "Kia", "Nissan", "Honda",
    "Mazda", "Ford", "Chevrolet", "BMW", "Mercedes",
    "Lexus", "Audi", "Other"
]

TYPE_OPTIONS = ["Sedan", "SUV", "Hatchback", "Pickup", "Coupe", "Van", "Other"]
GEAR_OPTIONS = ["Automatic", "Manual"]
FUEL_OPTIONS = ["Gasoline", "Diesel", "Hybrid", "Electric", "Other"]
CITY_OPTIONS = ["Riyadh", "Jeddah", "Dammam", "Makkah", "Madinah", "Abha", "Other"]
CONDITION_OPTIONS = ["Excellent", "Very Good", "Good", "Fair"]
COLOR_OPTIONS = ["White", "Black", "Silver", "Gray", "Blue", "Red", "Other"]

# =========================
# Sidebar
# =========================
with st.sidebar:
    st.header("⚙️ الإعدادات")
    show_details = st.toggle("عرض تفاصيل الإدخال", True)
    st.markdown("---")
    st.caption("تأكدي أن أسماء الأعمدة تطابق التدريب")

# =========================
# Tabs
# =========================
tab1, tab2 = st.tabs(["🧾 إدخال البيانات", "📈 النتيجة"])

# =========================
# TAB 1
# =========================
with tab1:
    with st.form("car_form"):
        c1, c2, c3 = st.columns(3)

        with c1:
            year = st.slider("سنة الصنع", 1990, 2025, 2018)
            mileage = st.slider("الممشى (كم)", 0, 500000, 80000, step=1000)
            engine_size = st.slider("سعة المحرك (لتر)", 1.0, 8.0, 2.0, step=0.1)
            cylinders = st.selectbox("عدد السلندرات", [3, 4, 6, 8])

        with c2:
            brand = st.selectbox("الماركة", BRAND_OPTIONS)
            car_type = st.selectbox("نوع السيارة", TYPE_OPTIONS)
            gear = st.selectbox("القير", GEAR_OPTIONS)
            fuel = st.selectbox("نوع الوقود", FUEL_OPTIONS)

        with c3:
            city = st.selectbox("المدينة", CITY_OPTIONS)
            condition = st.selectbox("حالة السيارة", CONDITION_OPTIONS)
            color = st.selectbox("اللون", COLOR_OPTIONS)
            owners = st.slider("عدد الملاك السابقين", 0, 10, 1)

        st.markdown("---")

        c4, c5 = st.columns(2)
        with c4:
            has_accidents = st.selectbox("هل عليها حوادث؟", ["No", "Yes"])
        with c5:
            warranty = st.selectbox("هل عليها ضمان؟", ["No", "Yes"])

        submitted = st.form_submit_button("🔮 توقّع السعر")

    if submitted:
        input_data = pd.DataFrame([{
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
            "warranty": warranty
        }])

        try:
            prediction = model.predict(input_data)[0]
            st.session_state.prediction = prediction
            st.session_state.last_input = input_data
            st.success("تم التوقع بنجاح ✅ انتقلي لتبويب النتيجة")

        except Exception as e:
            st.error("حدث خطأ أثناء التوقع")
            st.exception(e)

        if show_details:
            st.dataframe(input_data, use_container_width=True)

# =========================
# TAB 2
# =========================
with tab2:
    if "prediction" not in st.session_state:
        st.info("قومي بإدخال البيانات أولًا")
    else:
        price = st.session_state.prediction
        st.metric("💰 السعر المتوقع", f"{price:,.0f} ريال")
        st.caption(f"آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

        if show_details:
            st.markdown("### تفاصيل الإدخال")
            st.dataframe(st.session_state.last_input, use_container_width=True)
