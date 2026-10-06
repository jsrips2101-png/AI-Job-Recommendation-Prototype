import streamlit as st
import requests
import json
import re
import os
import html

from groq import Groq
from pypdf import PdfReader
from docx import Document


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="CareerAI | Smart Job Discovery",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# CUSTOM DESIGN
# =========================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 10% 10%, rgba(99,102,241,0.08), transparent 25%),
        radial-gradient(circle at 90% 20%, rgba(14,165,233,0.08), transparent 25%),
        #f8fafc;
    color: #0f172a;
}

.block-container {
    max-width: 1180px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}


/* ---------------------------------------------------------
   HIDE DEFAULT STREAMLIT ELEMENTS
--------------------------------------------------------- */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    background: transparent !important;
}


/* ---------------------------------------------------------
   TOP NAVIGATION
--------------------------------------------------------- */

.navbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 4px 30px 4px;
}

.brand {
    display: flex;
    align-items: center;
    gap: 10px;
}

.brand-icon {
    width: 42px;
    height: 42px;
    border-radius: 13px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white !important;
    font-size: 21px;
    font-weight: 800;
    box-shadow: 0 8px 20px rgba(99,102,241,0.25);
}

.brand-name {
    font-size: 21px;
    font-weight: 800;
    color: #0f172a !important;
}

.brand-name span {
    color: #6366f1 !important;
}


/* ---------------------------------------------------------
   HERO
--------------------------------------------------------- */

.hero {
    position: relative;
    overflow: hidden;
    border-radius: 30px;
    padding: 60px 55px;
    margin-bottom: 28px;
    background:
        radial-gradient(circle at 85% 20%, rgba(255,255,255,0.20), transparent 20%),
        radial-gradient(circle at 10% 100%, rgba(255,255,255,0.12), transparent 25%),
        linear-gradient(135deg, #111827, #312e81 55%, #4f46e5);
    box-shadow: 0 20px 50px rgba(49,46,129,0.20);
}

.hero-kicker {
    color: #c7d2fe !important;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 16px;
}

.hero h1 {
    color: white !important;
    font-size: 46px;
    line-height: 1.1;
    max-width: 720px;
    margin: 0 0 18px 0;
    font-weight: 800;
}

.hero p {
    color: #e0e7ff !important;
    font-size: 17px;
    line-height: 1.7;
    max-width: 650px;
    margin-bottom: 0;
}

.hero-orb {
    position: absolute;
    right: 65px;
    top: 55px;
    width: 150px;
    height: 150px;
    border-radius: 50%;
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.12);
}


/* ---------------------------------------------------------
   SECTION TITLE
--------------------------------------------------------- */

.section-title {
    color: #0f172a !important;
    font-size: 25px;
    font-weight: 800;
    margin: 35px 0 8px 0;
}

.section-subtitle {
    color: #64748b !important;
    font-size: 14px;
    margin-bottom: 22px;
}


/* ---------------------------------------------------------
   UPLOAD CARD
--------------------------------------------------------- */

.upload-card {
    background: rgba(255,255,255,0.88);
    border: 1px solid #e2e8f0;
    border-radius: 24px;
    padding: 28px;
    box-shadow: 0 10px 35px rgba(15,23,42,0.06);
}

.upload-title {
    color: #0f172a !important;
    font-size: 19px;
    font-weight: 700;
    margin-bottom: 5px;
}

.upload-text {
    color: #64748b !important;
    font-size: 13px;
    margin-bottom: 18px;
}


/* ---------------------------------------------------------
   INPUTS
--------------------------------------------------------- */

div[data-baseweb="input"] {
    border-radius: 12px !important;
}

div[data-baseweb="input"] > div {
    border-radius: 12px !important;
    border-color: #dbe2ea !important;
    background: white !important;
}

div[data-baseweb="input"] input {
    color: #0f172a !important;
}

label {
    color: #334155 !important;
    font-weight: 600 !important;
}


/* ---------------------------------------------------------
   BUTTON
--------------------------------------------------------- */

.stButton > button {
    width: 100%;
    border-radius: 13px;
    min-height: 50px;
    border: none;
    background: linear-gradient(135deg, #6366f1, #7c3aed);
    color: white !important;
    font-size: 15px;
    font-weight: 700;
    box-shadow: 0 10px 25px rgba(99,102,241,0.22);
    transition: all 0.2s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 14px 30px rgba(99,102,241,0.30);
}


/* ---------------------------------------------------------
   PROFILE CARD
--------------------------------------------------------- */

.profile-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 24px;
    padding: 28px;
    box-shadow: 0 10px 35px rgba(15,23,42,0.06);
    margin-top: 20px;
}

.profile-label {
    color: #64748b !important;
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.profile-role {
    color: #0f172a !important;
    font-size: 30px;
    font-weight: 800;
    margin: 5px 0 15px 0;
}

.skill-chip {
    display: inline-block;
    background: #eef2ff;
    color: #4338ca !important;
    border: 1px solid #c7d2fe;
    padding: 7px 13px;
    border-radius: 999px;
    margin: 4px 5px 4px 0;
    font-size: 12px;
    font-weight: 600;
}


/* ---------------------------------------------------------
   JOB CARD
--------------------------------------------------------- */

.job-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 22px;
    padding: 24px;
    margin: 15px 0;
    box-shadow: 0 8px 28px rgba(15,23,42,0.05);
}

.job-number {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 30px;
    height: 30px;
    border-radius: 9px;
    background: #eef2ff;
    color: #4f46e5 !important;
    font-size: 12px;
    font-weight: 800;
    margin-right: 9px;
}

.job-title {
    color: #0f172a !important;
    font-size: 20px;
    font-weight: 800;
}

.job-company {
    color: #334155 !important;
    font-size: 14px;
    font-weight: 600;
    margin-top: 10px;
}

.job-location {
    color: #64748b !important;
    font-size: 13px;
    margin-top: 6px;
}

.job-description {
    color: #64748b !important;
    font-size: 13px;
    line-height: 1.7;
    margin-top: 15px;
}

.match {
    display: inline-block;
    background: #ecfdf5;
    color: #047857 !important;
    border: 1px solid #a7f3d0;
    padding: 6px 11px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 700;
    margin-top: 12px;
}


/* ---------------------------------------------------------
   INFO CARDS
--------------------------------------------------------- */

.info-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 20px;
    padding: 22px;
    height: 100%;
    box-shadow: 0 8px 25px rgba(15,23,42,0.04);
}

.info-icon {
    font-size: 25px;
    margin-bottom: 12px;
}

.info-title {
    color: #0f172a !important;
    font-weight: 700;
    font-size: 15px;
}

.info-text {
    color: #64748b !important;
    font-size: 12px;
    line-height: 1.6;
}


/* ---------------------------------------------------------
   FOOTER
--------------------------------------------------------- */

.footer {
    text-align: center;
    padding: 35px 0 10px 0;
    color: #94a3b8 !important;
    font-size: 12px;
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
# API CHECK
# =========================================================

if not GROQ_API_KEY:
    st.error("Groq API key is missing.")
    st.info("Add GROQ_API_KEY in your Streamlit app Secrets.")
    st.stop()

if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
    st.error("Adzuna API credentials are missing.")
    st.info("Add ADZUNA_APP_ID and ADZUNA_APP_KEY in your Streamlit app Secrets.")
    st.stop()


client = Groq(api_key=GROQ_API_KEY)


# =========================================================
# NAVBAR
# =========================================================

st.markdown("""
<div class="navbar">

    <div class="brand">
        <div class="brand-icon">✦</div>
        <div class="brand-name">Career<span>AI</span></div>
    </div>

</div>
""", unsafe_allow_html=True)


# =========================================================
# HERO
# =========================================================

st.markdown("""
<div class="hero">

    <div class="hero-orb"></div>

    <div class="hero-kicker">
        AI Career Intelligence
    </div>

    <h1>
        Find work that<br>
        fits your skills.
    </h1>

    <p>
        Upload your resume and let AI understand your
        professional profile, identify your strongest
        technical skills, and discover relevant job
        opportunities.
    </p>

</div>
""", unsafe_allow_html=True)


# =========================================================
# INPUT AREA
# =========================================================

st.markdown(
    '<div class="section-title">Build your career profile</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-subtitle">Upload your resume and tell us where you want to work.</div>',
    unsafe_allow_html=True
)


col1, col2 = st.columns([1.45, 1], gap="large")


with col1:

    st.markdown("""
    <div class="upload-card">

        <div class="upload-title">
            📄 Your Resume
        </div>

        <div class="upload-text">
            PDF, DOCX or TXT files are supported.
        </div>

    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload resume",
        type=["pdf", "docx", "txt"],
        label_visibility="collapsed"
    )


with col2:

    st.markdown("""
    <div class="upload-card">

        <div class="upload-title">
            📍 Preferred Location
        </div>

        <div class="upload-text">
            Enter a city where you want to find jobs.
        </div>

    </div>
    """, unsafe_allow_html=True)

    location = st.text_input(
        "Location",
        placeholder="Example: Chennai",
        label_visibility="collapsed"
    )


st.write("")


analyze_button = st.button(
    "✦  Analyze Resume & Discover Jobs",
    use_container_width=True
)


# =========================================================
# RESUME READER
# =========================================================

def read_resume(file):

    filename = file.name.lower()

    if filename.endswith(".pdf"):

        reader = PdfReader(file)

        text = ""

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        return text.strip()


    elif filename.endswith(".docx"):

        doc = Document(file)

        text = "\n".join(
            paragraph.text
            for paragraph in doc.paragraphs
            if paragraph.text.strip()
        )

        return text.strip()


    elif filename.endswith(".txt"):

        return file.read().decode(
            "utf-8",
            errors="ignore"
        )


    raise ValueError("Unsupported file format.")


# =========================================================
# CLEAN RESUME
# =========================================================

def clean_resume(text):

    text = text.lower()

    text = re.sub(
        r'\s+',
        ' ',
        text
    )

    text = re.sub(
        r'[^a-zA-Z0-9+.#\s]',
        ' ',
        text
    )

    return text.strip()


# =========================================================
# AI ANALYSIS
# =========================================================

def analyze_resume(resume_text):

    prompt = f"""
You are an AI resume analysis system.

Analyze the resume and identify the most suitable
technical job role and important technical skills.

Rules:

- Return ONLY valid JSON.
- Do not use markdown.
- Do not explain your answer.
- Do not invent information.
- Choose ONE primary technical role.
- Maximum 3 words for the role.
- Maximum 6 technical skills.
- Only select skills actually supported by the resume.

Return exactly:

{{
    "role": "Data Scientist",
    "skills": [
        "Python",
        "SQL",
        "Machine Learning"
    ]
}}

Resume:

{resume_text}
"""

    response = client.chat.completions.create(

        model="openai/gpt-oss-20b",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0
    )

    result = response.choices[0].message.content.strip()

    result = re.sub(
        r"```json|```",
        "",
        result
    ).strip()

    return json.loads(result)


# =========================================================
# JOB SEARCH
# =========================================================

def search_jobs(role, skills, location):

    url = (
        "https://api.adzuna.com/"
        "v1/api/jobs/in/search/1"
    )

    params = {

        "app_id": ADZUNA_APP_ID,

        "app_key": ADZUNA_APP_KEY,

        "what": role,

        "where": location,

        "results_per_page": 10

    }

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    if response.status_code != 200:

        raise Exception(
            f"Adzuna API error: {response.status_code}"
        )

    data = response.json()

    return data.get(
        "results",
        []
    )


# =========================================================
# JOB CARD
# =========================================================

def display_job(number, job):

    title = html.escape(
        job.get(
            "title",
            "Job title not available"
        )
    )

    company = html.escape(
        job.get(
            "company",
            {}
        ).get(
            "display_name",
            "Company not specified"
        )
    )

    job_location = html.escape(
        job.get(
            "location",
            {}
        ).get(
            "display_name",
            "Location not specified"
        )
    )

    description = job.get(
        "description",
        ""
    )

    if len(description) > 280:
        description = description[:280] + "..."

    description = html.escape(description)

    st.markdown(
        f"""
        <div class="job-card">

            <div>
                <span class="job-number">{number}</span>
                <span class="job-title">{title}</span>
            </div>

            <div class="job-company">
                🏢 {company}
            </div>

            <div class="job-location">
                📍 {job_location}
            </div>

            <div class="match">
                ✦ Relevant opportunity
            </div>

            <div class="job-description">
                {description}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    apply_url = job.get(
        "redirect_url",
        "#"
    )

    st.link_button(
        "View & Apply →",
        apply_url,
        use_container_width=True
    )


# =========================================================
# PROCESS
# =========================================================

if analyze_button:

    if not uploaded_file:

        st.warning(
            "Please upload your resume first."
        )

        st.stop()


    if not location.strip():

        st.warning(
            "Please enter your preferred location."
        )

        st.stop()


    try:

        # -------------------------------------------------
        # READ RESUME
        # -------------------------------------------------

        with st.spinner(
            "Reading your resume..."
        ):

            resume_text = read_resume(
                uploaded_file
            )


        if not resume_text:

            st.error(
                "No readable text was found in the resume."
            )

            st.stop()


        # -------------------------------------------------
        # AI ANALYSIS
        # -------------------------------------------------

        with st.spinner(
            "AI is understanding your career profile..."
        ):

            cleaned_text = clean_resume(
                resume_text
            )

            analysis = analyze_resume(
                cleaned_text
            )


        role = analysis.get(
            "role",
            "Technical Professional"
        )

        skills = analysis.get(
            "skills",
            []
        )


        # -------------------------------------------------
        # PROFILE RESULT
        # -------------------------------------------------

        st.markdown(
            '<div class="section-title">Your AI Career Profile</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-subtitle">Based on the information found in your resume.</div>',
            unsafe_allow_html=True
        )


        skill_html = ""

        for skill in skills:

            skill_html += (
                f'<span class="skill-chip">'
                f'{html.escape(str(skill))}'
                f'</span>'
            )


        st.markdown(
            f"""
            <div class="profile-card">

                <div class="profile-label">
                    Recommended career direction
                </div>

                <div class="profile-role">
                    {html.escape(str(role))}
                </div>

                <div class="profile-label">
                    Skills detected
                </div>

                <div style="margin-top:10px;">
                    {skill_html}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


        # -------------------------------------------------
        # JOB SEARCH
        # -------------------------------------------------

        with st.spinner(
            f"Searching opportunities in {location}..."
        ):

            jobs = search_jobs(
                role,
                skills,
                location
            )


        # -------------------------------------------------
        # JOB RESULTS
        # -------------------------------------------------

        st.markdown(
            '<div class="section-title">Opportunities for you</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="section-subtitle">
                Showing jobs related to
                <b>{html.escape(str(role))}</b>
                in
                <b>{html.escape(str(location))}</b>.
            </div>
            """,
            unsafe_allow_html=True
        )


        if not jobs:

            st.warning(
                f"No matching jobs were found for {location}."
            )

        else:

            st.success(
                f"Found {len(jobs)} opportunities."
            )

            for index, job in enumerate(
                jobs,
                start=1
            ):

                display_job(
                    index,
                    job
                )


    except json.JSONDecodeError:

        st.error(
            "The AI returned an unexpected response. Please try again."
        )


    except Exception as e:

        st.error(
            "Something went wrong while processing your request."
        )

        st.exception(e)


# =========================================================
# HOW IT WORKS
# =========================================================

if not analyze_button:

    st.markdown(
        '<div class="section-title">How CareerAI works</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">Three simple steps from resume to opportunity.</div>',
        unsafe_allow_html=True
    )


    c1, c2, c3 = st.columns(3, gap="medium")


    with c1:

        st.markdown("""
        <div class="info-card">

            <div class="info-icon">📄</div>

            <div class="info-title">
                01 — Upload
            </div>

            <div class="info-text">
                Upload your resume in PDF, DOCX or TXT format.
            </div>

        </div>
        """, unsafe_allow_html=True)


    with c2:

        st.markdown("""
        <div class="info-card">

            <div class="info-icon">🧠</div>

            <div class="info-title">
                02 — Understand
            </div>

            <div class="info-text">
                AI analyzes your resume and identifies your
                strongest technical career direction.
            </div>

        </div>
        """, unsafe_allow_html=True)


    with c3:

        st.markdown("""
        <div class="info-card">

            <div class="info-icon">✦</div>

            <div class="info-title">
                03 — Discover
            </div>

            <div class="info-text">
                Find relevant job opportunities based on
                your role and preferred location.
            </div>

        </div>
        """, unsafe_allow_html=True)


# =========================================================
# FOOTER
# =========================================================

st.markdown("""
<div class="footer">

    CareerAI · AI-Powered Job Discovery<br>
    Resume Intelligence + Job Search

</div>
""", unsafe_allow_html=True)
