import streamlit as st
import PyPDF2
import docx
import re
from rapidfuzz import fuzz

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Enterprise AI Resume Analyzer",
    layout="wide"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>

.main-title {
    font-size: 34px;
    font-weight: bold;
    text-align: center;
    margin-bottom: 30px;
}

/* Blue Large Button */
div.stButton > button {
    background-color: #007BFF;
    color: white;
    font-size: 20px;
    font-weight: bold;
    padding: 14px 30px;
    border-radius: 12px;
    border: none;
    width: 100%;
    transition: 0.3s;
}

div.stButton > button:hover {
    background-color: #0056b3;
    color: white;
}

/* Score Card */
.score-card {
    border: 3px solid;
    border-radius: 15px;
    padding: 25px;
    text-align: center;
    font-size: 28px;
    font-weight: bold;
    margin-top: 25px;
    background-color: #f9f9f9;
}

/* Result Cards */
.card {
    border-radius: 12px;
    padding: 20px;
    margin-top: 20px;
    background-color: #ffffff;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.08);
}

.match-card {
    border-left: 6px solid green;
}

.missing-card {
    border-left: 6px solid red;
}

.suggestion-card {
    border-left: 6px solid #007BFF;
}

.footer {
    text-align:center;
    margin-top:50px;
    color:gray;
    font-size:13px;
}

</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📊 Enterprise AI Resume Analyzer</div>', unsafe_allow_html=True)

# ---------------- TEXT NORMALIZATION ----------------
def normalize(text):
    text = text.lower()
    text = re.sub(r'\n', ' ', text)
    text = re.sub(r'[^a-zA-Z0-9+#. ]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# ---------------- FILE UPLOAD ----------------
col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader(
        "Upload Resume (PDF or Word)",
        type=["pdf", "docx"]
    )

resume_text = ""

if uploaded_file is not None:
    if uploaded_file.type == "application/pdf":
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            if page.extract_text():
                resume_text += page.extract_text()

    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(uploaded_file)
        for para in doc.paragraphs:
            resume_text += para.text + " "

    resume_text = normalize(resume_text)
    st.success("Resume uploaded successfully ✅")

with col2:
    jd_input = st.text_area(
        "Paste Job Description Skills (comma separated)",
        height=150
    )

# ---------------- ANALYZE BUTTON ----------------
if st.button("Analyze Resume Match"):

    if resume_text and jd_input:

        jd_skills = [normalize(skill.strip()) for skill in jd_input.split(",")]
        jd_skills = list(filter(None, jd_skills))

        matched_skills = []
        unmatched_skills = []

        for skill in jd_skills:
            if skill in resume_text:
                matched_skills.append(skill)
                continue

            found = False
            for chunk in resume_text.split("."):
                if fuzz.partial_ratio(skill, chunk) > 85:
                    matched_skills.append(skill)
                    found = True
                    break

            if not found:
                unmatched_skills.append(skill)

        match_percentage = (len(matched_skills) / len(jd_skills)) * 100 if jd_skills else 0

        # ---------------- COLOR LOGIC ----------------
        if match_percentage > 60:
            color = "green"
            performance = "Strong Match"
        elif 40 <= match_percentage <= 60:
            color = "orange"
            performance = "Moderate Match"
        else:
            color = "red"
            performance = "Low Match"

        # ---------------- SCORE CARD ----------------
        st.markdown(f"""
        <div class="score-card" style="color:{color}; border-color:{color}">
            Match Score: {match_percentage:.2f}%<br>
            {performance}
        </div>
        """, unsafe_allow_html=True)

        # ---------------- SKILL CARDS ----------------
        colA, colB = st.columns(2)

        with colA:
            st.markdown("""
            <div class="card match-card">
            <h3>✅ Matched Skills</h3>
            """, unsafe_allow_html=True)

            if matched_skills:
                for skill in matched_skills:
                    st.write(f"✔ {skill}")
            else:
                st.write("No skills matched")

            st.markdown("</div>", unsafe_allow_html=True)

        with colB:
            st.markdown("""
            <div class="card missing-card">
            <h3>❌ Missing Skills</h3>
            """, unsafe_allow_html=True)

            if unmatched_skills:
                for skill in unmatched_skills:
                    st.write(f"✘ {skill}")
            else:
                st.write("No missing skills")

            st.markdown("</div>", unsafe_allow_html=True)

        # ---------------- SUGGESTIONS SECTION ----------------
        st.markdown("""
        <div class="card suggestion-card">
        <h3>💡 Resume Improvement Suggestions</h3>
        """, unsafe_allow_html=True)

        if unmatched_skills:
            st.write("🔹 Add the missing skills listed above if you have experience.")
            st.write("🔹 Include measurable achievements related to these skills.")
            st.write("🔹 Add a dedicated 'Technical Skills' section if not present.")
            st.write("🔹 Use exact keywords from the job description.")
        else:
            st.write("🔹 Your resume aligns well with the job description.")
            st.write("🔹 Ensure achievements are quantified (numbers, impact).")
            st.write("🔹 Keep formatting ATS-friendly (simple layout, no tables).")

        if match_percentage < 50:
            st.write("🔹 Consider upskilling in the missing technologies.")
            st.write("🔹 Customize resume summary according to job role.")

        st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.warning("Please upload resume and enter job description skills.")

# ---------------- FOOTER ----------------
st.markdown('<div class="footer">Enterprise Resume Matching System | AI Powered</div>', unsafe_allow_html=True)