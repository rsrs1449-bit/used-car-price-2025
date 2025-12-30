import streamlit as st
import pandas as pd
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
# العنوان
# =========================
st.title("🚗 توقع سعر السيارة المستعملة")
st.caption("تطبيق ويب لتقدير سعر السيارة المستعملة بناءً على بيانات الإدخال")

# =========================
# Sidebar
# =========================
with st.sidebar:
    st.header("⚙️ الإعدادات")
    show_details = st.toggle("عرض تفاصيل الإدخال", True)
    st.markdown("---")
    st.caption("هذا الإصدار مخصص للعرض والتسليم الأكاديمي")

# =========================
# القوائم
# =========================
BRAND_OPTIONS = ["Toyota", "Hyundai", "Kia", "Nissan", "Honda", "BMW", "Mercedes", "Other"]
TYPE_OPTIONS = ["Sedan", "SUV", "Hatchback", "Pickup", "Coupe", "Other"]
GEAR_OPTIONS = ["Automatic", "Manual"]
FUEL_OPTIONS = ["Gasoline", "Diesel", "Hybrid", "Electric"]
CITY_OPTIONS = ["Riyadh", "Jeddah", "Dammam", "Makkah", "Madinah"]
CONDITION_OPTIONS = ["Excellent", "Very Good", "Good", "Fair"]
COLOR_OPTIONS = ["White", "Black", "Silver", "Gray", "Other"]

# =========================
# Tabs
# =========================
tab1, tab2, tab3 = st.tabs(["🧾 إدخال البيانات", "📈 النتيجة", "ℹ️ عن المشروع"])

# =========================
# TAB 1: إدخال البيانات
# =========================
with tab1:
    with st.form("car_form"):
        c1, c2, c3 = st.columns(3)

        with c1:
            year = st.slider("سنة الصنع", 1990, 2025, 2018)
            mileage = st.slider("الممشى (كم)", 0, 500000, 80000, step=1000)
            engine_size = st.slider("سعة المحرك (لتر)", 1.0, 8.0, 2.0, step=0.1)

        with c2:
            brand = st.selectbox("الماركة", BRAND_OPTIONS)
            car_type = st.selectbox("نوع السيارة", TYPE_OPTIONS)
            gear = st.selectbox("نوع القير", GEAR_OPTIONS)

        with c3:
            fuel = st.selectbox("نوع الوقود", FUEL_OPTIONS)
            city = st.selectbox("المدينة", CITY_OPTIONS)
            condition = st.selectbox("حالة السيارة", CONDITION_OPTIONS)

        color = st.selectbox("اللون", COLOR_OPTIONS)
        owners = st.slider("عدد الملاك السابقين", 0, 10, 1)
        has_accidents = st.selectbox("هل عليها حوادث؟", ["No", "Yes"])

        submitted = st.form_submit_button("🔮 توقّع السعر")

    if submitted:
        # =========================
        # تنبؤ تجريبي (للعرض فقط)
        # =========================
        base_price = 60000
        year_factor = (year - 2010) * 1200
        mileage_factor = -(mileage / 1000) * 150
        engine_factor = engine_size * 4000
        accident_factor = -7000 if has_accidents == "Yes" else 0

        predicted_price = base_price + year_factor + mileage_factor + engine_factor + accident_factor
        predicted_price = max(predicted_price, 15000)

        st.session_state.prediction = predicted_price
        st.session_state.last_input = pd.DataFrame([{
            "year": year,
            "mileage": mileage,
            "engine_size": engine_size,
            "brand": brand,
            "type": car_type,
            "gear": gear,
            "fuel": fuel,
            "city": city,
            "condition": condition,
            "color": color,
            "owners": owners,
            "accidents": has_accidents
        }])

        st.success("✅ تم التوقع بنجاح! انتقلي لتبويب النتيجة.")

        if show_details:
            st.dataframe(st.session_state.last_input, use_container_width=True)

# =========================
# TAB 2: النتيجة
# =========================
with tab2:
    if "prediction" not in st.session_state:
        st.info("يرجى إدخال البيانات أولًا.")
    else:
        st.metric("💰 السعر المتوقع", f"{st.session_state.prediction:,.0f} ريال")
        st.caption(f"وقت التوقع: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# =========================
# TAB 3: عن المشروع
# =========================
with tab3:
    st.subheader("عن المشروع")
    st.write(
        "هذا المشروع عبارة عن تطبيق ويب يستخدم فكرة التنبؤ بأسعار السيارات المستعملة. "
        "تم تصميم واجهة تفاعلية باستخدام Streamlit تسمح للمستخدم بإدخال بيانات السيارة "
        "ويتم عرض السعر المتوقع بشكل فوري."
    )

    st.subheader("أهداف المشروع")
    st.write(
        "- فهم آلية بناء تطبيقات تعلم آلي\n"
        "- ربط النماذج بواجهات ويب\n"
        "- تحسين تجربة المستخدم\n"
        "- تطبيق المفاهيم النظرية بشكل عملي"
    )

    st.subheader("التقنيات المستخدمة")
    st.write(
        "- Python\n"
        "- Streamlit\n"
        "- Pandas\n"
        "- مفاهيم التعلم الآلي"
    )
