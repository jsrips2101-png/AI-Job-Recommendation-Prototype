import streamlit as st
import requests
import json
import re
import os

from groq import Groq
from pypdf import PdfReader
from docx import Document


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="AI Job Recommendation System",
    page_icon="💼",
    layout="wide"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.main {
    background-color: #f7f9fc;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}

.hero {
    padding: 35px;
    border-radius: 20px;
    background: linear-gradient(
        135deg,
        #667eea 0%,
        #764ba2 100%
    );
    color: white;
    margin-bottom: 30px;
}

.hero h1 {
    font-size: 42px;
    margin-bottom: 10px;
}

.hero p {
    font-size: 18px;
    opacity: 0.95;
}

.job-card {
    background: white;
    padding: 22px;
    border-radius: 15px;
    margin-bottom: 18px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 3px 12px rgba(0,0,0,0.06);
}

.job-title {
    font-size: 22px;
    font-weight: 700;
}

.company {
    font-size: 16px;
    margin-top: 8px;
}

.location {
    font-size: 15px;
    margin-top: 5px;
}

.badge {
    display: inline-block;
    padding: 5px 12px;
    border-radius: 20px;
    background-color: #eef2ff;
    margin-right: 6px;
    margin-top: 8px;
    font-size: 13px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# LOAD API KEYS
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
# CHECK API KEYS
# =========================================================

if not GROQ_API_KEY:

    st.error("Groq API key is missing.")

    st.stop()


if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:

    st.error("Adzuna API credentials are missing.")

    st.stop()


client = Groq(
    api_key=GROQ_API_KEY
)


# =========================================================
# HERO SECTION
# =========================================================

st.markdown("""
<div class="hero">

<h1>💼 AI-Powered Job Recommendation System</h1>

<p>
Upload your resume and discover job opportunities
that match your skills and career profile.
</p>

</div>
""", unsafe_allow_html=True)


# =========================================================
# RESUME READER
# =========================================================

def read_resume(file):

    filename = file.name.lower()

    # ---------------- PDF ----------------

    if filename.endswith(".pdf"):

        reader = PdfReader(file)

        text = ""

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:

                text += page_text + "\n"

        return text.strip()


    # ---------------- DOCX ----------------

    elif filename.endswith(".docx"):

        doc = Document(file)

        text = "\n".join(
            paragraph.text
            for paragraph in doc.paragraphs
            if paragraph.text.strip()
        )

        return text.strip()


    # ---------------- TXT ----------------

    elif filename.endswith(".txt"):

        return file.read().decode(
            "utf-8",
            errors="ignore"
        )


    else:

        raise ValueError(
            "Unsupported file format."
        )


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
# AI RESUME ANALYSIS
# =========================================================

def analyze_resume(resume_text):

    prompt = f"""

You are an AI resume analysis system.

Analyze the resume below and identify the
most suitable technical job role and important
technical skills.

STRICT RULES:

- Return ONLY valid JSON.
- No markdown.
- No explanation.
- Do not invent information.
- Choose ONE primary technical role.
- Maximum 3 words for the role.
- Maximum 6 technical skills.
- Skills must be relevant to the candidate.

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

    result = response.choices[
        0
    ].message.content.strip()


    # Remove accidental markdown

    result = re.sub(
        r"```json|```",
        "",
        result
    ).strip()


    return json.loads(result)


# =========================================================
# ADZUNA JOB SEARCH
# =========================================================

def search_jobs(
    role,
    skills,
    location
):

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
            f"Adzuna API error: "
            f"{response.status_code}"
        )


    data = response.json()

    return data.get(
        "results",
        []
    )


# =========================================================
# DISPLAY JOB
# =========================================================

def display_job(
    number,
    job
):

    title = job.get(
        "title",
        "Job title not available"
    )

    company = job.get(
        "company",
        {}
    ).get(
        "display_name",
        "Company not specified"
    )

    location = job.get(
        "location",
        {}
    ).get(
        "display_name",
        "Location not specified"
    )

    description = job.get(
        "description",
        ""
    )

    apply_url = job.get(
        "redirect_url",
        "#"
    )


    # Limit description

    if len(description) > 300:

        description = (
            description[:300]
            + "..."
        )


    st.markdown(
        f"""
        <div class="job-card">

        <div class="job-title">
        {number}. {title}
        </div>

        <div class="company">
        🏢 <b>{company}</b>
        </div>

        <div class="location">
        📍 {location}
        </div>

        <br>

        <div>
        {description}
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )


    st.link_button(
        "🔗 Apply for this Job",
        apply_url
    )


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("📄 Resume")

    uploaded_file = st.file_uploader(
        "Upload your resume",
        type=[
            "pdf",
            "docx",
            "txt"
        ]
    )


    st.header("📍 Job Preferences")

    location = st.text_input(
        "Preferred Location",
        placeholder="Example: Chennai"
    )


    st.markdown("---")

    st.info(
        """
        The system analyzes your resume
        using AI and searches for relevant
        job opportunities.
        """
    )


# =========================================================
# MAIN ACTION
# =========================================================

st.markdown(
    "## 🚀 Find Your Recommended Jobs"
)


if uploaded_file:

    st.success(
        f"Resume uploaded: "
        f"{uploaded_file.name}"
    )


if st.button(
    "✨ Analyze Resume & Find Jobs",
    type="primary",
    use_container_width=True
):

    # ---------------------------------------------
    # VALIDATION
    # ---------------------------------------------

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


    # ---------------------------------------------
    # PROCESS
    # ---------------------------------------------

    try:

        with st.spinner(
            "📖 Reading your resume..."
        ):

            resume_text = read_resume(
                uploaded_file
            )


        if not resume_text:

            st.error(
                "Could not extract text "
                "from the resume."
            )

            st.stop()


        with st.spinner(
            "🤖 AI is analyzing your resume..."
        ):

            cleaned_text = clean_resume(
                resume_text
            )

            analysis = analyze_resume(
                cleaned_text
            )


        role = analysis.get(
            "role"
        )

        skills = analysis.get(
            "skills",
            []
        )


        # ---------------------------------------------
        # AI RESULT
        # ---------------------------------------------

        st.markdown(
            "## 🧠 AI Resume Analysis"
        )


        col1, col2 = st.columns(2)


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


        st.markdown(
            "**Technical Skills**"
        )


        for skill in skills:

            st.markdown(
                f"""
                <span class="badge">
                {skill}
                </span>
                """,
                unsafe_allow_html=True
            )


        st.markdown("---")


        # ---------------------------------------------
        # SEARCH JOBS
        # ---------------------------------------------

        with st.spinner(
            "🔎 Searching for matching jobs..."
        ):

            jobs = search_jobs(
                role,
                skills,
                location
            )


        st.markdown(
            "## 💼 Recommended Jobs"
        )


        if not jobs:

            st.warning(
                f"No matching jobs were found "
                f"for {location}."
            )

        else:

            st.success(
                f"Found {len(jobs)} "
                f"job opportunities."
            )


            for index, job in enumerate(
                jobs,
                start=1
            ):

                display_job(
                    index,
                    job
                )


    except Exception as e:

        st.error(
            "Something went wrong."
        )

        st.exception(e)


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "AI-Powered Job Recommendation System | "
    "Resume Analysis + AI + Job Search API"
)