from fasthtml.common import *
from database import db 

app = FastHTML()

def get_all_tasks():
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, description, complete FROM tasks ORDER BY id DESC")
        return cursor.fetchall()

def render_task(task):
    """Helper function to render a single task"""
    return Li(
        Div(
            Div(
                Input(
                    type="checkbox",
                    checked=bool(task['complete']),
                    hx_post=f"/toggle-task/{task['id']}",
                    hx_target=f"#task-{task['id']}",
                    hx_swap="outerHTML",
                    cls="w-5 h-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                ),
                Span(
                    task['description'],
                    cls=f"text-lg {'line-through text-gray-400' if task['complete'] else 'text-gray-800'}"
                ),
                cls="flex items-center gap-3 flex-1"
            ),
            Button(
                "Delete",
                hx_delete=f"/delete-task/{task['id']}", 
                hx_target="closest li",
                hx_swap="outerHTML",
                hx_confirm="Are you sure you want to delete this task?",
                cls="px-4 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors duration-200"
            ),
            cls="flex items-center justify-between gap-4"
        ),
        cls="bg-white p-4 rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200 border border-gray-100",
        id=f"task-{task['id']}"
    )

@app.get('/')
def home():
    tasks_data = get_all_tasks()
    completed_count = sum(1 for task in tasks_data if task['complete'])
    total_count = len(tasks_data)
    
    return Html(
        Head(
            Title('My To-Do List'),
            Script(src="https://unpkg.com/htmx.org@1.9.10"),
            Script(src="https://cdn.tailwindcss.com"),
            Style("""
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
                body { font-family: 'Inter', sans-serif; }
            """)
        ),
        Body(
            Div(
                # Header Section
                Div(
                    Div(
                        H1("✨ My Tasks", cls="text-4xl font-bold text-gray-800"),
                        P(
                            f"{completed_count} of {total_count} tasks completed",
                            cls="text-gray-500 mt-2"
                        ),
                        cls="mb-8"
                    ),
                    
                    # Add Task Form
                    Form(
                        Div(
                            Input(
                                type='text',
                                name='description', 
                                placeholder='What needs to be done?', 
                                required=True, 
                                id="task-input",
                                cls="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-lg"
                            ),
                            Button(
                                "Add Task",
                                type="submit",
                                cls="px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors duration-200 shadow-sm hover:shadow-md"
                            ),
                            cls="flex gap-3"
                        ),
                        hx_post="/add-task", 
                        hx_target="#task-list",
                        hx_swap="afterbegin",
                        hx_on__after_request="document.getElementById('task-input').value = ''",
                        cls="mb-8"
                    ),
                    
                    # Tasks List
                    Div(
                        Ul(
                            *[render_task(task) for task in tasks_data] if tasks_data else [
                                Li(
                                    Div(
                                        P("🎉 No tasks yet! Add one above to get started.", 
                                          cls="text-gray-400 text-center text-lg"),
                                        cls="py-12"
                                    ),
                                    cls="bg-gray-50 rounded-lg"
                                )
                            ],
                            id="task-list",
                            cls="space-y-3"
                        ),
                    ),
                    
                    cls="max-w-3xl mx-auto bg-white rounded-2xl shadow-lg p-8"
                ),
                cls="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 py-12 px-4"
            )
        )
    )

@app.post("/add-task")
async def add_task(description: str = Form(...)):
    description = description.strip()
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (description, complete) VALUES (?, ?)", 
            (description, 0)
        )
        conn.commit()
        
        new_id = cursor.lastrowid
        cursor.execute(
            "SELECT id, description, complete FROM tasks WHERE id = ?",
            (new_id,)
        )
        new_task = cursor.fetchone()
    
    if new_task:
        return render_task(new_task)
    return ""

@app.post("/toggle-task/{task_id}")
def toggle_task(task_id: int):
    with db.get_connection() as conn:
        cursor = conn.cursor()
        # Toggle the complete status
        cursor.execute(
            "UPDATE tasks SET complete = 1 - complete WHERE id = ?",
            (task_id,)
        )
        conn.commit()
        
        # Fetch the updated task
        cursor.execute(
            "SELECT id, description, complete FROM tasks WHERE id = ?",
            (task_id,)
        )
        task = cursor.fetchone()
    
    if task:
        return render_task(task)
    return ""

@app.delete("/delete-task/{task_id}")
def delete_task(task_id: int):
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
    return ""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)