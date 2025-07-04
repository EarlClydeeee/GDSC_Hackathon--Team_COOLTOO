# GDSC_Hackathon--Team_COOLTOO

GDSC Hackathon 2024 Submission – Team COOLTOO

S.I.G.A.L.A (Smart Integrated Geo-Alert and Legal Assistance) is a web-based incident reporting and scheduling system designed to empower communities and barangay officials by streamlining local issue reporting and resolution.

## Problem Statement
In many communities, incident reporting remains manual, fragmented, or poorly documented. Residents often do not know how to escalate issues effectively, while barangay officials face difficulty in managing, prioritizing, and responding to concerns efficiently.

## Our Solution

S.I.G.A.L.A. provides a centralized, intelligent platform where:
- Citizens can **report incidents** with a simple form.
- An **AI classifier** automatically categorizes the report based on urgency.
– A **chatbot** that answers common questions regarding the establishment and government policies.
– Barangay officials receive **report signals** (unfinished) based on urgency and type.
- Data is stored in a database for future reference and transparency.

## Features
- 📝 **Incident Reporting Form** – Simple and accessible form for citizens.
- 🧠 **AI-Powered Classifier** – Automatically determines the incident urgency category.
- 🗨️ **Chatbot for Legal Assistance** – Lets users enquire common questions.
- 🗓️ **Appointment Scheduler** – Enables citizens to create an appointment before visiting barangay establishments.
- 📊 **Database Logging** – Tracks reports and responses securely.
- 🌐 **Web-Based Interface** – Built with Flask (Python) for ease of deployment.

## Tech Stack
| Component        | Technology           |
|------------------|----------------------|
| Backend          | Python (Flask)       |
| Frontend         | HTML, CSS, JavaScript |
| AI Classifier    | gemini wrapper |
| Chatbot for legal assistance | TogetherAI wrapper |
| Database         | MySQL |
| Deployment       | Local |


# How to Run The Flask App

---

Ensure you have the following installed:
- **Python** (version 3.7 or higher)
- **pip** (Python package manager)
- **Flask** (installed via pip)

---

## Instructions

### 1. Clone the Repository
If you haven't already, clone the project repository to your local machine.
```bash
git clone https://github.com/RenzArcilla/GDSC_Hackathon--Team_COOLTOO
```

### 2. Navigate to the Project Directory
Open your terminal and navigate to the `GDSC_Hackathon--Team_COOLTOO` directory:
```bash
cd GDSC_Hackathon--Team_COOLTOO
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Flask DotEnv
```bash
cd GDSC_Hackathon--Team_COOLTOO
touch .flaskenv
```
- Add Environment Variables to .flaskenv Open the file in your favorite text editor (e.g., nano, vim, or code) and add the following content:
```
TOGETHER_API_KEY=
TOGETHER_MODEL=
GOOGLE_API_KEY=
ADMIN_ID=
```
### 5. Run Flask
```bash
cd GDSC_Hackathon--Team_COOLTOO
flask run
```
