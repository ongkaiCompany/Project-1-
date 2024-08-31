import streamlit as st
import spacy 
from nltk.stem import WordNetLemmatizer
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import io
import pdfplumber
from sklearn.feature_extraction.text import TfidfVectorizer
import base64
import re
from io import BytesIO
import pickle
from nltk.corpus import stopwords
from pymongo import MongoClient
import os
import pandas as pd
import bcrypt
from bson import ObjectId
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import numpy as np
from streamlit_option_menu import option_menu
from streamlit.components.v1 import html


st.set_page_config(layout='wide', initial_sidebar_state="expanded")
nlp = spacy.load('en_core_web_sm')
nltk.download('stopwords')
nltk.download('wordnet')
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))
mongo_url = "mongodb+srv://ResumeProject:Password@resume.slltz.mongodb.net/?retryWrites=true&w=majority&appName=Resume"
client = MongoClient(mongo_url)

#Select database and collection you want to work with 
db= client['Resume']
collection=db['ResumeData']
excel_file = 'C:/Users/ongka/OneDrive/Desktop/FYP Spare/Users.xlsx'
###################################################### CSS ###########################################

# Example of injecting CSS
# Global CSS definition
css = """
<style>
    html, body, [class*="css"] {
        font-family: 'Garamond', serif;  # You can change this to any font you like
    }
    .big-font {
        font-size:20px;  # Adjusts the size of the text
        color: #34495e;  # Optional: changes the color of the text
    }
</style>
"""
st.markdown(css, unsafe_allow_html=True)  # Apply the CSS globally
# Custom CSS to alter spacing

###################################################General###############################################

def load_vectorizer():
    vectorizer_path = 'C:/Users/ongka/OneDrive/Desktop/FYP Spare/vectorizer.pkl'
    with open(vectorizer_path, 'rb') as file:
        vectorizer = pickle.load(file)
    return vectorizer

def read_pdf_file(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        return " ".join(page.extract_text() for page in pdf.pages if page.extract_text())
 

def process_text(text):
    text=text.lower()
    text= re.sub(r'[^a-zA-Z0-9\s]','',text)
    text=re.sub(r'\s+',' ',text).strip()
    words=text.split()
    cleaned_words=[lemmatizer.lemmatize(word)for word in words if word not in stop_words]
    text=' '.join(cleaned_words)
    return text 


#def calculate_cosine_similarity(tfidf_matrix):
   # similarities = cosine_similarity(tfidf_matrix)
  #  return similarities





###################################################Job seeker###############################################
def display_contact_info(emails, phones):
    # Display extracted contact information
    css = """
            <style>
                .info-header {
                    font-size: 20px;
                    font-weight: bold;
                    margin-bottom: 5px;
                }
                .info-content {
                    font-size: 16px;
                    margin-left: 10px;
                }
                .no-info {
                    color: #ff0000;
                    font-style: italic;
                }
            </style>
        """
    st.markdown(css, unsafe_allow_html=True)
    if emails:
        emails_formatted = "<br>".join(emails)  # Joining phone numbers with line breaks
        st.markdown(f"<div class='info-header'>Email Found:</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='info-content'>{emails_formatted}</div>", unsafe_allow_html=True)
        
        #st.markdown(f"**Emails Found:** {', '.join(emails)}")
    else:
        st.markdown(f"<span class='no-info'>No emails found.</span>", unsafe_allow_html=True)
    if phones:
        phones_formatted = "<br>".join(phones)  # Joining phone numbers with line breaks
        st.markdown(f"<div class='info-header'>Phone Numbers Found:</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='info-content'>{phones_formatted}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<span class='no-info'>No phone numbers found.</span>", unsafe_allow_html=True)
        
def read_and_process_file(file):
    if file.type == "application/pdf":
        text = read_pdf_file(file)
    processed_text = process_text(text)
    return processed_text

def extract_info(text):
    doc = nlp(text)
    emails = [ent.text for ent in doc.ents if ent.label_ == "EMAIL"]
    # SpaCy doesn't recognize phone numbers; use regex for this:
    phones = re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text)
    return emails, phones
def display_job_category(max_prob, predicted_label):
    css = """
            <style>
                .info-header {
                    font-size: 20px;
                    font-weight: bold;
                    margin-bottom: 5px;
                }
                .info-content {
                    font-size: 16px;
                    margin-left: 10px;
                }
                .no-info {
                    color: #ff0000;
                    font-style: italic;
                }
            </style>
        """
    # Display the predicted job category based on the model's output
    label_mapping = {
        0: 'ACCOUNTING',
        1: 'ENGINEERING',
        2: 'INFORMATION-TECHNOLOGY'
    }
    threshold = 0.55
    if max_prob < threshold:
        st.markdown("<div class='info-header'>Job Category:</div>", unsafe_allow_html=True)
        st.markdown("<div class='no-info'>Unknown or Irrelevant</div>", unsafe_allow_html=True)
    else:
        # Display the predicted job category
        predicted_category = label_mapping[predicted_label]
        st.markdown("<div class='info-header'>Job Category:</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='info-content'>{predicted_category}</div>", unsafe_allow_html=True)


def extract_contact_info(text):
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    phones = re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text)
    return emails, phones


###################################################Employer ###############################################


def load_users():
    # Load users from Excel file if it exists
    if os.path.exists(excel_file):
        return pd.read_excel(excel_file)
    else:
        # Create a new DataFrame if no file exists
        return pd.DataFrame(columns=['username', 'password'])

def save_users(users):
    # Save user data to Excel file
    with pd.ExcelWriter(excel_file, engine='openpyxl', mode='w') as writer:
        users.to_excel(writer, index=False)

def register_user(username, password):
    users = load_users()
    if username in users['username'].values:
        st.error("Username already exists, please choose another.")
    else:
        # Append the new user data
        new_user = pd.DataFrame({'username': [username], 'password': [password]})
        users = pd.concat([users, new_user], ignore_index=True)
        save_users(users)
        st.success('Registration successful! You can now login.')
        st.session_state['username'] = username
        st.session_state['logged_in'] = True

def check_credentials(username, password):
    users = load_users()
    # Check if username and password match
    user_record = users[(users['username'] == username) & (users['password'] == password)]
    return not user_record.empty

def login_page():
    st.subheader("Login")
    username = st.text_input("Business name", key='login_username')
    password = st.text_input("Password", type="password", key='login_password')
    if st.button("Login"):
        if check_credentials(username, password):
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.success('Logged in successfully!')
        else:
            st.error('Incorrect Username or Password')

def registration_page():
    st.subheader("Register")
    new_username = st.text_input("Business name", key='new_username')
    instructions = """
    _(Please enter your **official business name** as registered with the government. This name will be used to identify your account on Job Matcher and **cannot be changed** once registered.)_
    """
    st.markdown(instructions, unsafe_allow_html=True)
    new_password = st.text_input("Choose a Password", type="password", key='new_password')
    if st.button("Register"):
        register_user(new_username, new_password)
def read_jobs():
    st.header("Read Jobs")
    if 'logged_in' in st.session_state and st.session_state['logged_in']:
        if st.button("Read Jobs"):
            jobs = list(collection.find({"Business Name": st.session_state['username']}))
            if jobs:
                for job in jobs:
                    job_id = str(job['_id'])
                    st.subheader(f"{job['Job Category']} - {job['Job Title']} (ID: {job_id})")
                    st.write(f"**Business Name:** {job['Business Name']}")
                    st.write(f"**Job Description:** {job['Job Description']}")
                    st.write(f"**Location:** {job['Address line']}, {job['Postcode']} {job['City']}, {job['State']}")
                    st.write(f"**Work Type:** {job['WorkType']}")
                    st.write(f"**Salary Range:** {job['Salary From']} to {job['Salary To']}")
                    st.write(f"**Contact Email:** {job['Email']}")

                    # Safely display benefits
                    benefits = job.get('Benefit', [])
                    benefits_display = ", ".join(benefits) if benefits else "No benefits listed"
                    st.write(f"**Benefits:** {benefits_display}")

                    st.write(f"**Company Size:** {job.get('CompanySize', 'Not specified')}")
            else:
                st.write("No jobs found for your company.")
    else:
        st.write("Please log in to view jobs.")
        
def logout():
    # Clear specific session state keys related to login
    if 'logged_in' in st.session_state:
        del st.session_state['logged_in']
    if 'username' in st.session_state:
        del st.session_state['username']
    st.session_state['need_rerun'] = True  # Trigger rerun manually
    st.info('You have been logged out.')
        
def create_job_page():
    st.header("Create Job")
    
    # Fields definition
    create_company = st.text_input("Business Name", value=st.session_state.get('username', ''), key="create_company", disabled=True)
    JobCategory = ["Accounting", "Engineering", "Information-Technology"]
    create_JobCategory = st.selectbox("Job Category", JobCategory, key="create_JobCategory")
    create_title = st.text_input("Job Title *", key="create_title")
    create_Job_Description = st.text_area("Job Description *", key="create_Job_Description")
    create_location = st.text_input("Address Line *", key="create_location")
    create_city = st.text_input("City, Town or Region *", key="create_city")
    states = ["Johor", "Kedah", "Kelantan", "Kuala Lumpur", "Labuan", "Melaka", "Negeri Sembilan", "Pahang", "Penang", "Perak", "Perlis", "Putrajaya", "Sabah", "Sarawak", "Selangor", "Terengganu"]
    create_state = st.selectbox("State *", states, key="create_state")
    create_Postcode = st.text_input("Postcode *", key="create_Postcode")
    WorkType = ["Full-time", "Part-time", "Contract", "Casual"]
    WorkTypeSelection = st.selectbox("Work Type", WorkType, key="create_WorkType")
    create_salary_from = st.number_input("Salary From", min_value=1, step=1, key="create_salary_from", format="%d")
    create_salary_to = st.number_input("Salary To", min_value=create_salary_from, step=1, key="create_salary_to", format="%d")
    create_email = st.text_input("Email *", key="create_email")
    common_benefits = ['Health insurance', 'Dental insurance', 'Retirement plan', 'Stock options', 'Paid time off', 'Remote work options', 'Gym membership', 'Free lunches', 'Childcare']
    selected_benefits = st.multiselect("Select benefits and perks", common_benefits, key="selected_benefits")
    create_company_Size = st.number_input("Company Size", min_value=1, step=1, key="Company Size", format="%d")
    # Button to create a job
    if st.button("Create Job"):
        # Check if all mandatory fields are filled
        if not (create_title and create_Job_Description and create_location and create_city and create_state and create_Postcode and create_email):
            st.error("Please fill in all required fields.")
        elif create_salary_from > create_salary_to:
            st.error("Salary From cannot be greater than Salary To.")
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", create_email):
            st.error("Invalid email format.")
        else:
            job = {
                "Business Name": create_company,
                "Job Category": create_JobCategory,
                "Job Title": create_title,
                "Job Description": create_Job_Description,
                "Address line": create_location,
                "City": create_city,
                "State": create_state,
                "Postcode": create_Postcode,
                "WorkType": WorkTypeSelection,
                "Salary From": create_salary_from,
                "Salary To": create_salary_to,
                "Email": create_email,
                "Benefit": selected_benefits,
                "CompanySize": create_company_Size,
            }
            result = collection.insert_one(job)
            st.success(f"Job Created with ID: {result.inserted_id}")
def update_job():
    st.header("Update Job")
    
    job_id = st.text_input("Enter the MongoDB ID of the job you wish to update", key="update_job_id")
    
    if job_id:
        try:
            job_details = collection.find_one({"_id": ObjectId(job_id)})
        except Exception as e:
            st.error("Invalid ID format. Please enter a valid MongoDB ObjectId.")
            return
        
        if job_details:
            create_JobCategory = st.selectbox("Job Category", ["Accounting", "Engineering", "Information-Technology"], index=["Accounting", "Engineering", "Information-Technology"].index(job_details['Job Category']), key=f"job_cat_{job_id}")
            create_title = st.text_input("Job Title *", value=job_details['Job Title'], key=f"job_title_{job_id}")
            create_Job_Description = st.text_area("Job Description", value=job_details['Job Description'], key=f"job_desc_{job_id}")
            create_location = st.text_input("Address Line", value=job_details['Address line'], key=f"job_loc_{job_id}")
            create_city = st.text_input("City, Town or Region", value=job_details['City'], key=f"job_city_{job_id}")
            states = ["Johor", "Kedah", "Kelantan", "Kuala Lumpur", "Labuan", "Melaka", "Negeri Sembilan", "Pahang", "Penang", "Perak", "Perlis", "Putrajaya", "Sabah", "Sarawak", "Selangor", "Terengganu"]
            create_state = st.selectbox("State", states, index=states.index(job_details['State']), key=f"job_state_{job_id}")
            create_Postcode = st.text_input("Postcode", value=job_details['Postcode'], key=f"job_postcode_{job_id}")
            create_salary_from = st.number_input("Salary From", min_value=1, step=1, format="%d", value=job_details['Salary From'], key=f"salary_from_{job_id}")
            create_salary_to = st.number_input("Salary To", min_value=1, step=1, format="%d", value=job_details['Salary To'], key=f"salary_to_{job_id}")
            create_email = st.text_input("Email", value=job_details['Email'], key=f"job_email_{job_id}")
            common_benefits = ['Health insurance', 'Dental insurance', 'Retirement plan', 'Stock options', 'Paid time off', 'Remote work options', 'Gym membership', 'Free lunches', 'Childcare']
            selected_benefits = st.multiselect("Select benefits and perks", common_benefits, key=f"selected_benefits_{job_id}")
            create_company_Size = st.number_input("Company Size", min_value=1, step=1, format="%d", key=f"company_size_{job_id}")
            WorkType = ["Full-time", "Part-time", "Contract", "Casual"]
            WorkTypeSelection = st.selectbox("Work Type", WorkType, index=WorkType.index(job_details['WorkType']), key=f"work_type_{job_id}")
            if st.button("Update Job", key=f"update_button_{job_id}"):
                collection.update_one(
                    {"_id": ObjectId(job_id)},
                    {"$set": {
                        "Job Category": create_JobCategory,
                        "Job Title":create_title,
                        "Job Description": create_Job_Description,
                        "Address line": create_location,
                        "City": create_city,
                        "State": create_state,
                        "Postcode": create_Postcode,
                        "WorkType": WorkTypeSelection,  # Correct usage after defining
                        "Salary From": create_salary_from,
                        "Salary To": create_salary_to,
                        "Email": create_email,
                        "Benefit": selected_benefits,
                        "CompanySize": create_company_Size,
                    }}
                )
                st.success("Job updated successfully!")
        else:
            st.error("No job found with the provided ID.")
    else:
        st.info("Please enter a MongoDB ID to update a job.")





def delete_job():
    st.header("Delete Job")
    
    # User inputs the MongoDB ID
    job_id = st.text_input("Enter the MongoDB ID of the job you wish to delete", key="delete_job_id")
    
    if st.button("Delete Job"):
        if job_id:
            try:
                # Validate and delete the job based on the entered ID
                result = collection.delete_one({"_id": ObjectId(job_id)})
                if result.deleted_count > 0:
                    st.success("Job deleted successfully!")
                else:
                    st.error("No job found with the provided ID.")
            except Exception as e:
                st.error("Invalid ID format. Please enter a valid MongoDB ObjectId.")
        else:
            st.error("Please enter a MongoDB ID to delete a job.")
def delete_all_jobs():
    st.header("Delete All My Jobs")

    if 'username' in st.session_state and st.session_state['username']:
        user_id = st.session_state['username']
        confirm = st.text_input("Type 'CONFIRM' to delete all your jobs", key="confirm_delete_all")

        if st.button("Delete All Jobs"):
            if confirm == 'CONFIRM':
                try:
                    # Correctly count jobs before deletion
                    job_count = collection.count_documents({"Business Name": user_id})
                    st.write(f"Found {job_count} jobs posted by {user_id}")
                    # Proceed with deletion
                    result = collection.delete_many({"Business Name": user_id})
                    if result.deleted_count > 0:
                        st.success(f"All jobs posted by {user_id} have been deleted successfully! Total deleted: {result.deleted_count}")
                    else:
                        st.error("No jobs found posted by you.")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
            else:
                st.error("You must type 'CONFIRM' to delete all your jobs.")
    else:
        st.error("You are not logged in. Please log in to delete your jobs.")
        
def delete_account():
    st.header("Delete Account and All Related Jobs")

    if 'username' in st.session_state and st.session_state['username']:
        user_id = st.session_state['username']
        confirm = st.text_input("Type 'DeleteAll' to delete your account and all related jobs", key="confirm_delete_account")

        if st.button("Delete My Account"):
            if confirm == 'DeleteAll':
                try:
                    # Delete all jobs from MongoDB
                    job_result = collection.delete_many({"Business Name": user_id})
                    st.success(f"All jobs posted by {user_id} have been deleted successfully! Total deleted: {job_result.deleted_count}")

                    # Delete user account from Excel
                    if os.path.exists(excel_file):
                        users = pd.read_excel(excel_file)
                        # Filter out the user to delete
                        users = users[users['username'] != user_id]
                        # Save the updated DataFrame
                        with pd.ExcelWriter(excel_file, engine='openpyxl', mode='w') as writer:
                            users.to_excel(writer, index=False)
                        st.success("Your account has been deleted successfully.")

                    # Clear session state and log out the user
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.info('You have been logged out. Your account and all associated jobs are deleted.')

                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
            else:
                st.error("You must type 'CONFIRM' to delete your account and all jobs.")
    else:
        st.error("You are not logged in. Please log in to delete your account.")
###################################################Job listing ###############################################

salary_options = ['RM0', '1K', '2K', '3K', '4K', '5K', '8K', '10K', '20K', '30K', '40K', '50K', '50+K']

def show_filtered_jobs():
    st.title("Job Listings")

    # Initialize or fetch the vectorizer and check if a resume TF-IDF is available
    if 'vectorizer' not in st.session_state:
        st.session_state['vectorizer'] = load_vectorizer()
    vectorizer = st.session_state['vectorizer']

    # UI setup for filters
    col1, col2, col3 = st.columns(3)
    with col1:
        job_category = st.selectbox("Category", ["Engineering", "Accounting", "Information-Technology"], key="filter_job_category")
    with col2:
        state = st.selectbox("State", [""] + collection.distinct("State"), key="filter_state")
    with col3:
        work_type = st.multiselect("Type", options=collection.distinct("WorkType"), key="filter_work_type")

    col4, col5 = st.columns(2)
    with col4:
        salary_options = ['RM0', '1K', '2K', '3K', '4K', '5K', '8K', '10K', '20K', '30K', '40K', '50K', '50+K']
        salary_from = st.selectbox("Salary From (Monthly)", salary_options, key="filter_salary_from")
    with col5:
        salary_to = st.selectbox("Salary To (Monthly)", salary_options, key="filter_salary_to", index=len(salary_options)-1)

    if salary_options.index(salary_from) >= salary_options.index(salary_to):
        st.error("Salary From must be less than Salary To.")
        return
    
    
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        filter_button = st.button("Filter Jobs")
    with btn_col2:
        compare_button = st.button("Find best Match")

    # Check which button was pressed and execute respective function
    if filter_button:
        display_filtered_jobs(job_category, state, work_type, salary_from, salary_to)
    if compare_button:
        query = build_query(job_category, state, work_type, salary_from, salary_to)
        filtered_jobs = list(collection.find(query))
        display_jobs(filtered_jobs, vectorizer)
    
    
   # col6, col7 = st.columns(2)
  #  with col6:
   #     if st.button("Filter Jobs"):
   #         display_filtered_jobs(job_category, state, work_type, salary_from, salary_to)
    #with col7:
   #     if st.button("Find Best Match"):
  #          query = build_query(job_category, state, work_type, salary_from, salary_to)
     #       filtered_jobs = list(collection.find(query))
    #        display_jobs(filtered_jobs, vectorizer)
            

def display_filtered_jobs(job_category, state, work_type, salary_from, salary_to):
    css = """
    <style>
        .no-info {
            font-style: italic;
            color: #ff0000;
        }

    </style>
    """ 
    st.markdown(css, unsafe_allow_html=True)
    if salary_options.index(salary_from) >= salary_options.index(salary_to):
        st.error("Salary From must be less than Salary To.")
        return

    query = construct_query(job_category, state, work_type, salary_from, salary_to)
    filtered_jobs = list(collection.find(query))
    if filtered_jobs:
        for job in filtered_jobs:
            display_job_details(job)
    else:
        st.markdown("<span class='no-info'>No jobs fulfill the selected requirements.</span>", unsafe_allow_html=True)
        
def construct_query(job_category, state, work_type, salary_from, salary_to):
    query = {}
    if job_category:
        query["Job Category"] = job_category
    if state:
        query["State"] = state
    if work_type:
        query["WorkType"] = {"$in": work_type}
    if salary_from and salary_to:
        salary_from_value = 0 if salary_from == 'RM0' else int(salary_from.strip('+K').strip('RM')) * 1000
        salary_to_value = int(salary_to.strip('+K').strip('RM')) * 1000 if salary_to != '50+K' else 100000
        query["Salary From"] = {"$gte": salary_from_value}
        query["Salary To"] = {"$lte": salary_to_value}
    return query     
def display_job_details(job, similarity=None):
    css = """
    <style>
        .header {
            font-size: 20px;
            font-weight: bold;
        }
        .content {
            font-size: 18px;
            margin-bottom: 5px;
            margin-left: 10px;
        }
        .info {
            font-style: italic;
            color: #ff0000;
        }
        .job-section {
            border-bottom: 2px solid #ccc;
            padding-bottom: 10px;
            margin-bottom: 10px;
        }
    </style>
    """ 
    st.markdown(css, unsafe_allow_html=True)
    st.markdown(f"<div class='job-section'>", unsafe_allow_html=True)
    st.subheader(f"{job['Job Title']} at {job['Business Name']}")
    if similarity is not None:
        st.metric(label="Similarity", value=f"{similarity:.2f}")
    with st.expander("See full job description"):
        st.markdown(f"<div class='content'>{job['Job Description']}</div>", unsafe_allow_html=True)

    st.markdown(f"<div class='header'>Job Category:</div><div class='content'>{job['Job Category']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='header'>Location:</div><div class='content'>{job['Address line']}, {job['Postcode']} {job['City']}, {job['State']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='header'>Work Type:</div><div class='content'>{job['WorkType']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='header'>Salary Range:</div><div class='content'>{job['Salary From']} to {job['Salary To']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='header'>Email:</div><div class='content'><a href='mailto:{job['Email']}'>{job['Email']}</a></div>", unsafe_allow_html=True)
    benefits = ", ".join(job.get('Benefit', [])) if job.get('Benefit', []) else "No benefits listed"
    st.markdown(f"<div class='header'>Benefits and Perks:</div><div class='content'>{benefits}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='header'>Company Size:</div><div class='content'>{job.get('CompanySize', 'Not specified')}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)  # Close job-section div

def build_query(job_category, state, work_type, salary_from, salary_to):
    query = {}
    if job_category:
        query["Job Category"] = job_category
    if state:
        query["State"] = state
    if work_type:
        query["WorkType"] = {"$in": work_type}
    salary_from_value = 0 if salary_from == 'RM0' else int(salary_from.strip('+K').strip('RM')) * 1000
    salary_to_value = int(salary_to.strip('+K').strip('RM')) * 1000 if salary_to != '50+K' else 100000
    query["Salary From"] = {"$gte": salary_from_value}
    query["Salary To"] = {"$lte": salary_to_value}
    return query

def display_jobs(filtered_jobs, vectorizer):
    css = """
    <style>
        .header {
            font-size: 20px;
            font-weight: bold;
        }
        .content {
            font-size: 16px;
            margin-left: 10px;
        }
        .no-info {
            color: #ff0000;
            font-style: italic;
        }
        .job-section {
            border-top: 2px solid #ccc;
            padding-top: 10px;
            margin-top: 10px;
        }
        .high-similarity {
            font-weight: bold;
            color: green;
        }
        .moderate-similarity {
            font-weight: bold;
            color: #00FFFF;
        }
        .low-similarity {
            font-weight: bold;
            color: red;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
    def get_similarity_class(similarity):
        if similarity < 0.1:
            return 'low-similarity'  # Assuming low-similarity is styled with red
        elif similarity < 0.3:
            return 'moderate-similarity'  # Assuming moderate-similarity is styled with blue
        else:
            return 'high-similarity' 
    if 'resume_tfidf' in st.session_state and filtered_jobs:
        job_descs = [process_text(job['Job Description']) for job in filtered_jobs]
        job_descs_tfidf = vectorizer.transform(job_descs)
        resume_tfidf = st.session_state['resume_tfidf']

        # Calculate cosine similarity
        cos_similarities = cosine_similarity(resume_tfidf, job_descs_tfidf).flatten()
        for index, job in enumerate(filtered_jobs):
            job['Cosine Similarity'] = cos_similarities[index]

        # Sort jobs by cosine similarity
        sorted_jobs = sorted(filtered_jobs, key=lambda x: x['Cosine Similarity'], reverse=True)
        for job in sorted_jobs:
            similarity_class = get_similarity_class(job['Cosine Similarity'])
            st.markdown(f"<div class='job-section'>", unsafe_allow_html=True)
            st.markdown(f"<h4>{job['Job Title']} at {job['Business Name']} (Similarity: <span class='{similarity_class}'>{job['Cosine Similarity']:.2f}</span>)</h4>", unsafe_allow_html=True)
            st.markdown(f"<div class='header'>Job Description:</div>", unsafe_allow_html=True)
            with st.expander("See full description"):
                st.write(f"{job['Job Description']}")
            
            st.markdown(f"<div class='header'>Job Category:</div><div class='content'>{job['Job Category']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='header'>Location:</div><div class='content'>{job['Address line']}, {job['Postcode']} {job['City']}, {job['State']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='header'>Work Type:</div><div class='content'>{job['WorkType']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='header'>Salary Range:</div><div class='content'>{job['Salary From']} to {job['Salary To']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='header'>Email:</div><div class='content'><a href='mailto:{job['Email']}'>{job['Email']}</a></div>", unsafe_allow_html=True)
            benefits = ", ".join(job.get('Benefit', [])) if job.get('Benefit', []) else "No benefits listed"
            st.markdown(f"<div class='header'>Benefits and Perks:</div><div class='content'>{benefits}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='header'>Company Size:</div><div class='content'>{job.get('CompanySize', 'Not specified')}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)  # Close job-section div
          #  st.write(f"**Contact Email:** {job['Email']}")
    else:
        st.markdown("<span class='no-info'>No resume uploaded or no jobs found matching the criteria.</span>", unsafe_allow_html=True)

        
 ###################################################Visualization####################################
def visualize_job_market():

    # Load and prepare data
    data = list(collection.find({}, {"Job Category": 1, "Salary From": 1, "Salary To": 1}))
    df = pd.DataFrame(data)
    df['Salary From'] = pd.to_numeric(df['Salary From'], errors='coerce')
    df['Salary To'] = pd.to_numeric(df['Salary To'], errors='coerce')
    df.dropna(inplace=True)  # Clean the data
    
    # Compute average salary
    df['Average Salary'] = df[['Salary From', 'Salary To']].mean(axis=1)
    summary_df = df.groupby('Job Category').agg({
        'Average Salary': 'mean',
        'Job Category': 'count'
    }).rename(columns={'Job Category': 'Count'}).reset_index()
    
    # Default to all categories for the pie chart
    all_categories = summary_df['Job Category'].unique()
    selected_categories = st.multiselect("Select Job Categories", options=all_categories, default=all_categories)
    filtered_data = summary_df[summary_df['Job Category'].isin(selected_categories)]
    
    # Allow user to choose which type of chart to display, default to Pie Chart
    chart_type = st.selectbox("Choose Chart Type", ['Pie Chart', 'Bar Chart'], index=0)
    
    # Bar chart for average salary comparison
    if chart_type == 'Bar Chart':
        fig_salary = px.bar(filtered_data, x='Job Category', y='Average Salary',
                            title="Average Salary Comparison by Job Category",
                            labels={"Average Salary": "Average Salary ($)"},
                            color_discrete_sequence=px.colors.sequential.Pinkyl)  # Pink-themed color sequence
        fig_salary.update_traces(hovertemplate="<b>%{x}</b><br>Average Salary: $%{y:.2f}")
        st.plotly_chart(fig_salary)
    
    # Pie chart for job listings distribution
    elif chart_type == 'Pie Chart':
        fig_count = px.pie(filtered_data, names='Job Category', values='Count',
                           title='Distribution of Job Listings by Job Category',
                           color_discrete_sequence=px.colors.sequential.Agsunset)  # Colorful theme
        fig_count.update_traces(textinfo='percent+label',
                                hovertemplate="<b>%{label}</b><br>%{value} listings (%{percent})")
        st.plotly_chart(fig_count)



def visualize_salary_distribution():

    # Fetch data directly from the globally defined MongoDB collection
    data = list(collection.find({}, {"Job Category": 1, "WorkType": 1, "Salary From": 1, "Salary To": 1}))
    
    if not data:
        st.error("No data available to display.")
        return
    
    df = pd.DataFrame(data)
    
    # Calculate average salary
    df['Average Salary'] = df[['Salary From', 'Salary To']].mean(axis=1)
    
    # Dynamic selection based on available data
    job_categories = df['Job Category'].unique()
    work_types = df['WorkType'].unique()

    selected_category = st.selectbox("Select Job Category", options=job_categories)
    default_work_types = work_types  # Select all available work types by default if they exist
    selected_work_types = st.multiselect("Select Work Types", options=work_types, default=default_work_types)

    # Filter data based on selections
    filtered_data = df[(df['Job Category'] == selected_category) & (df['WorkType'].isin(selected_work_types))]
    
    if filtered_data.empty:
        st.write("No data available for the selected filters. Please try different options.")
        return

    # Group by Work Type and calculate average salary for selected job category
    avg_salary_by_work_type = filtered_data.groupby('WorkType')['Average Salary'].mean().reset_index()

    # Plotting the results with a bright pink color theme
    fig = px.bar(avg_salary_by_work_type, x='WorkType', y='Average Salary',
                 title=f"Average Salaries for {selected_category}",
                 labels={"Average Salary": "Average Salary ($)"},
                 color_discrete_sequence=['#FF69B4'])  # Bright pink color theme

    # Customizing hover information to display two decimal places
    fig.update_traces(hovertemplate="<b>%{x}</b>: $%{y:.2f}")

    st.plotly_chart(fig)


def job_applications_by_state():
    # Fetch data from MongoDB
    data = list(collection.find({}, {"State": 1, "Job Category": 1, "Salary From": 1, "Salary To": 1}))
    df = pd.DataFrame(data)
    
    if df.empty:
        st.error("No data available to display.")
        return

    # Calculate the average salary from the salary range
    df['Average Salary'] = df[['Salary From', 'Salary To']].mean(axis=1)

    # Adding a category selection, including an "Overall" option
    job_categories = list(df['Job Category'].unique()) + ['Overall']
    selected_category = st.selectbox("Select Job Category", options=job_categories)

    # Filter data based on selected job category unless "Overall" is selected
    if selected_category != 'Overall':
        filtered_data = df[df['Job Category'] == selected_category]
    else:
        filtered_data = df

    # Counting job applications by state and calculate average salary for the tooltip
    state_summary = filtered_data.groupby('State').agg({'State': 'count', 'Average Salary': 'mean'}).rename(columns={'State': 'Number of Applications'}).reset_index()

    # Plotting the histogram
    fig = px.bar(state_summary, x='State', y='Number of Applications', title=f"Number of Applications and Average Salary in Each State for {selected_category}",
                 labels={'Number of Applications': 'Number of Applications', 'State': 'State'},
                 hover_data={'Average Salary': ':.2f'})
    fig.update_traces(hovertemplate="<b>%{x}</b><br>Number of Applications: %{y}<br>Average Salary: $%{customdata[0]:.2f}")
    st.plotly_chart(fig)





######################################################Main function ###############################
    
 
# Define the main function that will coordinate the navigation
def main():
    # Setup for the option menu with icons
    with st.sidebar:
        selected = option_menu(
            menu_title=None,  # Title of the menu
            options=["Job Seeker", "Employer", "Job Listings", "Visualization"],
            icons=["house", "building", "envelope", "bar-chart-line"],  # Corrected icons
            menu_icon="cast",  # Icon for the menu
            default_index=0,
            )

    # Page handling based on selected option from the menu
    if selected == "Job Seeker":
        job_seeker_page()
    elif selected == "Employer":
        # Check if the user is logged in before showing job listings
        if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
            login_page()  # Display login page if not logged in
            registration_page()  # Optionally allow registration from here
        else:
            employer_page()
    elif selected == "Job Listings":
        job_listings_page()
    elif selected == "Visualization":
        Analysis_page()
        
def job_seeker_page():
    css = """
    <style>
        /* Reduces padding around the main content area */
        .main .block-container {
           padding: 2rem 1rem;                    /* Adjust the padding as needed */
            max-width: 800px;                     /* Adjusts the maximum width of the central content area */
        }
        .big-font {
            font-size: 20px;
            text-align: justify;  /* Justify text */
            margin-bottom: 10px;  /* Adds spacing below each paragraph */
        }
        .section-space {
            margin-top: 20px;  /* Adds vertical space between sections */
        }
        .bold {
            font-weight: bold;  /* Makes text bold */
            }
    </style>
    """
# Inject CSS
    st.markdown(css, unsafe_allow_html=True)
    st.title("Welcome to Job matcher")
    image_path = "C:\\Users\\ongka\\Downloads\\JobMatcherIcon.png"

    # Display the image
    st.image(image_path, caption='Job Matcher Icon', width=500)

    
    st.markdown("""
    <div class="big-font">
        Our platform is designed to connect job seekers with outstanding opportunities in <span class="bold">engineering</span>, <span class="bold">accounting</span>, and <span class="bold">information technology</span>. By leveraging precise matching algorithms, we ensure that each candidate is paired with job openings that best suit their skills and career aspirations.
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("How It Works")
    st.markdown("""
    <div class="big-font">
    Upon uploading your resume in <span class="bold">PDF</span> format, our system analyzes your experience and skills. We process this information to match you with job listings that align with your professional qualifications.
    This intelligent matching saves you valuable time by filtering out unsuitable job positions, thereby enhancing your chances of finding the ideal role that fits your career goals.    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("Supported Fields")
    st.markdown("""
    <div class="big-font">
Currently, our service focuses exclusively on careers within <span class="bold">engineering</span>, <span class="bold">accounting</span>, and <span class="bold">information technology</span> sectors. This specialization ensures that our recommendations are relevant and valuable to your specific professional needs.
    """, unsafe_allow_html=True)
    if 'vectorizer' not in st.session_state:
        st.session_state['vectorizer'] = load_vectorizer()

    resume = st.file_uploader("Upload your resume", type=['pdf'], key="resume")

    # If the process button is clicked
    if st.button("Process"):
        if resume:
            try:
                # Clear previous PDF display if it exists
                if 'pdf_display' in st.session_state:
                    del st.session_state['pdf_display']

                # Convert resume to base64 for PDF display
                base64_pdf = base64.b64encode(resume.getvalue()).decode('utf-8')
                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)
                st.session_state['pdf_display'] = pdf_display  # Save the current PDF display

                # Reading and processing the resume
                resume_text = read_pdf_file(BytesIO(resume.getvalue()))
                processed_text = process_text(resume_text)
                tfidf_matrix = st.session_state['vectorizer'].transform([processed_text])
                st.session_state['resume_tfidf'] = tfidf_matrix

                # Load the model and predict
                model_filename = 'C:/Users/ongka/OneDrive/Desktop/FYP Spare/tuned_logistic_regression_model.pkl'
                with open(model_filename, 'rb') as file:
                    loaded_model = pickle.load(file)
                probabilities = loaded_model.predict_proba(tfidf_matrix)
                max_prob = max(probabilities[0])
                predicted_label = loaded_model.predict(tfidf_matrix)[0]

                # Extracting contact info
                emails, phones = extract_contact_info(resume_text)
                display_contact_info(emails, phones)
                display_job_category(max_prob, predicted_label)

                # Save the latest info for restoration
                st.session_state.update({
                    'emails': emails,
                    'phones': phones,
                    'max_prob': max_prob,
                    'predicted_label': predicted_label
                })

            except Exception as e:
                st.error(f"Failed to process files: {e}")
        else:
            st.error("Please upload a resume.")
    else:
        # Attempt to restore the display if data exists in session state
        if 'pdf_display' in st.session_state:
            st.markdown(st.session_state['pdf_display'], unsafe_allow_html=True)
            display_contact_info(st.session_state['emails'], st.session_state['phones'])
            display_job_category(st.session_state['max_prob'], st.session_state['predicted_label'])
        
def employer_page():
    st.title(f"Welcome {st.session_state.get('username', 'Guest')}!")
    if st.button('Logout'):
        logout()
    create_job_page()
    read_jobs()
    update_job()
    delete_job()
    delete_all_jobs()
    delete_account()

def job_listings_page():
    st.markdown("<div id='link_to_top'></div>", unsafe_allow_html=True)
    
    # Display the job listings or any other content
    show_filtered_jobs()
    
   # HTML and CSS for the back to top button
    back_to_top_html = """
    <a href="#link_to_top" style="
        position: fixed;
        bottom: 20px;
        right: 20px;
        cursor: pointer;
        background-color: grey;
        color: white;
        padding: 2px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        text-align: center;
        font-size: 30px;
        text-decoration: none;
        display: inline-block;
        transition: opacity 0.3s;">
        &#8679; <!-- Unicode character for an upward pointing arrow -->
    </a>
    """
    
    st.markdown(back_to_top_html, unsafe_allow_html=True)      

def Analysis_page():
    st.title("Visualisation")
    col1, col2 = st.columns(2)
 #   st.set_page_config(layout='wide', initial_sidebar_state="expanded")

# Display the first visualization in the first column
    with col1:
        st.header("Distribution/average salary per category")
        visualize_job_market()

# Display the second visualization in the second column
    with col2:
        st.header("Salary Distribution by work types")
        visualize_salary_distribution()
    st.header("Average Salary in each states")
    job_applications_by_state()
if __name__ == "__main__":
    main()