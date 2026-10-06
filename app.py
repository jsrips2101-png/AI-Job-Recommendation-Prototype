import streamlit as st
import requests
import json
import re
import os
from groq import Groq
from pypdf import PdfReader
from docx import Document


# =========================================================
# PAGE SETTINGS
# =========================================================

st.set_page_config(
    page_title="CareerAI - Smart Job Finder",
    page_icon="💜",
    layout="wide"
)


# =========================================================
# SIMPLE PROFESSIONAL DESIGN
# =========================================================

st.markdown("""
<style>

.stApp {
    background-color: #f7f8fc;
}

.block-container {
    max-width: 1150px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* Main title */
.main-title {
    font-size: 42px;
    font-weight: 800;
    color: #17172b;
    margin-bottom: 5px;
}

.subtitle {
    font-size: 17px;
    color: #667085;
    margin-bottom: 30px;
}

/* Cards */
.card {
    background-color: white;
    border: 1px solid #e6e8f0;
    border-radius: 18px;
    padding: 25px;
    margin-bottom: 20px;
    box-shadow: 0px 6px 20px rgba(20, 20, 50, 0.05);
}

/* Section headings */
.section-title {
    font-size: 25px;
    font-weight: 750;
    color: #17172b;
    margin-top: 25px;
    margin-bottom: 5px;
}

.section-text {
    color: #667085;
    font-size: 14px;
    margin-bottom: 20px;
}

/* Role */
.role-box {
    background-color: #f0edff;
    border: 1px solid #ddd6fe;
    border-radius: 15px;
    padding: 22px;
    text-align: center;
}

.role-label {
    color: #6d5bd0;
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
}

.role-name {
    color: #29215f;
    font-size: 28px;
    font-weight: 800;
    margin-top: 5px;
}

/* Job cards */
.job-box {
    background-color: white;
    border: 1px solid #e4e7ec;
    border-radius: 17px;
    padding: 22px;
    margin-top: 15px;
    margin-bottom: 10px;
}

.job-title {
    font-size: 20px;
    font-weight: 750;
    color: #17172b;
}

.job-company {
    font-size: 14px;
    font-weight: 600;
    color: #344054;
    margin-top: 9px;
}

.job-location {
    font-size: 13px;
    color: #667085;
    margin-top: 5px;
}

.job-description {
    font-size: 13px;
    line-height: 1.6;
    color: #667085;
    margin-top: 14px;
}

/* Skill */
.skill {
    display: inline-block;
    background-color: #f4f3ff;
    color: #5746af;
    border: 1px solid #ddd6fe;
    padding: 6px 12px;
    border-radius: 20px;
    margin: 4px;
    font-size: 13px;
    font-weight: 600;
}

/* Buttons */
.stButton > button {
    border-radius: 12px;
    min-height: 48px;
    font-weight: 700;
}

/* Footer */
.footer {
    text-align: center;
    color: #98a2b3;
    font-size: 12px;
    margin-top: 50px;
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
# API VALIDATION
# =========================================================

if not GROQ_API_KEY:

    st.error("Groq API key is missing.")

    st.info(
        "Please add GROQ_API_KEY in Streamlit Secrets."
    )

    st.stop()


if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:

    st.error("Adzuna API credentials are missing.")

    st.info(
        "Please add ADZUNA_APP_ID and ADZUNA_APP_KEY "
        "in Streamlit Secrets."
    )

    st.stop()


client = Groq(
    api_key=GROQ_API_KEY
)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">💜 CareerAI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Turn your resume into your next career opportunity.'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# INTRO
# =========================================================

col1, col2, col3 = st.columns(3)

with col1:

    st.markdown(
        '<div class="card">'
        '<h3>📄 Resume Analysis</h3>'
        '<p>AI reads your resume and understands your technical profile.</p>'
        '</div>',
        unsafe_allow_html=True
    )

with col2:

    st.markdown(
        '<div class="card">'
        '<h3>🧠 Career Intelligence</h3>'
        '<p>Identify the most suitable technical role and skills.</p>'
        '</div>',
        unsafe_allow_html=True
    )

with col3:

    st.markdown(
        '<div class="card">'
        '<h3>💼 Job Discovery</h3>'
        '<p>Find relevant job opportunities based on your profile.</p>'
        '</div>',
        unsafe_allow_html=True
    )


# =========================================================
# INPUT SECTION
# =========================================================

st.markdown(
    '<div class="section-title">Start your job search</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-text">'
    'Upload your resume and choose your preferred job location.'
    '</div>',
    unsafe_allow_html=True
)


input_col1, input_col2 = st.columns(2)


with input_col1:

    uploaded_file = st.file_uploader(
        "Upload your resume",
        type=["pdf", "docx", "txt"],
        help="Supported formats: PDF, DOCX and TXT"
    )


with input_col2:

    location = st.text_input(
        "Preferred job location",
        placeholder="Example: Chennai"
    )


st.write("")


analyze = st.button(
    "✨ Analyze Resume & Find Jobs",
    type="primary",
    use_container_width=True
)


# =========================================================
# READ RESUME
# =========================================================

def read_resume(file):

    filename = file.name.lower()

    # PDF
    if filename.endswith(".pdf"):

        reader = PdfReader(file)

        text = ""

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        return text.strip()


    # DOCX
    elif filename.endswith(".docx"):

        document = Document(file)

        text = "\n".join(
            paragraph.text
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        )

        return text.strip()


    # TXT
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
        r"\s+",
        " ",
        text
    )

    text = re.sub(
        r"[^a-zA-Z0-9+.#\s]",
        " ",
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

1. Return ONLY valid JSON.
2. Do not return markdown.
3. Do not explain your answer.
4. Do not invent information.
5. Choose ONE primary technical role.
6. Role must contain a maximum of 3 words.
7. Select a maximum of 6 technical skills.
8. Only select skills supported by the resume.

Return exactly this structure:

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
# SHOW JOB
# =========================================================

def show_job(
    number,
    job
):

    title = job.get(
        "title",
        "Job title unavailable"
    )

    company = job.get(
        "company",
        {}
    ).get(
        "display_name",
        "Company not specified"
    )

    job_location = job.get(
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

    if len(description) > 280:

        description = (
            description[:280]
            + "..."
        )

    apply_url = job.get(
        "redirect_url",
        "#"
    )


    st.markdown(
        f"""
        <div class="job-box">

        <div class="job-title">
        {number}. {title}
        </div>

        <div class="job-company">
        🏢 {company}
        </div>

        <div class="job-location">
        📍 {job_location}
        </div>

        <div class="job-description">
        {description}
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )


    st.link_button(
        "View & Apply →",
        apply_url,
        use_container_width=True
    )


# =========================================================
# MAIN PROCESS
# =========================================================

if analyze:

    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    if uploaded_file is None:

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
        # STEP 1
        # -------------------------------------------------

        with st.spinner(
            "📖 Reading your resume..."
        ):

            resume_text = read_resume(
                uploaded_file
            )


        if not resume_text:

            st.error(
                "Could not extract text from your resume."
            )

            st.stop()


        # -------------------------------------------------
        # STEP 2
        # -------------------------------------------------

        with st.spinner(
            "🧠 AI is analyzing your profile..."
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
            '<div class="section-title">'
            'Your AI Career Profile'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-text">'
            'Based on the information identified in your resume.'
            '</div>',
            unsafe_allow_html=True
        )


        profile_col1, profile_col2 = st.columns(
            [1, 2],
            gap="large"
        )


        with profile_col1:

            st.markdown(
                f"""
                <div class="role-box">

                <div class="role-label">
                Recommended Role
                </div>

                <div class="role-name">
                {role}
                </div>

                </div>
                """,
                unsafe_allow_html=True
            )


        with profile_col2:

            st.markdown(
                '<div class="card">'
                '<b>🛠 Technical Skills Identified</b>'
                '</div>',
                unsafe_allow_html=True
            )

            skill_html = ""

            for skill in skills:

                skill_html += (
                    f'<span class="skill">'
                    f'{skill}'
                    f'</span>'
                )

            st.markdown(
                skill_html,
                unsafe_allow_html=True
            )


        # -------------------------------------------------
        # STEP 3
        # -------------------------------------------------

        st.markdown(
            '<div class="section-title">'
            'Recommended Opportunities'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="section-text">
            Searching for <b>{role}</b> opportunities
            in <b>{location}</b>.
            </div>
            """,
            unsafe_allow_html=True
        )


        with st.spinner(
            "🔎 Finding relevant jobs..."
        ):

            jobs = search_jobs(
                role,
                skills,
                location
            )


        if not jobs:

            st.warning(
                f"No matching jobs were found for {location}."
            )


        else:

            st.success(
                f"Found {len(jobs)} job opportunities."
            )


            for index, job in enumerate(
                jobs,
                start=1
            ):

                show_job(
                    index,
                    job
                )


    except json.JSONDecodeError:

        st.error(
            "AI returned an unexpected response. "
            "Please try again."
        )


    except Exception as error:

        st.error(
            "Something went wrong while processing your request."
        )

        st.exception(error)


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">
    CareerAI · AI-Powered Job Recommendation System<br>
    Resume Analysis • AI Career Matching • Job Discovery
    </div>
    """,
    unsafe_allow_html=True
)
