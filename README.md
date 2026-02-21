AI-Driven Job Matching & Market Analytics Platform (FYP)
📌 Project Vision
Traditional recruitment systems prioritize employers, often leaving job seekers overwhelmed by irrelevant listings and high rejection rates. This Candidate-Centric platform reverses the power dynamic—allowing job seekers to upload their resumes and instantly receive a ranked list of job openings based on AI-calculated compatibility before they even apply.

⚙️ Technical System Workflow
The system follows a rigorous Natural Language Processing (NLP) Pipeline to transform raw, unstructured text into actionable matching scores.

Automated Extraction: Uses pdfplumber and Regex to capture contact info (Email, Phone) and candidate names from PDF uploads.

Semantic Preprocessing: Implemented spaCy for Named Entity Recognition (NER) to identify key professional attributes and standardized text via lemmatization and stop-word removal.

Vectorization (TF-IDF): Converts resumes and job descriptions into a weighted vector space model to quantify term importance.

Job Type Prediction: Features a Fine-tuned Logistic Regression model (stored as .pkl) to automatically categorize resumes into specific industries.

Dynamic Ranking (Cosine Similarity): Measures the angular distance between vectors to provide the "Best Match" ranking.

##🗄️ Database & Security
NoSQL Architecture: Utilized MongoDB for its schema flexibility, ideal for handling diverse and unstructured job descriptions.

Data Security: Implemented bcrypt for password hashing to ensure employer credential integrity.
