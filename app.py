import streamlit as st
import requests
import json
import re
import os

from groq import Groq
from pypdf import PdfReader
from docx import Document


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="NEXORA | AI Career Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# DESIGN
# =========================================================

st.markdown("""
<style>

    /* ================================
       MAIN APP
       ================================ */

    .stApp {
        background-color: #0b1020;
        color: #f5f7ff;
    }

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }


    /* ================================
       ALL TEXT VISIBILITY
       ================================ */

    .stApp p,
    .stApp span,
    .stApp label,
    .stApp li {
        color: #e8ecff !important;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }


    /* ================================
       SIDEBAR
       ================================ */

    section[data-testid="stSidebar"] {
        background-color: #11182d;
        border-right: 1px solid #293352;
    }

    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4 {
        color: #ffffff !important;
    }


    /* ================================
       FILE UPLOADER
       ================================ */

    [data-testid="stFileUploader"] {
        background-color: #18213b;
        border: 1px solid #354266;
        border-radius: 16px;
        padding: 10px;
    }

    [data-testid="stFileUploader"] * {
        color: #ffffff !important;
    }


    /* ================================
       INPUT
       ================================ */

    .stTextInput input {
        background-color: #18213b !important;
        color: #ffffff !important;
        border: 1px solid #354266 !important;
        border-radius: 10px !important;
    }

    .stTextInput input::placeholder {
        color: #aeb8d4 !important;
    }


    /* ================================
       BUTTONS
       ================================ */

    .stButton > button {
        background-color: #7c3aed;
        color: #ffffff !important;
        border: none;
        border-radius: 10px;
        font-weight: 700;
        min-height: 45px;
    }

    .stButton > button:hover {
        background-color: #8b5cf6;
        color: #ffffff !important;
    }


    /* ================================
       METRICS
       ================================ */

    [data-testid="stMetric"] {
        background-color: #151e36;
        border: 1px solid #303c60;
        border-radius: 16px;
        padding: 18px;
    }

    [data-testid="stMetricLabel"] {
        color: #aeb8d4 !important;
    }

    [data-testid="stMetricValue"] {
        color: #ffffff !important;
    }


    /* ================================
       EXPANDERS
       ================================ */

    [data-testid="stExpander"] {
        background-color: #151e36;
        border: 1px solid #303c60;
        border-radius: 14px;
    }

    [data-testid="stExpander"] * {
        color: #ffffff !important;
    }


    /* ================================
       ALERTS
       ================================ */

    .stAlert p {
        color: #ffffff !important;
    }


    /* ================================
       LINKS
       ================================ */

    a {
        color: #a78bfa !important;
    }


    /* ================================
       DIVIDER
       ================================ */

    hr {
        border-color: #293352 !important;
    }

</style>
""", unsafe_allow_html=True)


# =========================================================
# API KEYS
# =========================================================

GROQ_API_KEY = st.secrets.get(
    "GROQ_API_KEY",
    os.getenv("GROQ_API_KEY")
)

ADZUNA_APP_ID = st.secrets.get(
    "ADZUNA_APP_ID",
    os.getenv("ADZUNA_APP_ID")
)

ADZUNA_APP_KEY = st.secrets.get(
    "ADZUNA_APP_KEY",
    os.getenv("ADZUNA_APP_KEY")
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title("🧠 NEXORA")

    st.caption(
        "AI Career Intelligence Platform"
    )

    st.divider()

    st.subheader("📄 Upload Resume")

    uploaded_file = st.file_uploader(
        "Choose your resume",
        type=["pdf", "docx", "txt"],
        help="PDF, DOCX and TXT files are supported."
    )

    st.write("")

    st.subheader("📍 Job Location")

    location = st.text_input(
        "Preferred location",
        value="India",
        placeholder="Example: Chennai"
    )

    st.divider()

    st.subheader("⚡ Platform Flow")

    st.write("01  📄 Resume Intelligence")
    st.caption(
        "Understand your education, experience and technical profile."
    )

    st.write("02  🧠 Career Matching")
    st.caption(
        "Identify a suitable technical role from your profile."
    )

    st.write("03  💼 Opportunity Discovery")
    st.caption(
        "Find relevant job opportunities based on your role."
    )

    st.divider()

    st.caption(
        "NEXORA Career Intelligence • 2026"
    )


# =========================================================
# FUNCTIONS
# =========================================================

def extract_resume_text(uploaded_file):

    file_name = uploaded_file.name.lower()

    try:

        if file_name.endswith(".pdf"):

            reader = PdfReader(uploaded_file)

            text = ""

            for page in reader.pages:

                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

            return text

        elif file_name.endswith(".docx"):

            document = Document(uploaded_file)

            return "\n".join(
                paragraph.text
                for paragraph in document.paragraphs
            )

        elif file_name.endswith(".txt"):

            return uploaded_file.read().decode(
                "utf-8",
                errors="ignore"
            )

        return ""

    except Exception as e:

        st.error(
            f"Unable to read the resume: {e}"
        )

        return ""


def clean_resume(text):

    text = text.replace(
        "\x00",
        " "
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    text = re.sub(
        r"[^\w\s\+\#\.\-/]",
        " ",
        text
    )

    return text.strip()


def analyze_resume(resume_text):

    if not GROQ_API_KEY:

        return None, "Groq API key is missing."

    try:

        client = Groq(
            api_key=GROQ_API_KEY
        )

        prompt = f"""
You are an AI career assistant.

Analyze this resume.

Identify:

1. The most suitable technical job role.
2. Technical skills found in the resume.

Return ONLY valid JSON.

Required format:

{{
    "role": "Data Analyst",
    "skills": [
        "Python",
        "SQL",
        "Excel"
    ]
}}

Resume:

{resume_text[:12000]}
"""

        response = client.chat.completions.create(

            model="openai/gpt-oss-20b",

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.2
        )

        result = response.choices[0].message.content.strip()

        result = result.replace(
            "```json",
            ""
        )

        result = result.replace(
            "```",
            ""
        )

        match = re.search(
            r"\{.*\}",
            result,
            re.DOTALL
        )

        if match:
            result = match.group(0)

        data = json.loads(result)

        role = data.get(
            "role",
            "Technical Professional"
        )

        skills = data.get(
            "skills",
            []
        )

        if not isinstance(skills, list):
            skills = []

        return {
            "role": role,
            "skills": skills
        }, None

    except Exception as e:

        return None, str(e)


def search_jobs(role, skills, location):

    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:

        return [], "Adzuna credentials are missing."

    try:

        url = (
            "https://api.adzuna.com/v1/api/jobs/in/search/1"
        )

        skill_text = " ".join(
            str(skill)
            for skill in skills[:3]
        )

        search_term = (
            f"{role} {skill_text}"
        ).strip()

        params = {

            "app_id": ADZUNA_APP_ID,

            "app_key": ADZUNA_APP_KEY,

            "what": search_term,

            "where": location,

            "results_per_page": 10,

            "content-type": "application/json"
        }

        response = requests.get(
            url,
            params=params,
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

        return data.get(
            "results",
            []
        ), None

    except Exception as e:

        return [], str(e)


# =========================================================
# MAIN HEADER
# =========================================================

st.title("🧠 NEXORA")

st.subheader(
    "AI Career Intelligence for Your Next Opportunity"
)

st.write(
    "Turn your resume into a career profile, "
    "discover your strongest technical role, "
    "and explore relevant job opportunities."
)

st.divider()


# =========================================================
# EMPTY STATE
# =========================================================

if not uploaded_file:

    st.header("🚀 Begin Your Career Analysis")

    st.write(
        "Your resume is the starting point. "
        "Upload it from the sidebar and let NEXORA analyze your profile."
    )

    st.write("")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "STEP 01",
            "Resume Intelligence"
        )

        st.write(
            "Extract useful information from your resume "
            "and understand your technical background."
        )

    with col2:

        st.metric(
            "STEP 02",
            "Career Matching"
        )

        st.write(
            "Identify a suitable technical role based "
            "on your skills and profile."
        )

    with col3:

        st.metric(
            "STEP 03",
            "Job Discovery"
        )

        st.write(
            "Search for relevant job opportunities "
            "in your preferred location."
        )

    st.divider()

    st.header("✨ Why NEXORA?")

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("🎯 Personalized")

        st.write(
            "Recommendations are generated from "
            "your own resume instead of a generic job list."
        )

    with col2:

        st.subheader("⚡ Simple")

        st.write(
            "Upload once, analyze your profile, "
            "and explore suitable opportunities."
        )

    st.stop()


# =========================================================
# RESUME PROCESSING
# =========================================================

st.header("📄 Resume Intelligence")

st.write(
    f"Selected resume: **{uploaded_file.name}**"
)

with st.spinner(
    "Reading your resume..."
):

    resume_text = extract_resume_text(
        uploaded_file
    )


if not resume_text.strip():

    st.error(
        "No readable text was found in the uploaded resume."
    )

    st.info(
        "Try a text-based PDF, DOCX or TXT file."
    )

    st.stop()


cleaned_text = clean_resume(
    resume_text
)


# =========================================================
# AI ANALYSIS
# =========================================================

with st.spinner(
    "🧠 NEXORA is analyzing your technical profile..."
):

    analysis, error = analyze_resume(
        cleaned_text
    )


if error:

    st.error(
        f"AI analysis failed: {error}"
    )

    st.stop()


role = analysis["role"]

skills = analysis["skills"]


st.success(
    "Resume analysis completed successfully."
)


# =========================================================
# PROFILE OVERVIEW
# =========================================================

st.divider()

st.header("🎯 Your Career Profile")

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Recommended Role",
        role
    )

with col2:

    st.metric(
        "Skills Identified",
        len(skills)
    )

with col3:

    st.metric(
        "Search Location",
        location
    )


st.write("")

st.subheader("💡 AI Career Insight")

st.write(
    f"Based on your resume, **{role}** appears to be "
    "one of the most suitable technical career directions "
    "for your current profile."
)


# =========================================================
# SKILLS
# =========================================================

st.divider()

st.header("🛠️ Technical Skill Profile")

if skills:

    st.write(
        "The following technical skills were identified "
        "from your resume:"
    )

    skill_columns = st.columns(
        min(len(skills), 4)
    )

    for index, skill in enumerate(skills):

        with skill_columns[index % len(skill_columns)]:

            st.info(
                f"✓ {skill}"
            )

else:

    st.warning(
        "No specific technical skills were detected."
    )


# =========================================================
# JOB RECOMMENDATIONS
# =========================================================

st.divider()

st.header("💼 Opportunity Discovery")

st.write(
    f"Finding **{role}** opportunities around **{location}**..."
)


with st.spinner(
    "🔎 Searching for relevant jobs..."
):

    jobs, job_error = search_jobs(
        role,
        skills,
        location
    )


if job_error:

    st.error(
        f"Job search failed: {job_error}"
    )

elif not jobs:

    st.warning(
        "No matching jobs were found right now."
    )

    st.write(
        "Try changing the preferred location "
        "from the sidebar."
    )

else:

    st.success(
        f"{len(jobs)} job opportunities found."
    )

    for index, job in enumerate(
        jobs,
        start=1
    ):

        title = job.get(
            "title",
            "Job Opportunity"
        )

        company_data = job.get(
            "company",
            {}
        )

        company = company_data.get(
            "display_name",
            "Company not specified"
        )

        location_data = job.get(
            "location",
            {}
        )

        job_location = location_data.get(
            "display_name",
            location
        )

        description = job.get(
            "description",
            "No description available."
        )

        apply_url = job.get(
            "redirect_url",
            ""
        )

        with st.expander(
            f"💼 {index}. {title}"
        ):

            col1, col2 = st.columns(2)

            with col1:

                st.write(
                    f"**Company**  \n{company}"
                )

            with col2:

                st.write(
                    f"**Location**  \n{job_location}"
                )

            st.divider()

            st.write(
                "**Job Description**"
            )

            st.write(
                description
            )

            if apply_url:

                st.link_button(
                    "🔗 View / Apply for Job",
                    apply_url
                )


# =========================================================
# FINAL SECTION
# =========================================================

st.divider()

st.header("🌟 Your Next Step")

st.write(
    "Use the recommended role and detected skills "
    "as a starting point for your job search."
)

st.info(
    "Tip: Keep your resume updated with relevant "
    "projects, technical skills and certifications."
)

st.divider()

st.caption(
    "NEXORA • AI Career Intelligence Platform • 2026"
)
