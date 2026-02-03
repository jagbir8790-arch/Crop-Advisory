import streamlit as st
import matplotlib.pyplot as plt
import tempfile
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from logic.recommender import recommend, load_csv, extract_average_yield


# 🌐 Language dictionary
LANGUAGES = {
    "English": {
        "title": "🌾 Offline Crop Advisory System",
        "soil": "Select Soil Type",
        "season": "Select Season",
        "rainfall": "Rainfall Level",
        "climate": "🌍 Climate-Resilient Mode",
        "button": "Get Recommendation",
        "crop": "Recommended Crop",
        "fertilizer": "Fertilizer",
        "quantity": "Quantity",
        "yield": "Expected Yield",
        "income": "Estimated Income",
        "why": "Why this crop?",
        "download": "📄 Download Advisory PDF",
    },
    "Hindi": {
        "title": "🌾 ऑफलाइन फसल सलाह प्रणाली",
        "soil": "मिट्टी चुनें",
        "season": "मौसम चुनें",
        "rainfall": "वर्षा स्तर",
        "climate": "🌍 जलवायु-सहिष्णु मोड",
        "button": "सलाह प्राप्त करें",
        "crop": "अनुशंसित फसल",
        "fertilizer": "उर्वरक",
        "quantity": "मात्रा",
        "yield": "अपेक्षित उत्पादन",
        "income": "अनुमानित आय",
        "why": "यह फसल क्यों?",
        "download": "📄 सलाह PDF डाउनलोड करें",
    }
}


st.set_page_config(page_title="Crop Advisory", page_icon="🌾")

language = st.selectbox("Language / भाषा", ["English", "Hindi"])
TEXT = LANGUAGES[language]

st.title(TEXT["title"])

soil = st.selectbox(TEXT["soil"], ["Alluvial", "Black", "Red", "Laterite", "Sandy", "Loamy", "Clay"])
season = st.selectbox(TEXT["season"], ["Kharif", "Rabi","Zaid"])
rainfall = st.selectbox(TEXT["rainfall"], ["Low", "Medium", "High"])
climate_mode = st.checkbox(TEXT["climate"])


def generate_pdf(result):
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(temp.name, pagesize=A4)
    text = c.beginText(40, 800)

    for line in [
        TEXT["title"],
        f"{TEXT['crop']}: {result['crop']}",
        f"{TEXT['fertilizer']}: {result['fertilizer']}",
        f"{TEXT['quantity']}: {result['quantity']}",
        f"{TEXT['yield']}: {result['yield']}",
        f"{TEXT['income']}: {result['income']}",
        "",
        TEXT["why"],
        result["explanation"],
    ]:
        text.textLine(line)

    c.drawText(text)
    c.showPage()
    c.save()
    return temp.name


def plot_yield_chart(crop, soil):
    rules = load_csv("data/crop_rules.csv")
    yields = load_csv("data/yield.csv")

    crops, values = [], []
    for r in rules:
        if r["soil"] == soil.lower():
            y = next((y for y in yields if y["crop"] == r["crop"]), None)
            if y:
                avg = extract_average_yield(y["expected_yield"])
                if avg:
                    crops.append(r["crop"])
                    values.append(avg)

    fig, ax = plt.subplots()
    bars = ax.bar(crops, values)
    for i, c in enumerate(crops):
        if c == crop.lower():
            bars[i].set_color("green")

    ax.set_ylabel("Avg Yield (quintals/acre)")
    ax.set_title("Yield Comparison")
    st.pyplot(fig)


if st.button(TEXT["button"]):
    result = recommend(soil, season, rainfall, climate_mode)

    if result:
        st.success(f"{TEXT['crop']}: {result['crop']}")
        st.write(f"{TEXT['fertilizer']}: {result['fertilizer']}")
        st.write(f"{TEXT['quantity']}: {result['quantity']}")
        st.write(f"{TEXT['yield']}: {result['yield']}")
        st.write(f"{TEXT['income']}: {result['income']}")
        st.info(result["explanation"])

        plot_yield_chart(result["crop"], soil)

        pdf = generate_pdf(result)
        with open(pdf, "rb") as f:
            st.download_button(TEXT["download"], f, "crop_advisory.pdf")
