import streamlit as st
from PIL import Image
import pdfplumber
import re
import pandas as pd
from streamlit_tags import st_tags
import random
import plotly.express as px
import pyttsx3


def clean_resume_text(text):
    text = re.sub(r"[]", "", text)  # remove icons
    text = re.sub(r"\s+", " ", text)           # normalize spaces
    text = text.replace(".", ".\n")            # break long lines
    return text

import streamlit.components.v1 as components
import time

def speak_with_highlight(text,box):
    clean_text = clean_resume_text(text)

    components.html(
        "<script>window.scrollTo({top: 0, behavior: 'smooth'});</script>",
        height=0,
    )

    engine = pyttsx3.init()
    engine.setProperty("rate", 160)

    lines = [l.strip() for l in clean_text.split("\n") if l.strip()]
    

    for i in range(len(lines)):
        html = ""
        for j, line in enumerate(lines):
            if i == j:
                html += f"<div style='background-color:yellow;color:black;font-weight:bold'>{line}</div>"
            else:
                html += f"<div style='color:gray'>{line}</div>"

        box.markdown(html, unsafe_allow_html=True)

        engine.say(lines[i])
        engine.runAndWait()
        time.sleep(0.1)

    engine.stop()



def extract_name(text):
    lines = text.split("\n")

    for line in lines[:30]:   # ⬅️ CHANGED from 10 to 30 lines
        line = line.strip()

        # Case 1: Name: XYZ
        if line.lower().startswith("name"):
            parts = line.split(":")
            if len(parts) > 1:
                candidate = parts[1].strip()
                if re.match(r"^[A-Za-z ]+$", candidate):
                    return candidate

        # Case 2: Standalone name line
        if (
            2 <= len(line.split()) <= 3
            and re.match(r"^[A-Za-z ]+$", line)
            and not any(x in line.lower() for x in [
                "resume", "email", "phone", "mobile", "profile", "personal",
                "college", "school", "institute", "university", "junior", "polytechnic"
            ])
        ):
            return line

    return "Not found"



# -------- AUTH IMPORT --------
from auth.auth import create_user, login_user

# ---- Local imports ----
from modules.pdf_utils import show_pdf
from modules.download_utils import download_link
from modules.skills_utils import detect_fields
from modules.scoring_utils import calculate_resume_score

# -------- RECRUITER EXTRA FEATURES --------

def generate_interview_questions(sector):
    questions = {
        "IT": [
            "Explain a Python project you worked on.",
            "What is SQL and how have you used it?",
            "How do you debug code?"
        ],
        "Healthcare": [
            "How do you analyze healthcare data?",
            "Explain patient data privacy importance.",
            "What tools are used in healthcare analytics?"
        ],
        "Finance": [
            "Explain financial statement analysis.",
            "What is risk management?",
            "How do you analyze market trends?"
        ]
    }
    return questions.get(sector, [])


def predict_training_time(score):
    if score >= 80:
        return "1–2 weeks"
    elif score >= 60:
        return "3–4 weeks"
    else:
        return "1–2 months"


def generate_email(candidate_name):
    return f"""
Subject: Interview Invitation

Dear {candidate_name},

We are pleased to inform you that you have been shortlisted for an interview.

Our team will contact you with further details.

Best regards,
HR Team
"""



# -------- SESSION STATE --------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_rows" not in st.session_state:
    st.session_state.user_rows = []

# -------- SECTOR DATABASE --------
SECTOR_DATA = {
    "IT": {
        "roles": ["Data Analyst", "Web Developer", "Data Scientist"],
        "jobs": [
            ("Junior Data Analyst", "https://www.linkedin.com/jobs/search/?keywords=Junior%20Data%20Analyst"),
            ("Python Developer", "https://www.linkedin.com/jobs/search/?keywords=Python%20Developer")
        ]
    },

    "Healthcare": {
        "roles": ["Healthcare Data Analyst", "Medical Assistant"],
        "jobs": [
            ("Healthcare Analyst", "https://www.linkedin.com/jobs/search/?keywords=Healthcare%20Analyst"),
            ("Medical Data Specialist", "https://www.linkedin.com/jobs/search/?keywords=Medical%20Data")
        ]
    },

    "Finance": {
        "roles": ["Financial Analyst", "Investment Analyst"],
        "jobs": [
            ("Financial Analyst", "https://www.linkedin.com/jobs/search/?keywords=Financial%20Analyst"),
            ("Investment Associate", "https://www.linkedin.com/jobs/search/?keywords=Investment%20Analyst")
        ]
    }
}

# -------- Skill Requirements --------
ROLE_SKILLS = {
    "Data Analyst": {"python", "sql", "excel", "power bi", "tableau", "statistics"},
    "Web Developer": {"html", "css", "javascript", "react", "django"},
    "Data Scientist": {"python", "machine learning", "statistics", "pandas"},

    "Healthcare Data Analyst": {"excel", "statistics", "data analysis", "healthcare systems"},
    "Medical Assistant": {"patient care", "medical terminology", "communication"},

    "Financial Analyst": {"excel", "financial modeling", "accounting", "statistics"},
    "Investment Analyst": {"finance", "market analysis", "excel"}

}


def extract_skills_from_text(text):
    text = text.lower()
    skills_found = set()
    for skills in ROLE_SKILLS.values():
        for skill in skills:
            if skill in text:
                skills_found.add(skill)
    return list(skills_found)


def predict_salary(years_exp, skill_count):
    base_salary = 3.5
    salary = base_salary + (years_exp * 0.8) + (skill_count * 0.3)
    return round(salary - 0.7, 1), round(salary + 0.7, 1)


def learning_resources(skill):
    resources = {
        "python": {
            "course": "https://www.coursera.org/specializations/python",
            "youtube": "https://www.youtube.com/watch?v=_uQrJ0TkZlc"
        },
        "sql": {
            "course": "https://www.coursera.org/learn/sql-for-data-science",
            "youtube": "https://www.youtube.com/watch?v=HXV3zeQKqGY"
        },
        "excel": {
            "course": "https://www.coursera.org/learn/excel-skills-for-business",
            "youtube": "https://www.youtube.com/watch?v=Vl0H-qTclOg"
        },
        "power bi": {
            "course": "https://www.coursera.org/learn/power-bi-data-analysis",
            "youtube": "https://www.youtube.com/watch?v=AGrl-H87pRU"
        },
        "tableau": {
            "course": "https://www.coursera.org/learn/data-visualization-tableau",
            "youtube": "https://www.youtube.com/watch?v=TPMlZxRRaBQ"
        },
        "statistics": {
            "course": "https://www.coursera.org/learn/basic-statistics",
            "youtube": "https://www.youtube.com/watch?v=xxpc-HPKN28"
        },
        "healthcare systems": {
            "course": "https://www.coursera.org/learn/health-informatics",
            "youtube": "https://www.youtube.com/watch?v=q2cXh7g8RzA"
        },
        "patient care": {
            "course": "https://www.coursera.org/learn/patient-care",
            "youtube": "https://www.youtube.com/watch?v=O6Z7Kp0QwJ8"
        },
        "medical terminology": {
            "course": "https://www.coursera.org/learn/medical-terminology",
            "youtube": "https://www.youtube.com/watch?v=F8ME0dZr8go"
        },

        # Finance Skills
        "financial modeling": {
            "course": "https://www.coursera.org/learn/financial-modeling",
            "youtube": "https://www.youtube.com/watch?v=I8zQZzJ6K1g"
        },
        "accounting": {
            "course": "https://www.coursera.org/learn/wharton-accounting",
            "youtube": "https://www.youtube.com/watch?v=WEDIj9JBTC8"
        },
        "market analysis": {
            "course": "https://www.coursera.org/learn/market-analysis",
            "youtube": "https://www.youtube.com/watch?v=R4t4fC8f7gQ"
        },
        "finance": {
            "course": "https://www.coursera.org/learn/finance-for-everyone",
            "youtube": "https://www.youtube.com/watch?v=2uSH8c5gJ4s"
        }
    }

    
    return resources.get(skill.lower())


# -------- LOGIN PAGE --------
def login_page():
    st.set_page_config(page_title="Login | An AI-Based System for Resume Analysis and Recommendation", layout="centered")
    st.title(" An AI-Based System for Resume Analysis and Recommendation")
    menu = ["Login", "Sign Up"]
    choice = st.selectbox("Select Option", menu)

    if choice == "Sign Up":
        st.subheader("Create Account")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Sign Up"):
            if create_user(username, password):
                st.success("Account created successfully! Please login.")
            else:
                st.error("Username already exists")

    else:
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if login_user(username, password):
                st.session_state.logged_in = True
                st.success("Login successful 🎉")
                st.rerun()
            else:
                st.error("Invalid username or password")



# ----------------- MAIN APP -----------------
def run():
    if not st.session_state.logged_in:
        login_page()
        return

    st.set_page_config(page_title="An AI-Based System for Resume Analysis and Recommendation", page_icon="assets/logo2.png")
    logo = Image.open("assets/logo2.png")

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image(logo, width=120)
    st.title("An AI-Based System for Resume Analysis and recommendation")
    highlight_box = st.empty()


    st.sidebar.button("🚪 Logout", on_click=lambda: st.session_state.update({"logged_in": False}))

    st.sidebar.markdown("# Choose User")
    mode = st.sidebar.selectbox("Choose among the given options:", ["Candidate", "Admin"])
    # ----------------- USER MODE -----------------
    if mode == "Candidate":
        st.info("Upload your résumé (PDF) for instant analysis.")
        pdf_file = st.file_uploader("Choose your Résumé", type=["pdf"])
        sector = st.selectbox(
            "🏭 Select Your Sector",
            list(SECTOR_DATA.keys())
        )

        if pdf_file:
            text = ""
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    if page.extract_text():
                        text += page.extract_text() + "\n"

            show_pdf(pdf_file.getvalue())

            name = extract_name(text)
            email = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}", text)
            phone = re.findall(r"\+?\d[\d -]{8,}\d", text)

            st.subheader("📄 Extracted Information")
            st.write(f"**Name:** {name}")
            st.write(f"**Email:** {email[0] if email else 'Not found'}")
            st.write(f"**Phone:** {phone[0] if phone else 'Not found'}")

            detected_fields = detect_fields(text) or ["General"]
            st.subheader("🧠 Suggested Career Fields")
            st_tags(label="Detected Fields", value=detected_fields)

            score, tips = calculate_resume_score(text)
            st.subheader("📊 Résumé Score")
            st.progress(score)
            st.write(f"**ATS Compatibility Score: {score}%**")

            if tips:
                for t in tips:
                    st.warning(t)

            extracted_skills = extract_skills_from_text(text)
            sector_roles = SECTOR_DATA[sector]["roles"]
            best_role = None
            best_match = 0
            for role in sector_roles:
                role_skills = ROLE_SKILLS[role]
                matched = len(set(extracted_skills) & role_skills)
                if matched > best_match:
                    best_match = matched
                    best_role = role
            target_role = best_role if best_role else sector_roles[0]

            def recommend_best_sector(extracted_skills):
                best_sector = None
                best_score = 0
                for sector, data in SECTOR_DATA.items():
                    sector_score = 0
                    for role in data["roles"]:
                        role_skills = ROLE_SKILLS[role]
                        matched = len(set(extracted_skills) & role_skills)
                        sector_score += matched
                    if sector_score > best_score:
                            best_score = sector_score
                            best_sector = sector
                return best_sector



            missing_skills = ROLE_SKILLS[target_role] - set(extracted_skills)

            total_required = len(ROLE_SKILLS[target_role])
            matched = len(set(extracted_skills) & ROLE_SKILLS[target_role])
            skill_match_percent = int((matched / total_required) * 100)

            st.subheader("🎯 Skill Match Analysis")
            st.metric(
                label=f"{target_role} Skill Match",
                value=f"{skill_match_percent}%",
                delta=f"{matched}/{total_required} skills matched"
            )
            if skill_match_percent < 20:
                recommended_sector = recommend_best_sector(extracted_skills)
                st.error(f"⚠️ Your skills do not match the {sector} sector.")
                if recommended_sector and recommended_sector != sector:
                    st.success(
                        f"✅ Based on your resume, the **{recommended_sector}** sector is a better match."
                    )
                    sector = recommended_sector






            st.subheader("🧠 AI Resume Summary")

            summary = f"""
            You are a potential {target_role} candidate with experience in
            {', '.join(extracted_skills[:5]) if extracted_skills else 'basic technical skills'}.

            Your resume achieved an ATS compatibility score of {score}%.
            To improve your profile, focus on developing skills such as
           {', '.join(list(missing_skills)[:3]) if missing_skills else 'advanced analytics tools'}.
            """

            st.info(summary)

            st.subheader("📈 Skill Comparison Chart")

            skill_df = pd.DataFrame({
                "Skill": list(ROLE_SKILLS[target_role]),
                "Status": [
                "Present" if skill in extracted_skills else "Missing"
                for skill in ROLE_SKILLS[target_role]
                ]
            })

            fig = px.bar(
                skill_df,
                x="Skill",
                color="Status",
                title="Required vs Available Skills"
            )

            st.plotly_chart(fig, width="stretch")
            
            st.subheader("🧩 Experience Level (Estimated)")

            experience_years = max(0, min(5, len(extracted_skills) // 2))

            if experience_years <= 1:
                st.success("🟢 Fresher Level (0–1 years)")
            elif experience_years <= 3:
                st.success("🟡 Junior Level (2–3 years)")
            else:
                st.success("🔵 Mid-Level (4+ years)")

            st.subheader("🏆 Resume Strength")

            if score >= 80:
                st.success("🔥 Strong Resume – High Shortlisting Chance")
            elif score >= 60:
                st.warning("⚡ Moderate Resume – Needs Improvement")
            else:
                st.error("❌ Weak Resume – Significant Improvement Needed")






            st.subheader("❌ Missing Skills")
            for skill in missing_skills:
                st.write("- " + skill.title())

            if missing_skills:
                st.subheader("📚 Recommended Learning Resources")

                for skill in missing_skills:
                    res = learning_resources(skill)
                    if res:
                        st.markdown(f"### 🔹 {skill.title()}")

                        st.link_button(
                            f"📘 {skill.title()} – Structured Online Course",
                            res["course"]
                        )

                        st.link_button(
                            f"▶ {skill.title()} – Beginner Friendly YouTube Tutorial",
                            res["youtube"]
                        )


            st.subheader("💼 Sector-Based Job Recommendations")
            for role, link in SECTOR_DATA[sector]["jobs"]:
                st.write(f"### {role}")
                st.link_button("Apply Here", link)


            min_sal, max_sal = predict_salary(random.randint(1, 3), len(extracted_skills))
            st.subheader("💰 Salary Prediction")
            st.write(f"₹{min_sal} – ₹{max_sal} LPA")

            st.session_state.user_rows.append({
                "Name": name if name else "Unknown",
                "Email": email[0] if email else "Unknown",
                "Score": score,
                "Salary": f"{min_sal}-{max_sal} LPA"
            })

            # -------- VOICE FEEDBACK --------
            analysis_text = f"""
            Resume analysis completed successfully.
            Candidate name is {name if name else 'Not found'}.
            Your ATS score is {score} percent.
            Suggested career role is {target_role}.
            Predicted salary range is {min_sal} to {max_sal} LPA.
            """


            st.subheader("🔊 Voice Resume Reader")

            if st.button("🔈 Read Resume with Highlight"):
                speak_with_highlight(text, highlight_box)




    # ----------------- ADMIN MODE -----------------
        # ----------------- ADMIN MODE -----------------
        
    elif mode == "Admin":
        st.title("🏢 Admin Panel – Resume Screening System")
        sector = st.selectbox(
        "🏭 Select Recruitment Sector",
        list(SECTOR_DATA.keys())
        )
        st.info(f"Analyzing resumes for {sector} sector")


        st.info("Upload Job Description and multiple resumes to find best candidates")

        job_desc = st.text_area(
            "📄 Job Description",
            height=200,
            placeholder="Paste job description here..."
        )

        resume_files = st.file_uploader(
            "📂 Upload Multiple Resumes (PDF)",
            type=["pdf"],
            accept_multiple_files=True
        )

        if st.button("🔍 Analyze Resumes"):
            if not job_desc or not resume_files:
                st.warning("Please upload job description and resumes")
            else:
                from modules.bulk_resume_matcher import rank_resumes

                resume_texts = []
                resume_names = []

                for file in resume_files:
                    text = ""
                    with pdfplumber.open(file) as pdf:
                        for page in pdf.pages:
                            if page.extract_text():
                                text += page.extract_text()
                    resume_texts.append(text)
                    resume_names.append(file.name)

                scores = rank_resumes(job_desc, resume_texts)

                results = pd.DataFrame({
                    "Resume Name": resume_names,
                    "Match Score (%)": scores
                }).sort_values(by="Match Score (%)", ascending=False)

                st.subheader("🏆 Ranked Resumes")
                st.dataframe(results, width="stretch")

                top_n = st.slider("Show Top Candidates", 1, len(results), 3)
                st.success("🎯 Top Candidates")
                st.dataframe(results.head(top_n), width="stretch")
                # -------- DOWNLOAD SHORTLISTED CANDIDATES --------
                
                shortlisted = results.head(top_n)
                st.subheader("⬇ Download Shortlisted Candidates")
                csv = shortlisted.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "📥 Download CSV",
                    csv,
                    "shortlisted_candidates.csv",
                    "text/csv"
                )
                # -------- SUMMARY REPORT --------
                summary = f"""
                Recruitment Summary Report
                ==========================
                Sector: {sector}
                Total Resumes: {len(results)}
                Top Candidates: {top_n}
                Top Candidate List:
                """
                for _, row in shortlisted.iterrows():
                    summary += f"\n{row['Resume Name']} — {row['Match Score (%)']}%"
                st.download_button(
                    "📄 Download Summary Report",
                    summary,
                    "summary_report.txt"
                    
                )
                # -------- INTERVIEW QUESTIONS --------
                st.subheader("🧠 Sector Interview Questions")
                questions = generate_interview_questions(sector)
                
                for q in questions:
                    st.write("•", q)
                    
                # -------- TRAINING TIME PREDICTION --------
                st.subheader("⏳ Training Time Prediction")
                for _, row in shortlisted.iterrows():
                    training = predict_training_time(row["Match Score (%)"])
                    st.write(f"{row['Resume Name']}: {training}")
                    
                # -------- AUTO INTERVIEW EMAIL --------
                st.subheader("📧 Interview Email Template")
                for _, row in shortlisted.iterrows():
                    email_text = generate_email(row["Resume Name"])
                    st.text_area(
                        f"Email for {row['Resume Name']}",
                        email_text,
                        height=150
                    )

    # -------- VOICE FUNCTION --------
    



# -------- RUN --------
if __name__ == "__main__":
    run()



