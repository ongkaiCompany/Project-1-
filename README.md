📌 Project Vision <br />
Traditional recruitment systems prioritize employers, often leaving job seekers overwhelmed by irrelevant listings and high rejection rates. This Candidate-Centric platform reverses the power dynamic—allowing job seekers to upload their resumes and instantly receive a ranked list of job openings based on AI-calculated compatibility before they even apply.
<br />
<br />
⚙️ Technical System Workflow<br />
The system follows a rigorous Natural Language Processing (NLP) Pipeline to transform raw, unstructured text into actionable matching scores.

1）Automated Extraction: Uses pdfplumber and Regex to capture contact info (Email, Phone) and candidate names from PDF uploads.

2）Semantic Preprocessing: Implemented spaCy for Named Entity Recognition (NER) to identify key professional attributes and standardized text via lemmatization and stop-word removal.

3）Vectorization (TF-IDF): Converts resumes and job descriptions into a weighted vector space model to quantify term importance.

4）Job Type Prediction: Features a Fine-tuned Logistic Regression model (stored as .pkl) to automatically categorize resumes into specific industries.

5）Dynamic Ranking (Cosine Similarity): Measures the angular distance between vectors to provide the "Best Match" ranking.
<br />
<br />
🛠️ Key Features
<br />
1. Dual-Portal Interface (Streamlit)<br />
Employer Portal: A secure environment with full CRUD capabilities (Create, Read, Update, Delete) for managing job postings and account settings.<br />
Job Seeker Portal: A "no-login-required" interface designed for speed, allowing instant resume-to-job matching.

2. Multi-Criteria Filtering<br />
Beyond AI ranking, users can refine searches using:
  i) Hard Filters: Location, Work Type, Salary Range, and Tags.<br />
  ii) Smart Ranking: The 'Find Best Match' button, which triggers the Cosine Similarity engine to re-order filtered results.<br />

3. Interactive Market Analytics<br />
A dynamic dashboard that translates MongoDB data into visual insights:<br />
i)Bar & Pie Charts: Distribution of jobs by category and type.<br />
ii)Hiring Trends: Line graphs tracking posting frequency to identify market gaps.<br />
<br />
<br />
🗄️ Database & Security
<br />
NoSQL Architecture: Utilized MongoDB for its schema flexibility, ideal for handling diverse and unstructured job descriptions.<br />

Data Security: Implemented bcrypt for password hashing to ensure employer credential integrity.
