from app.models import AgentState
import re

def get_timetable(state: AgentState, **kwargs):
    """Returns the current weekly timetable of fixed classes/events."""
    return {"timetable": state.timetable}

def get_pending_tasks(state: AgentState, **kwargs):
    """Returns the list of pending tasks that need to be scheduled."""
    return {"pending_tasks": state.pending_tasks}

def schedule_session(state: AgentState, task_id: str = "", day: str = "", start: str = "", end: str = "", **kwargs):
    """
    Schedules a study session. 
    start and end should be in HH:MM format (e.g. 14:00, 16:00).
    Returns success message or error if there's a conflict or task not found.
    """
    if not start or not end or not re.match(r"^\d{2}:\d{2}$", start) or not re.match(r"^\d{2}:\d{2}$", end):
        return {"error": "start and end must be in HH:MM format."}
    
    if start >= end:
        return {"error": "start time must be before end time."}
        
    if day not in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
        return {"error": "day must be a valid day of the week, capitalized (e.g., Monday)."}

    # Check if task exists
    task = next((t for t in state.pending_tasks if t.get("id") == task_id), None)
    if not task:
        return {"error": f"Task '{task_id}' not found in pending tasks."}
    
    # Check timetable conflicts
    day_schedule = state.timetable.get(day, [])
    for block in day_schedule:
        b_start = block.get("start")
        b_end = block.get("end")
        if start < b_end and end > b_start:
            return {"error": f"Conflict with fixed timetable event: {block.get('title')} from {b_start} to {b_end}."}
            
    # Check scheduled sessions conflicts
    for sess in state.scheduled_sessions:
        if sess.get("day") == day:
            s_start = sess.get("start")
            s_end = sess.get("end")
            if start < s_end and end > s_start:
                return {"error": f"Conflict with already scheduled study session for '{sess.get('task_id')}' from {s_start} to {s_end}."}
                
    # Add to schedule
    state.scheduled_sessions.append({
        "task_id": task_id,
        "day": day,
        "start": start,
        "end": end
    })
    return {"success": f"Scheduled {task_id} on {day} from {start} to {end}."}

def get_scheduled_sessions(state: AgentState, **kwargs):
    """Returns the list of already scheduled study sessions."""
    return {"scheduled_sessions": state.scheduled_sessions}

def delete_session(state: AgentState, task_id: str = "", **kwargs):
    """Deletes a scheduled session by task_id. REQUIRES APPROVAL."""
    return {"error": "This action requires approval. Ask the user."}

TOOLS = {
    "get_timetable": get_timetable,
    "get_pending_tasks": get_pending_tasks,
    "schedule_session": schedule_session,
    "get_scheduled_sessions": get_scheduled_sessions,
    "delete_session": delete_session
}
