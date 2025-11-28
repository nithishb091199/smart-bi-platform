
 
🧠 Smart BI Platform
An end-to-end, containerized business intelligence platform featuring:
•	PostgreSQL (database), FastAPI (backend analytics API), Streamlit (interactive dashboard)
•	Full Docker orchestration for local and cloud portability
•	Realistic synthetic business data and advanced SQL analytics
 
🚀 Table of Contents
•	Overview
•	Features
•	Tech Stack
•	Project Structure
•	Setup Instructions
o	Local (dev)
o	Docker Compose (recommended)
•	API Documentation
•	Dashboard
•	Data Generation
•	Screenshots
•	Deployment
•	Contributing
•	License
•	Contact
•	Future Improvements
 
📊 Overview
Smart BI Platform is a modern business intelligence stack built to showcase developer skills in:
•	Data engineering
•	Advanced SQL analytics
•	API development
•	Interactive dashboarding
•	DevOps (Docker)
This platform is portfolio-ready and suitable for technical demos, job performance showcases, and scalable production analytics.
 
💡 Features
•	Complete Data Model: 10+ normalized tables covering departments, employees, products, customers, sales, transactions, and more
•	Advanced Analytics SQL: CTEs, window functions, cohort analysis, RFM segmentation, leaderboards, year-over-year comparisons, product/category breakdowns
•	RESTful FastAPI Backend: 8+ endpoints, schema-validated responses, query parameters, CORS enabled
•	Professional Streamlit Dashboard: Multi-page analytics, Plotly charts, KPI cards, departments/products/customer views
•	Synthetic Data Generator: 10,000+ rows of realistic sample business records using Faker
•	Fully Containerized: PostgreSQL, FastAPI, and Streamlit in separate Docker containers, orchestrated with Docker Compose
•	Cloud/Dev Ready: True environment variable management (.env, Docker Compose, cloud-ready)
 

🛠 Tech Stack
•	Database: PostgreSQL 15.x (containerized)
•	Backend API: FastAPI (Python 3.11+)
•	Dashboard: Streamlit (Python 3.11+)
•	Data Generation: Python, Pandas, Faker, SQLAlchemy
•	DevOps: Docker, Docker Compose
•	Other: dotenv, CORS, Plotly
 
📁 Project Structure
smart-bi-platform/
├── api/                  # FastAPI backend source code
├── dashboard/            # Streamlit dashboard source code
├── database/             # Schema SQL, connection, models
├── scripts/              # Data generation & analytics scripts
├── Dockerfile.api        # Dockerfile for FastAPI backend
├── Dockerfile.streamlit  # Dockerfile for Streamlit dashboard
├── docker-compose.yml    # Multiservice orchestration
├── .env                  # Environment variables (LOCAL only)
├── .env.example          # Example env file for sharing
├── requirements.txt      # Python dependencies
└── README.md             # This documentation

 
👨‍💻 Setup Instructions
Local Dev Setup
1.	Install requirements
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

2.	Create and set up PostgreSQL locally (optional, recommended to use Docker)
3.	Create .env file in root (refer .env.example)
4.	Run database and API
python database/connection.py  # test connection
uvicorn api.main:app --reload  # start FastAPI backend

5.	Generate synthetic data
python scripts/generate_data.py

6.	Run dashboard
cd dashboard
streamlit run dashboard.py

Docker Deployment (Recommended)
1.	Build and start all containers
docker-compose up --build

2.	Initialize your database schema
docker exec -it smart-bi-platform-db-1 psql -U bi_admin -d business_intelligence -f /tmp/schema.sql

(or copy and run locally)
3.	Generate business data
o	Run python scripts/generate_data.py from your host (with Docker DB running)
4.	Access services
o	FastAPI: http://localhost:8000
o	Docs: http://localhost:8000/docs
o	Dashboard: http://localhost:8501
 
📑 API Docs
Swagger UI (browse):
•	http://localhost:8000/docs
•	Endpoints include:
o	/health
o	/tables
o	/summary
o	/analytics/employees/salary
o	/analytics/sales/monthly
o	/analytics/customers/rfm
o	/analytics/products/top
o	/analytics/departments
•	Query params for limits, filters
 
📊 Dashboard
•	Interactive analytics via Streamlit
•	Multi-page navigation (sidebar)
•	Visualizations powered by Plotly (bar, line, box, treemap, pie, KPI cards)
•	Real-time queries against the FastAPI backend
 
⚡ Data Generation
Synthetic data is created using scripts/generate_data.py:
•	Departments, Employees, Products, Customers, Sales, Transactions
•	Uses Faker for randomized, realistic data
•	Populates >10,000 sample records with revenue, churn, activity dates
 
🖼️ Screenshots
 
🌐 Deployment
Cloud Ready:
•	Works on any Docker-enabled host (AWS ECS, Azure, Google Cloud Run, Heroku Docker, DigitalOcean, etc.)
•	Configure secrets/env vars in cloud dashboard
•	Set up automated build/deploy with GitHub Actions or other CI/CD
•	Use docker-compose.yaml for multi-service orchestration
 
🤝 Contributing
•	Fork the repo and make pull requests!
•	Open issues for bug reports, requests
•	Follow clean code and commit conventions
 
📄 License

 
✉️ Contact
Author: Nithish B
Email: nithishb091199@gmail.com
GitHub: https://github.com/nithishb091199
 
💡 Future Improvements
•	User authentication & roles (JWT)
•	Real-time dashboards (WebSocket)
•	ML-powered prediction endpoints (churn, LTV, forecasts)
•	Automated seed/migration scripts in container entrypoints
•	Advanced filtering/pagination in dashboard
•	Custom analytic modules by user/role
•	Automated CI/CD for cloud deployment
 
   
