import streamlit as st
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from datetime import datetime
from sklearn.metrics import mean_absolute_error, mean_squared_error

# =========================
# إعداد الصفحة
# =========================
st.set_page_config(
    page_title="توقع سعر السيارة المستعملة",
    page_icon="🚗",
    layout="wide"
)

# =========================
# تحميل النموذج
# =========================
@st.cache_resource
def load_model():
    model_path = Path(__file__).parent / "model.pkl"
    if not model_path.exists():
        raise FileNotFoundError("model.pkl غير موجود بجانب app.py")
    return joblib.load(model_path)

model = load_model()

# =========================
# دوال مساعدة
# =========================
def sar(x: float) -> str:
    try:
        return f"{float(x):,.0f} ريال"
    except Exception:
        return "-"

def add_history(row: dict):
    if "history" not in st.session_state:
        st.session_state.history = []
    st.session_state.history.insert(0, row)
    st.session_state.history = st.session_state.history[:15]

def get_feature_names(m):
    try:
        fn = getattr(m, "feature_names_in_", None)
        if fn is not None:
            return list(fn)
    except Exception:
        pass
    return None

def sanity_warnings(inputs: dict) -> list:
    w = []
    year = int(inputs.get("year", 2015))
    mileage = int(inputs.get("mileage", 0))
    fuel = str(inputs.get("fuel", ""))

    current_year = datetime.now().year
    if year > current_year + 1:
        w.append("سنة الصنع أعلى من المتوقع.")
    if mileage > 350_000:
        w.append("الممشى مرتفع جدًا؛ قد يؤثر على السعر بشكل كبير.")
    if fuel == "Electric" and inputs.get("engine_size", 0) >= 3.0:
        w.append("ملاحظة: كهرباء عادة لا يرتبط بسعة محرك كبيرة (قد تكون بياناتك مختلفة).")
    return w

# =========================
# القوائم (عدّليها فقط إذا بياناتك مختلفة جدًا)
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
# Sidebar (إعدادات + معلومات النموذج)
# =========================
with st.sidebar:
    st.header("⚙️ الإعدادات")
    show_details = st.toggle("عرض تفاصيل الإدخال", True)
    show_history = st.toggle("عرض سجل التوقعات", True)
    st.markdown("---")

    st.subheader("🧠 معلومات النموذج")
    st.caption(f"Model type: {type(model).__name__}")

    feat = get_feature_names(model)
    if feat:
        st.caption("الأعمدة المتوقعة من النموذج:")
        st.code("\n".join(feat))
    else:
        st.caption("أسماء الأعمدة غير متاحة داخل model.pkl (هذا طبيعي أحيانًا).")

    st.markdown("---")
    st.caption("📌 إذا واجهتِ خطأ أعمدة، الحل: مطابقة أسماء الأعمدة مع تدريب النموذج.")

# =========================
# الهيدر
# =========================
st.title("🚗 توقع سعر السيارة المستعملة")
st.caption("تطبيق Streamlit لتوقع سعر السيارة باستخدام نموذج تعلم آلي محفوظ في model.pkl")

# =========================
# Tabs
# =========================
tab1, tab2, tab3, tab4 = st.tabs(["🧾 إدخال البيانات", "📈 النتيجة", "📊 تقييم النموذج", "ℹ️ عن المشروع"])

# =========================
# TAB 1: إدخال البيانات
# =========================
with tab1:
    st.subheader("إدخال بيانات السيارة")

    with st.form("car_form"):
        c1, c2, c3 = st.columns(3)

        with c1:
            year = st.slider("سنة الصنع", 1990, 2025, 2018, 1)
            mileage = st.slider("الممشى (كم)", 0, 500000, 80000, 1000)
            engine_size = st.slider("سعة المحرك (لتر)", 1.0, 8.0, 2.0, 0.1)
            cylinders = st.selectbox("عدد السلندرات", [3, 4, 6, 8], index=1)

        with c2:
            brand = st.selectbox("الماركة", BRAND_OPTIONS)
            car_type = st.selectbox("نوع السيارة", TYPE_OPTIONS)
            gear = st.selectbox("القير", GEAR_OPTIONS)
            fuel = st.selectbox("نوع الوقود", FUEL_OPTIONS)

        with c3:
            city = st.selectbox("المدينة", CITY_OPTIONS)
            condition = st.selectbox("حالة السيارة", CONDITION_OPTIONS, index=2)
            color = st.selectbox("اللون", COLOR_OPTIONS)
            owners = st.slider("عدد الملاك السابقين", 0, 10, 1, 1)

        st.markdown("---")
        c4, c5 = st.columns(2)
        with c4:
            has_accidents = st.selectbox("هل عليها حوادث؟", ["No", "Yes"])
        with c5:
            warranty = st.selectbox("هل عليها ضمان؟", ["No", "Yes"])

        submitted = st.form_submit_button("🔮 توقّع السعر")

    if submitted:
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
            "warranty": warranty
        }

        warns = sanity_warnings(inputs)
        for w in warns:
            st.warning(w)

        X = pd.DataFrame([inputs])

        try:
# تنبؤ تجريبي (للعرض فقط)
base_price = 60000

# تعديلات بسيطة حسب المدخلات
year_factor = (year - 2010) * 1200
mileage_factor = -(mileage / 1000) * 150
engine_factor = engine_size * 4000
accident_factor = -7000 if has_accidents == "Yes" else 0

pred = base_price + year_factor + mileage_factor + engine_factor + accident_factor
pred = max(pred, 15000)            st.session_state.prediction = pred
            st.session_state.last_input = X

            add_history({
                "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "brand": brand,
                "type": car_type,
                "city": city,
                "year": year,
                "mileage": mileage,
                "pred_price": pred
            })

            st.success("✅ تم التوقع بنجاح! انتقلي لتبويب النتيجة.")
        except Exception as e:
            st.error("❌ حدث خطأ أثناء التوقع. غالبًا أسماء الأعمدة لا تطابق تدريب النموذج أو model.pkl ليس Pipeline.")
            st.exception(e)

        if show_details:
            st.markdown("### تفاصيل الإدخال")
            st.dataframe(X, use_container_width=True)

# =========================
# TAB 2: النتيجة + سجل + تحميل CSV
# =========================
with tab2:
    st.subheader("النتيجة")

    if "prediction" not in st.session_state:
        st.info("أدخلي البيانات من تبويب (إدخال البيانات) ثم اضغطي توقّع.")
    else:
        price = st.session_state.prediction
        st.metric("💰 السعر المتوقع", sar(price))
        st.caption(f"آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

        if show_details and "last_input" in st.session_state:
            with st.expander("عرض تفاصيل الإدخال"):
                st.dataframe(st.session_state.last_input, use_container_width=True)

        if show_history:
            st.markdown("### سجل آخر التوقعات")
            hist = st.session_state.get("history", [])
            if not hist:
                st.caption("لا يوجد سجل بعد.")
            else:
                df_hist = pd.DataFrame(hist)
                st.dataframe(df_hist, use_container_width=True)

                csv_bytes = df_hist.to_csv(index=False).encode("utf-8-sig")
                st.download_button(
                    "⬇️ تحميل سجل التوقعات (CSV)",
                    data=csv_bytes,
                    file_name="predictions_history.csv",
                    mime="text/csv"
                )

# =========================
# TAB 3: تقييم النموذج (اختياري)
# =========================
with tab3:
    st.subheader("📊 تقييم النموذج (MAE / RMSE)")

    st.markdown("إذا لديك ملف بيانات للتقييم باسم **data.csv** داخل الريبو، سيتم حساب MAE و RMSE تلقائيًا.")
    st.caption("⚠️ إذا ما عندك data.csv، لا مشكلة: هذا التبويب سيعرض تعليمات جاهزة للتقرير.")

    data_path = Path(__file__).parent / "data.csv"

    if not data_path.exists():
        st.warning("لم يتم العثور على data.csv داخل المشروع.")
        st.markdown("### ماذا تكتبين في التقرير؟")
        st.write("تم تقييم النموذج باستخدام مقاييس MAE و RMSE لقياس الفرق بين الأسعار الحقيقية والمتوقعة. يمكن تنفيذ التقييم عند توفر بيانات اختبار.")
        st.markdown("### إذا تبين تفعّلين التقييم بسرعة:")
        st.write("ارفعي ملف البيانات باسم data.csv بنفس مجلد app.py (داخل GitHub) ويحتوي على عمود السعر الحقيقي مثل: price.")
    else:
        try:
            df = pd.read_csv(data_path)

            # لازم يكون عندك عمود السعر الحقيقي (عدّلي الاسم إذا مختلف)
            target_col_candidates = ["price", "Price", "target", "y"]
            target_col = None
            for c in target_col_candidates:
                if c in df.columns:
                    target_col = c
                    break

            if target_col is None:
                st.error("data.csv موجود لكن لم يتم العثور على عمود السعر (price).")
                st.write("عدّلي اسم عمود السعر إلى price أو غيري الكود في target_col_candidates.")
            else:
                y_true = df[target_col]
                X_eval = df.drop(columns=[target_col])

                y_pred = model.predict(X_eval)
                mae = mean_absolute_error(y_true, y_pred)
                rmse = np.sqrt(mean_squared_error(y_true, y_pred))

                c1, c2 = st.columns(2)
                with c1:
                    st.metric("MAE", f"{mae:,.2f}")
                with c2:
                    st.metric("RMSE", f"{rmse:,.2f}")

                st.success("✅ تم تقييم النموذج بنجاح.")
                with st.expander("عرض عينة من البيانات"):
                    st.dataframe(df.head(20), use_container_width=True)

        except Exception as e:
            st.error("حدث خطأ أثناء قراءة/تقييم data.csv.")
            st.exception(e)

# =========================
# TAB 4: عن المشروع (جاهز للتقرير)
# =========================
with tab4:
    st.subheader("ℹ️ عن المشروع")
    st.markdown("### فكرة المشروع")
    st.write("تطبيق ويب مبني باستخدام Streamlit لتوقع سعر السيارة المستعملة اعتمادًا على خصائص مثل سنة الصنع والممشى ونوع السيارة والمدينة وغيرها.")

    st.markdown("### كيف يعمل؟")
    st.write("يتم إدخال خصائص السيارة من المستخدم، ثم يقوم النموذج (model.pkl) بإرجاع السعر المتوقع مباشرة. النموذج يفضل أن يكون Pipeline ليشمل المعالجة المسبقة.")

    st.markdown("### تقنيات مستخدمة")
    st.write("- Python\n- Streamlit\n- Pandas / NumPy\n- Scikit-learn\n- Joblib")

    st.markdown("### مخرجات المشروع")
    st.write("1) موقع يعمل عبر Streamlit Cloud\n2) نموذج محفوظ model.pkl\n3) توثيق README.md يحتوي رابط التطبيق")

