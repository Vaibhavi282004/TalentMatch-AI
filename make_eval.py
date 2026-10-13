"""Creates a small synthetic labeled test set in eval/ (run once)."""
import os

JDS = {
    "python_dev": "Python backend developer. Must know Python, Django or Flask, REST API, SQL, git. Build and maintain backend services and APIs. Experience with docker and aws is a plus.",
    "data_analyst": "Data analyst. Must know SQL, Excel, Python, pandas, data analysis, power bi or tableau. Build dashboards, clean data and present insights to business teams.",
    "web_dev": "Frontend web developer. Must know HTML, CSS, JavaScript, React. Build responsive websites and user interfaces. Experience with git and REST API integration is a plus.",
}

# text, labels for (python_dev, data_analyst, web_dev); 1 = real fit
RESUMES = {
    "r1": ("Backend developer. Built REST API projects with Python and Django using SQL and mysql. Used git and docker. Deployed a Django app on aws.", (1, 0, 0)),
    "r2": ("Data analyst. Skilled in SQL, Excel, Python, pandas and power bi. Built sales dashboards, cleaned large datasets and did data analysis for business reporting.", (0, 1, 0)),
    "r3": ("Frontend developer. Built responsive websites with HTML, CSS, JavaScript and React. Used git and consumed REST API data in user interfaces.", (0, 0, 1)),
    "r4": ("Full stack developer. Django and Python backend with REST API and SQL, plus React, JavaScript, HTML and CSS frontend. Used git and docker.", (1, 0, 1)),
    "r5": ("Machine learning student. Python, pandas, numpy, scikit-learn, nlp and tensorflow. Built sentiment analysis and prediction models. Data analysis in notebooks.", (0, 1, 0)),
    "r6": ("Java developer. Spring Boot microservices, Java, Oracle database, Maven and Jenkins. Built enterprise banking applications.", (0, 0, 0)),
    "r7": ("Mechanical engineer. AutoCAD, SolidWorks, thermodynamics, machine design and manufacturing processes. Worked on assembly line optimisation.", (0, 0, 0)),
    "r8": ("Sales and marketing executive. Lead generation, client relationships, social media campaigns, negotiation and market research.", (0, 0, 0)),
    "r9": ("Reporting analyst. Advanced Excel, SQL queries, tableau dashboards and monthly MIS reports. Data analysis for finance and operations teams.", (0, 1, 0)),
    "r10": ("Website designer. WordPress, PHP, HTML and CSS themes, basic JavaScript, responsive layouts for small business sites.", (0, 0, 1)),
    "r11": ("QA tester. Manual testing, basic Python scripts, test cases, bug reports and Selenium basics. Familiar with git.", (0, 0, 0)),
    "r12": ("Backend engineer. Python, Flask, REST API design, SQL, mysql and git. Containerised services with docker.", (1, 0, 0)),
}

os.makedirs("eval/jds", exist_ok=True)
os.makedirs("eval/resumes", exist_ok=True)
for name, text in JDS.items():
    open(f"eval/jds/{name}.txt", "w", encoding="utf-8").write(text)

rows = ["resume_path,jd_path,label"]
for rname, (text, labels) in RESUMES.items():
    open(f"eval/resumes/{rname}.txt", "w", encoding="utf-8").write(text)
    for jd, label in zip(JDS, labels):
        rows.append(f"eval/resumes/{rname}.txt,eval/jds/{jd}.txt,{label}")
open("eval/pairs.csv", "w", encoding="utf-8").write("\n".join(rows))
print("Created", len(rows) - 1, "pairs. Note: this set is synthetic and easy.")
