import os
import json
from datetime import datetime, timezone
from fpdf import FPDF
from fetch_and_save import fetch_and_save_data

# Constants
REPORTS_DIR = "data/"  # Save reports in the data directory

def merge_tasks_with_cases(tasks, cases):
    """Attach case names to tasks based on case ID."""
    case_lookup = {str(case["id"]): case.get("name", "Unknown Case") for case in cases}

    for task in tasks:
        case_id = str(task.get("case", {}).get("id", "MISSING"))
        task["case_name"] = case_lookup.get(case_id, "No Case Assigned")

    return tasks

def fetch_tasks():
    """Fetch and merge tasks with case names."""
    tasks = fetch_and_save_data("v1", "tasks")
    cases = fetch_and_save_data("v1", "cases")

    # Filter for incomplete tasks and merge with case names
    tasks = [t for t in tasks if t.get("due_date") and not t.get("completed", False)]
    tasks = merge_tasks_with_cases(tasks, cases)

    # Sort tasks by due date (latest first)
    tasks.sort(key=lambda x: x["due_date"], reverse=True)
    
    return tasks

### **PDF Generation Functions** ###
def initialize_pdf():
    """Initialize the PDF document with settings."""
    pdf = FPDF(orientation="L")  # Landscape mode
    pdf.set_auto_page_break(auto=True, margin=15)
    return pdf

def add_page_with_headers(pdf, width, height, first_page=False):
    """Adds a new page and prints table headers."""
    if not first_page:  # Don't add a new page after the title
        pdf.add_page()
    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(width[0], height, "Task Name", border=1)
    pdf.cell(width[1], height, "Case Name", border=1)
    pdf.cell(width[2], height, "Due Date", border=1)
    pdf.ln()
    pdf.set_font("Arial", size=12)

def render_task_row(pdf, task, width):
    """Renders a single task row, ensuring it fits on the page."""
    task_name = task.get("name", "N/A")
    case_name = task.get("case_name", "No Case Assigned")
    due_date = task.get("due_date", "N/A")

    # Calculate number of lines needed for each field
    num_lines_task = max(1, pdf.get_string_width(task_name) // width[0] + 1)
    num_lines_case = max(1, pdf.get_string_width(case_name) // width[1] + 1)

    # Determine the required row height
    height = 10 * max(num_lines_task, num_lines_case)

    # Check if the row fits on the page, otherwise add a new page
    if pdf.y + height > pdf.page_break_trigger:
        add_page_with_headers(pdf, width, 10, first_page=False)

    # Handle Task Name column (MultiCell if needed)
    top = pdf.y
    offset = pdf.x + width[0]
    if num_lines_task == 1:
        pdf.cell(width[0], height, task_name, border=1)
    else:
        pdf.multi_cell(width[0], 10, task_name, border=1)
        pdf.y = top  # Reset Y to ensure proper alignment
        pdf.x = offset

    # Handle Case Name & Due Date (Aligned with max height)
    if num_lines_case == 1:
        pdf.cell(width[1], height, case_name, border=1)
    else:
        pdf.multi_cell(width[1], 10, case_name, border=1)
        pdf.y = top
        pdf.x += width[1]

    pdf.cell(width[2], height, due_date, border=1, ln=True)

def generate_pdf(tasks):
    """Generate a landscape PDF report of incomplete tasks with case names."""
    os.makedirs(REPORTS_DIR, exist_ok=True)
    pdf = initialize_pdf()
    pdf.add_page()

    # Title
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(250, 10, "Incomplete Tasks with Case Names", ln=True, align="C")
    pdf.ln(10)

    width = [120, 120, 30]  # Column widths

    # Add headers **without adding an extra page**
    add_page_with_headers(pdf, width, 10, first_page=True)

    # Render each task row
    for task in tasks:
        render_task_row(pdf, task, width)

    # Save the PDF
    filename = os.path.join(REPORTS_DIR, f"tasks_{datetime.now(timezone.utc).strftime('%Y%m%d')}.pdf")
    pdf.output(filename)
    print(f"PDF generated: {filename}")

def main():
    """Main function to fetch tasks, merge with cases, and generate a PDF."""
    tasks = fetch_tasks()
    if tasks:
        generate_pdf(tasks)
    else:
        print("No tasks found.")

if __name__ == "__main__":
    main()
