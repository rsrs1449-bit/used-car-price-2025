import streamlit as st
import pandas as pd
import joblib

# إعداد الصفحة
st.set_page_config(
    page_title="توقع سعر السيارة",
    page_icon="🚗",
    layout="centered"
)

# تحميل الموديل
model = joblib.load("model.pkl")

# العنوان
st.markdown("<h1 style='text-align:center;'>🚗 توقع سعر السيارة المستعملة</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:gray;'>أدخلي بيانات السيارة وسنحسب السعر المتوقع</p>", unsafe_allow_html=True)
st.divider()

# قسم البيانات الأساسية
st.subheader("📌 بيانات السيارة الأساسية")

col1, col2 = st.columns(2)
with col1:
    brand = st.selectbox("الشركة", ["Toyota","Honda","Nissan","BMW","Mercedes","Hyundai","Kia","Other"])
    model_name = st.text_input("الموديل", "Camry")

with col2:
    model_year = st.slider("سنة الصنع", 1990, 2025, 2020)
    mileage = st.slider("الممشى (كم)", 0, 500000, 50000, step=5000)

# قسم المواصفات
st.subheader("⚙️ المواصفات")

col3, col4 = st.columns(2)
with col3:
    fuel_type = st.selectbox("نوع الوقود", ["Gasoline","Diesel","Hybrid","Electric"])
    transmission = st.selectbox("ناقل الحركة", ["Automatic","Manual"])

with col4:
    engine = st.text_input("المحرك", "2.5L")
    accident = st.selectbox("حوادث سابقة؟", ["No","Yes"])

# الألوان
st.subheader("🎨 الألوان")
col5, col6 = st.columns(2)
with col5:
    ext_col = st.text_input("اللون الخارجي", "White")
with col6:
    int_col = st.text_input("اللون الداخلي", "Black")

clean_title = st.selectbox("العنوان نظيف؟", ["Yes","No"])

st.divider()

# زر التنبؤ
if st.button("💰 احسب السعر المتوقع"):
    input_df = pd.DataFrame([{
        "brand": brand,
        "model": model_name,
        "model_year": model_year,
        "mileage": mileage,
        "fuel_type": fuel_type,
        "engine": engine,
        "transmission": transmission,
        "ext_col": ext_col,
        "int_col": int_col,
        "accident": accident,
        "clean_title": clean_title
    }])

    price = model.predict(input_df)[0]
    st.success(f"💵 السعر المتوقع: {price:,.0f} ريال سعودي")
