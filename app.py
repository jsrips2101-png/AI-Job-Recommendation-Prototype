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
    page_title="CareerAI - Smart Job Finder",
    page_icon="💜",
    layout="wide"
)


# =========================================================
# SIMPLE, SAFE STYLING
# No HTML cards or HTML text
# =========================================================

st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #f7f5fc;
    }

    /* Main text */
    .stApp,
    .stApp p,
    .stApp label,
    .stApp span {
        color: #222222;
    }

    /* Headings */
    h1, h2, h3, h4, h5, h6 {
        color: #17121f !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
    }

    section[data-testid="stSidebar"] * {
        color: #222222 !important;
    }

    /* Buttons */
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        font-weight: 600;
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        background-color: #ffffff;
        border-radius: 12px;
    }

    /* Input boxes */
    input {
        color: #222222 !important;
    }

    /* Success / warning / error */
    .stAlert p {
        color: #222222 !important;
    }

    /* Links */
    a {
        color: #5b21b6 !important;
        font-weight: 600;
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
# HEADER
# =========================================================

st.title("💜 CareerAI")

st.subheader("AI-Powered Job Recommendation System")

st.write(
    "Upload your resume and discover suitable technical roles "
    "and relevant job opportunities."
)

st.divider()


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("📄 Resume")

    uploaded_file = st.file_uploader(
        "Upload your resume",
        type=["pdf", "docx", "txt"],
        help="Supported formats: PDF, DOCX and TXT"
    )

    st.write("")

    location = st.text_input(
        "📍 Preferred Location",
        value="India",
        placeholder="Example: Chennai"
    )

    st.divider()

    st.subheader("How it works")

    st.write("📄 **1. Resume Analysis**")
    st.caption(
        "AI reads your resume and understands your technical profile."
    )

    st.write("🧠 **2. Smart Matching**")
    st.caption(
        "Your skills are matched with suitable technical job roles."
    )

    st.write("🎯 **3. Job Recommendations**")
    st.caption(
        "Relevant job opportunities are collected for you."
    )


# =========================================================
# RESUME TEXT EXTRACTION
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

            text = "\n".join(
                paragraph.text
                for paragraph in document.paragraphs
            )

            return text

        elif file_name.endswith(".txt"):

            return uploaded_file.read().decode(
                "utf-8",
                errors="ignore"
            )

        return ""

    except Exception as e:

        st.error(f"Could not read the resume: {e}")

        return ""


# =========================================================
# CLEAN RESUME
# =========================================================

def clean_resume(text):

    text = text.replace("\x00", " ")

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


# =========================================================
# AI RESUME ANALYSIS
# =========================================================

def analyze_resume(resume_text):

    if not GROQ_API_KEY:
        return None, "Groq API key is missing."

    try:

        client = Groq(
            api_key=GROQ_API_KEY
        )

        prompt = f"""
You are an AI career assistant.

Analyze the following resume and identify:

1. The most suitable technical job role.
2. The technical skills present in the resume.

Return ONLY valid JSON in this format:

{{
    "role": "Data Analyst",
    "skills": ["Python", "SQL", "Excel", "Power BI"]
}}

Do not add explanations outside the JSON.

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

        # Remove markdown code fences if the model returns them
        result = result.replace("```json", "")
        result = result.replace("```", "")
        result = result.strip()

        # Find JSON object if extra text is returned
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


# =========================================================
# JOB SEARCH
# =========================================================

def search_jobs(role, skills, location):

    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        return [], "Adzuna API credentials are missing."

    try:

        url = (
            "https://api.adzuna.com/v1/api/jobs/in/search/1"
        )

        skill_text = " ".join(
            str(skill)
            for skill in skills[:3]
        )

        search_term = f"{role} {skill_text}".strip()

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

        jobs = data.get(
            "results",
            []
        )

        return jobs, None

    except Exception as e:

        return [], str(e)


# =========================================================
# MAIN APPLICATION
# =========================================================

if uploaded_file:

    st.divider()

    st.header("📊 Resume Analysis")

    # -----------------------------------------------------
    # Read resume
    # -----------------------------------------------------

    with st.spinner("Reading your resume..."):

        resume_text = extract_resume_text(
            uploaded_file
        )

    if not resume_text.strip():

        st.error(
            "I could not find readable text in this resume."
        )

        st.info(
            "If this is a scanned PDF, upload a text-based PDF, "
            "DOCX, or TXT file."
        )

        st.stop()

    cleaned_text = clean_resume(
        resume_text
    )

    # -----------------------------------------------------
    # AI Analysis
    # -----------------------------------------------------

    with st.spinner(
        "AI is analyzing your technical profile..."
    ):

        analysis, error = analyze_resume(
            cleaned_text
        )

    if error:

        st.error(
            f"Resume analysis failed: {error}"
        )

        st.stop()

    role = analysis["role"]
    skills = analysis["skills"]

    # -----------------------------------------------------
    # PROFILE SUMMARY
    # -----------------------------------------------------

    st.success(
        "Resume successfully analyzed."
    )

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Recommended Role",
            role
        )

    with col2:

        st.metric(
            "Skills Detected",
            len(skills)
        )

    st.subheader("🎯 Recommended Technical Role")

    st.write(
        f"Based on your resume, the most suitable role is **{role}**."
    )

    # -----------------------------------------------------
    # SKILLS
    # -----------------------------------------------------

    st.subheader("🛠️ Skills Found in Your Resume")

    if skills:

        skill_text = " • ".join(
            str(skill)
            for skill in skills
        )

        st.info(skill_text)

    else:

        st.warning(
            "No specific technical skills were detected."
        )

    # -----------------------------------------------------
    # JOB SEARCH
    # -----------------------------------------------------

    st.divider()

    st.header("💼 Recommended Jobs")

    st.write(
        f"Searching for **{role}** opportunities in **{location}**..."
    )

    with st.spinner(
        "Finding relevant job opportunities..."
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
            "No matching jobs were found right now. "
            "Try another location."
        )

    else:

        st.success(
            f"Found {len(jobs)} job opportunities."
        )

        for index, job in enumerate(jobs, start=1):

            title = job.get(
                "title",
                "Job opportunity"
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

                st.write(
                    f"**Company:** {company}"
                )

                st.write(
                    f"**Location:** {job_location}"
                )

                st.write("**Job Description:**")

                st.write(description)

                if apply_url:

                    st.link_button(
                        "Apply / View Job",
                        apply_url
                    )


# =========================================================
# EMPTY STATE
# =========================================================

else:

    st.header("🚀 Start Your Job Search")

    st.write(
        "Upload your resume from the left sidebar to begin."
    )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:

        st.subheader("📄 Resume Analysis")

        st.write(
            "AI reads your resume and understands "
            "your technical profile."
        )

    with col2:

        st.subheader("🧠 Smart Matching")

        st.write(
            "Your skills are matched with suitable "
            "technical job roles."
        )

    with col3:

        st.subheader("🎯 Job Recommendations")

        st.write(
            "Find relevant job opportunities based "
            "on your profile."
        )

    st.divider()

    st.info(
        "Supported formats: PDF, DOCX and TXT"
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "CareerAI • AI-Powered Job Recommendation System"
)
