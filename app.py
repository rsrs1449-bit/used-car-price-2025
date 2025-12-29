import streamlit as st
import numpy as np
import joblib

# عنوان التطبيق
st.set_page_config(page_title="توقع سعر السيارة", layout="centered")
st.title("🚗 توقع سعر السيارة المستعملة")

st.write("أدخلي بيانات السيارة وسيتم توقع السعر التقريبي")

# إدخال البيانات
model_year = st.number_input(
    "سنة الموديل",
    min_value=1990,
    max_value=2025,
    value=2020,
    step=1
)

mileage = st.number_input(
    "الممشى (بالكيلومتر)",
    min_value=0,
    max_value=500000,
    value=50000,
    step=1000
)

# زر التوقع
if st.button("توقع السعر"):
    # معادلة بسيطة (مؤقتة للعرض)
    price = (model_year - 2000) * 2500 - (mileage * 0.05) + 30000
    price = max(price, 0)

    st.success(f"💰 السعر المتوقع: {price:,.0f} ريال سعودي")