# app.py
import streamlit as st
from gluten_rules import scan_ingredients
from ocr_utils import extract_text_from_image
from food_database import FOOD_DATABASE

st.set_page_config(page_title="CeliacAI — Gluten Scanner", page_icon="🌾")
st.title("CeliacAI — Gluten Scanner")


def get_ingredient_text_input(key_prefix):
    input_method = st.radio(
        "How do you want to enter ingredients?",
        ["Type ingredients", "Take a photo", "Upload a photo"],
        key=f"{key_prefix}_input_method",
    )

    ingredient_text = ""

    if input_method == "Type ingredients":
        ingredient_text = st.text_area("Ingredient list", key=f"{key_prefix}_typed_text")
    elif input_method == "Take a photo":
        camera_image = st.camera_input(
            "Take a photo of the ingredient label",
            key=f"{key_prefix}_camera_input",
        )
        if camera_image:
            try:
                extracted = extract_text_from_image(camera_image)
                ingredient_text = st.text_area(
                    "Extracted text (edit if OCR got something wrong)",
                    value=extracted,
                    key=f"{key_prefix}_camera_extracted_text",
                )
            except Exception as e:
                st.error(f"Couldn't read text from that image: {e}")
    else:
        uploaded_image = st.file_uploader(
            "Upload a photo of the ingredient label",
            type=["jpg", "jpeg", "png", "heic"],
            key=f"{key_prefix}_file_uploader",
        )
        if uploaded_image:
            try:
                extracted = extract_text_from_image(uploaded_image)
                ingredient_text = st.text_area(
                    "Extracted text (edit if OCR got something wrong)",
                    value=extracted,
                    key=f"{key_prefix}_upload_extracted_text",
                )
            except Exception as e:
                st.error(f"Couldn't read text from that image: {e}")

    return ingredient_text

mode = st.radio(
    "What are you doing?",
    ["🛒 Shopping (quick check, not saved)", "🍽️ Eating (track this food)"],
)

st.divider()

if mode.startswith("🛒"):
    st.header("Shopping Mode")
    st.caption("Quick check before you buy. This result is not saved.")

    ingredient_text = get_ingredient_text_input("shopping")

    if st.button("Check This Product"):
        if not ingredient_text.strip():
            st.warning("Please enter an ingredient list first.")
        else:
            result = scan_ingredients(ingredient_text)

            st.markdown(f"**Gluten status prediction:** {result['status']}")
            st.progress(result['confidence'] / 100)
            st.write(f"**Confidence score:** {result['confidence']}%")

            detected = ", ".join(result['matched_ingredients']) or "None"
            st.write(f"**Gluten-related ingredients detected:** {detected}")

            st.write(f"**Explanation:** {result['explanation']}")
            st.write(f"**Recommendation:** {result['recommendation']}")

else:
    st.header("Eating Mode")

    def _fill_food_name_from_suggestion():
        if st.session_state.food_suggestion:
            st.session_state.food_name = st.session_state.food_suggestion

    food_name = st.text_input("Type the food name", key="food_name")

    st.selectbox(
        "Or pick from a small sample list (optional)",
        [""] + FOOD_DATABASE,
        key="food_suggestion",
        on_change=_fill_food_name_from_suggestion,
        help="Optional — just a small starter list to browse, not a real "
             "connected food database yet. Typing above works for anything.",
    )

    food_type = st.radio(
        "What kind of food is this?",
        ["Packaged/Processed", "Homemade", "Restaurant"],
    )

    if food_type == "Packaged/Processed":
        ingredient_text = get_ingredient_text_input("eating")

        if st.button("Scan Ingredients"):
            if not ingredient_text.strip():
                st.warning("Please enter an ingredient list first.")
            else:
                result = scan_ingredients(ingredient_text)

                st.subheader(f"Results for: {food_name or 'this food'}")
                st.markdown(f"**Gluten status prediction:** {result['status']}")
                st.progress(result['confidence'] / 100)
                st.write(f"**Confidence score:** {result['confidence']}%")

                detected = ", ".join(result['matched_ingredients']) or "None"
                st.write(f"**Gluten-related ingredients detected:** {detected}")

                st.write(f"**Explanation:** {result['explanation']}")
                st.write(f"**Recommendation:** {result['recommendation']}")

                st.caption("Not saved yet — Food Log saving is coming in the next phase.")

    else:
        contained_flour = st.checkbox("Did it contain flour or a flour-based ingredient? (optional)")

        if st.button("Log This Food"):
            st.subheader(f"Results for: {food_name or 'this food'}")
            st.write(f"**Gluten status prediction:** Unknown ingredients ({food_type})")
            if contained_flour:
                st.write("**Note:** marked as possibly containing flour — treat with caution.")
            st.write(
                "**Explanation:** Homemade and restaurant foods aren't scanned because the "
                "exact ingredients and preparation aren't known."
            )
            st.write("**Recommendation:** Check further")
            st.caption("Not saved yet — Food Log saving is coming in the next phase.")

st.caption(
    "CeliacAI screens ingredient text against a curated gluten-keyword list. "
    "It is not a substitute for reading the full label or consulting a doctor."
)
