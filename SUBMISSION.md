Full name: Muhammad Asim
Roll number: i210852
Class / section: B
University email: i210852@nu.edu.pk
GitHub username: Dot-Asim
Agent name: StudyPlan Builder
Domain: Study-Plan Builder (Timetable + task list -> conflict-aware study plan)

GitHub repository URL: https://github.com/Dot-Asim/Study_Planner_Agent
Final commit hash: 8417c0e0da6d8978b14476ec59fb2edf2377b561
Working agent interface: https://study-planner-agent-b6n9.onrender.com/
Health endpoint (GET): https://study-planner-agent-b6n9.onrender.com/health
Arena endpoint (POST): https://study-planner-agent-b6n9.onrender.com/arena/run
Manifest endpoint (GET): https://study-planner-agent-b6n9.onrender.com/arena/manifest
API documentation: https://study-planner-agent-b6n9.onrender.com/docs

Hosting provider: Render
Default model / provider: llama-3.1-70b-versatile
Other available models: llama-3.1-8b-instant, mixtral-8x7b-32768
Example input: "I have a Math assignment due Friday (needs 3 hours). Schedule it."
Expected result: The agent calls get_timetable, get_pending_tasks, and then schedule_session, returning a completed plan.
Cold-start / restart limitations: In-memory history and state are lost on restart.
Repository access: Instructor invited / access confirmed
Public test results: tests/test_agent.py
