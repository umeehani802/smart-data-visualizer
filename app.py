from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
from markupsafe import Markup
import pandas as pd
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import uuid

app = Flask(__name__)
app.secret_key = 'your_super_secret_key_which_is_very_secret'
app.config['UPLOAD_FOLDER'] = 'uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
if not os.path.exists('static'):
    os.makedirs('static')

# SERVER-SIDE STORAGE
USER_DATA = {}

# ROBUST get_user_id FUNCTION
def get_user_id():
    if 'user_id' not in session:
        user_id = str(uuid.uuid4())
        session['user_id'] = user_id
    user_id = session['user_id']
    if user_id not in USER_DATA:
        USER_DATA[user_id] = {'visuals': []}
    return user_id

@app.route('/')
def home():
    get_user_id()
    return render_template('index.html')

# --- MODIFIED ROUTE ---
# This single route now handles both displaying the upload page (GET)
# and processing the uploaded file (POST).
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    # This block handles the form submission
    if request.method == 'POST':
        user_id = get_user_id()
        file = request.files.get('file')
        if file and file.filename.endswith('.csv'):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            USER_DATA[user_id]['filepath'] = filepath
            USER_DATA[user_id]['visuals'] = []
            return redirect(url_for('options_page'))
        else:
            flash('Please upload a valid CSV file.', 'error')
            # On error, redirect back to the upload page itself
            return redirect(url_for('upload'))
    
    # This line handles the page load for a GET request (e.g., from your "Back" button)
    return render_template('upload.html')


@app.route('/options')
def options_page():
    user_id = get_user_id()
    # Updated redirect
    if 'filepath' not in USER_DATA.get(user_id, {}): return redirect(url_for('upload'))
    visuals_count = len(USER_DATA[user_id]['visuals'])
    return render_template('options.html', visuals_count=visuals_count)

@app.route('/summary')
def summary():
    user_id = get_user_id()
    # Updated redirect
    if 'filepath' not in USER_DATA.get(user_id, {}): return redirect(url_for('upload'))
    df = pd.read_csv(USER_DATA[user_id]['filepath'])
    buffer = io.StringIO(); df.info(buf=buffer); info_output = buffer.getvalue()
    describe_table = Markup(df.describe(include='all').to_html(classes='styled-table', index=True, border=0))
    return render_template('summary.html', info_output=info_output, describe_table=describe_table)


@app.route('/download_summary')
def download_summary():
    user_id = get_user_id()
    # Updated redirect
    if 'filepath' not in USER_DATA.get(user_id, {}):
        return redirect(url_for('upload'))

    df = pd.read_csv(USER_DATA[user_id]['filepath'])
    
    # Create the summary text string
    buffer = io.StringIO()
    df.info(buf=buffer)
    info_output = buffer.getvalue()
    describe_output = df.describe(include='all').to_string()
    summary_text = f"--- Dataset Info ---\n\n{info_output}\n\n--- Descriptive Statistics ---\n\n{describe_output}"
    
    # Create an in-memory text file
    output_buffer = io.BytesIO(summary_text.encode('utf-8'))
    output_buffer.seek(0)
    
    # Send the file to the user
    return send_file(output_buffer, 
                     as_attachment=True, 
                     download_name='summary.txt', 
                     mimetype='text/plain')
# ----------------------------------------------------

@app.route('/clean_data', methods=['POST'])
def clean_data():
    user_id = get_user_id()
    # Updated redirect
    if 'filepath' not in USER_DATA.get(user_id, {}): return redirect(url_for('upload'))
    df = pd.read_csv(USER_DATA[user_id]['filepath']); action = request.form.get('action'); rows_before = len(df)
    if action == 'drop_na':
        df.dropna(inplace=True)
        flash(f"Success! Removed {rows_before - len(df)} row(s).", 'success')
    elif action == 'drop_duplicates':
        df.drop_duplicates(inplace=True)
        flash(f"Success! Removed {rows_before - len(df)} duplicate row(s).", 'success')
    df.to_csv(USER_DATA[user_id]['filepath'], index=False)
    return redirect(url_for('options_page'))

@app.route('/visualize', methods=['GET', 'POST'])
def visualize():
    user_id = get_user_id()
    # Updated redirect
    if 'filepath' not in USER_DATA.get(user_id, {}): return redirect(url_for('upload'))
    df = pd.read_csv(USER_DATA[user_id]['filepath']); columns = df.columns.tolist()
    visuals_count = len(USER_DATA[user_id]['visuals'])

    if request.method == 'POST':
        if request.form.get('action') == 'add_to_report':
            title = request.form.get('title'); plot_url = request.form.get('plot_url')
            USER_DATA[user_id]['visuals'].append({'title': title, 'plot_url': plot_url})
            report_url = url_for('report')
            flash(Markup(f"Chart '{title}' added! <a href='{report_url}' class='flash-link'>View Report</a>"), 'success')
            return redirect(url_for('visualize'))
        else:
            try:
                chart_type = request.form.get('chart_type'); x_col = request.form.get('x_column'); y_col = request.form.get('y_column')
                chart_title = request.form.get('chart_title'); hue_col = request.form.get('hue_column')
                if not chart_type or not y_col: return render_template('visualize.html', columns=columns, error="Please select a Chart Type and a primary (Y) column.", visuals_count=visuals_count)
                sns.set_style("whitegrid"); plt.figure(figsize=(12, 7)); plot_kwargs = {'data': df, 'x': x_col, 'y': y_col}
                if hue_col: plot_kwargs['hue'] = hue_col
                if chart_type == 'histogram': sns.histplot(data=df, x=y_col, hue=hue_col if hue_col else None, kde=True, multiple="stack")
                elif chart_type == 'pie': df[y_col].value_counts().plot.pie(autopct='%1.1f%%', startangle=90, figsize=(8,8)); plt.ylabel('')
                else:
                    if chart_type == 'bar': sns.barplot(**plot_kwargs)
                    elif chart_type == 'line': sns.lineplot(**plot_kwargs)
                    elif chart_type == 'scatter': sns.scatterplot(**plot_kwargs)
                    elif chart_type == 'box': sns.boxplot(**plot_kwargs)
                final_title = chart_title if chart_title else (f'{chart_type.title()} of {y_col}' if chart_type in ['histogram', 'pie'] else f'{chart_type.title()} of {y_col} by {x_col}')
                if not chart_title and hue_col and chart_type != 'pie': final_title += f' (colored by {hue_col})'
                plt.title(final_title, fontsize=18); plt.xticks(rotation=45, ha="right"); plt.tight_layout()
                img = io.BytesIO(); plt.savefig(img, format='png', bbox_inches='tight'); img.seek(0)
                preview_plot_url = base64.b64encode(img.getvalue()).decode('utf8'); plt.close()
                return render_template('visualize.html', columns=columns, visuals_count=visuals_count, plot_url_preview=preview_plot_url, chart_title_preview=final_title)
            except Exception as e:
                return render_template('visualize.html', columns=columns, error=f"An error occurred: {e}", visuals_count=visuals_count)
    return render_template('visualize.html', columns=columns, visuals_count=visuals_count)

@app.route('/report')
def report():
    user_id = get_user_id()
    # Updated redirect
    if 'filepath' not in USER_DATA.get(user_id, {}): return redirect(url_for('upload'))
    df = pd.read_csv(USER_DATA[user_id]['filepath']); buffer = io.StringIO(); df.info(buf=buffer); info_output = buffer.getvalue()
    describe_table = Markup(df.describe(include='all').to_html(classes='styled-table', index=True, border=0))
    visuals = USER_DATA[user_id]['visuals']
    return render_template('report.html', info_output=info_output, describe_table=describe_table, visuals=visuals)

@app.route('/download_report')
def download_report():
    user_id = get_user_id()
    # Updated redirect
    if 'filepath' not in USER_DATA.get(user_id, {}): return redirect(url_for('upload'))
    df = pd.read_csv(USER_DATA[user_id]['filepath']); buffer = io.StringIO(); df.info(buf=buffer); info_output = buffer.getvalue()
    describe_table = Markup(df.describe(include='all').to_html(classes='styled-table', index=True, border=0))
    visuals = USER_DATA[user_id]['visuals']
    html_string = render_template('report.html', info_output=info_output, describe_table=describe_table, visuals=visuals, is_download=True)
    output_buffer = io.BytesIO(html_string.encode('utf-8')); output_buffer.seek(0)
    return send_file(output_buffer, as_attachment=True, download_name='analysis_report.html', mimetype='text/html')

@app.route('/clear_report')
def clear_report():
    user_id = get_user_id()
    if user_id in USER_DATA:
        USER_DATA[user_id]['visuals'] = []
    flash('Report cleared. You can start creating new visuals.', 'success')
    return redirect(url_for('options_page'))

if __name__ == '__main__':
    app.run(debug=True)