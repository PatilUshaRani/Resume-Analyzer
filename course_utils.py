import streamlit as st
import random
import uuid

def course_recommender(courses, certificates):
    """Show courses and certificates separately with unique sliders"""
    
    # --- Courses Section ---
    if courses:
        st.subheader("Courses 🎓")
        courses_key = f"courses_slider_{uuid.uuid4()}"
        n_courses = st.slider(
            "Number of Courses to Show",
            1,
            min(5, len(courses)),
            3,
            key=courses_key
        )
        random.shuffle(courses)
        st.markdown("**Recommended Courses:**")
        for i, (name, link) in enumerate(courses[:n_courses], start=1):
            st.markdown(f"{i}. [{name}]({link})")
    
    # --- Certificates Section ---
    if certificates:
        st.subheader("Certificates 🏅")
        certs_key = f"certs_slider_{uuid.uuid4()}"
        n_certs = st.slider(
            "Number of Certificates to Show",
            1,
            min(5, len(certificates)),
            3,
            key=certs_key
        )
        random.shuffle(certificates)
        st.markdown("**Recommended Certificates:**")
        for i, (name, link) in enumerate(certificates[:n_certs], start=1):
            st.markdown(f"{i}. [{name}]({link})")
    
    # Return tuples so we can store in session_state
    return courses[:n_courses] if courses else [], certificates[:n_certs] if certificates else []
