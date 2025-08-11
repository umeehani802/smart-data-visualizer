# Smart Data Visualizer

A web app that allows users to upload datasets and visualize data interactively.  
Built with Python (Flask), HTML/CSS/JS frontend, and supports CSV data uploads.

---

## Features

- Upload CSV datasets for analysis
- Interactive data visualizations and reports
- Multiple visualization options
- Summary statistics and data previews
- Clean and responsive UI

---

## Technologies Used

- Python 3.x
- Flask (web framework)
- HTML5, CSS3, JavaScript
- Bootstrap (optional, if used)
- Pandas, Matplotlib / Plotly (for data processing & visualization)
- Jinja2 templating engine

---

## Setup and Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/umeehani802/smart-data-visualizer.git
   Create and activate a virtual environment (optional but recommended):

bash
Copy
Edit
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
Install required packages:

bash
Copy
Edit
pip install -r requirements.txt
Run the Flask app:

bash
Copy
Edit
python app.py
Open your browser and navigate to:
http://127.0.0.1:5000/

Usage
Use the web interface to upload your CSV dataset.

Navigate through different visualization options.

View summary statistics and detailed reports.

Download or save visualizations if enabled.

Project Structure
smart-data-visualizer/
│
├── app.py                   # Main Flask application
├── requirements.txt         # Python dependencies
├── netflix_titles.csv       # Sample dataset
├── uploads/                 # Folder for uploaded CSV files
├── static/                  # Static files (CSS, JS, images)
├── templates/               # HTML templates (Jinja2)
└── README.md                # Project README


Contact
For any questions, contact: umehanictds487@gmail.com

