"""
Realistic college starter seed data for StudyPilot AI.
Provides rich sample subjects, topics, flashcards, notes, and study logs.
"""

from datetime import datetime, timedelta
from database.db_manager import (
    init_db, get_subjects, add_subject, add_topic, add_flashcard, add_note,
    log_study_session, record_quiz_attempt, create_study_plan, add_study_plan_items
)

def seed_sample_data(reset_first: bool = False):
    """Populates the database with rich college starter courses and study items."""
    init_db()
    
    # If already seeded and reset not requested, return gracefully
    if not reset_first and len(get_subjects()) > 0:
        return True
    
    # Target exam dates relative to today
    today = datetime.now().date()
    exam_cs = (today + timedelta(days=21)).isoformat()
    exam_os = (today + timedelta(days=35)).isoformat()
    exam_bio = (today + timedelta(days=45)).isoformat()
    
    # 1. Subjects
    cs_id = add_subject(
        name="Data Structures & Algorithms",
        code="CS201",
        color="#4F46E5", # Indigo
        icon="💻",
        target_date=exam_cs,
        target_score=95.0
    )
    
    os_id = add_subject(
        name="Operating Systems & Architecture",
        code="CS305",
        color="#059669", # Emerald
        icon="⚙️",
        target_date=exam_os,
        target_score=90.0
    )
    
    bio_id = add_subject(
        name="Molecular & Cell Biology",
        code="BIO101",
        color="#D97706", # Amber
        icon="🧬",
        target_date=exam_bio,
        target_score=88.0
    )
    
    # 2. Topics for CS201
    t1 = add_topic(cs_id, "Binary Search Trees & AVL Balancing", "Hard", 3.0, "High", "In Progress", "Rotation algorithms and height balance invariants.")
    t2 = add_topic(cs_id, "Graph Traversal (BFS & DFS)", "Medium", 2.0, "High", "Mastered", "Queue vs Stack, visited sets, cycle detection.")
    t3 = add_topic(cs_id, "Dijkstra's & Bellman-Ford Shortest Path", "Hard", 3.5, "High", "In Progress", "Priority queues, edge relaxations, negative cycles.")
    t4 = add_topic(cs_id, "Dynamic Programming: Knapsack & LCS", "Hard", 4.0, "High", "Not Started", "Memoization table, state transitions, subproblem optimality.")
    t5 = add_topic(cs_id, "Hash Tables & Collision Resolution", "Easy", 1.5, "Medium", "Mastered", "Open addressing, chaining, load factor calculations.")
    
    # Topics for CS305
    t6 = add_topic(os_id, "Process Synchronization & Semaphores", "Hard", 3.0, "High", "In Progress", "Race conditions, critical sections, Mutex vs Counting Semaphores.")
    t7 = add_topic(os_id, "Virtual Memory & Page Replacement", "Medium", 2.5, "High", "In Progress", "LRU, FIFO, Clock algorithm, Page Fault frequency.")
    t8 = add_topic(os_id, "CPU Scheduling (Round Robin, CFS)", "Easy", 1.5, "Medium", "Mastered", "Context switches, turnaround vs response time.")
    t9 = add_topic(os_id, "Deadlock Detection & Banker's Algorithm", "Medium", 2.0, "Medium", "Not Started", "Resource allocation graphs, safe state verification.")
    
    # Topics for BIO101
    t10 = add_topic(bio_id, "Cellular Respiration & Krebs Cycle", "Hard", 3.5, "High", "In Progress", "Glycolysis, electron transport chain, ATP synthesis.")
    t11 = add_topic(bio_id, "DNA Replication & Polymerase Enzymes", "Medium", 2.0, "Medium", "Mastered", "Leading vs lagging strand, Okazaki fragments, helicase.")
    t12 = add_topic(bio_id, "Photosynthesis (Light Reactions & Calvin)", "Medium", 2.5, "Medium", "Not Started", "Thylakoid membrane, photophosphorylation, Rubisco.")

    # 3. Flashcards
    add_flashcard(cs_id, t1, "What is the balance factor of an AVL tree node?", 
                  "Balance Factor = Height(Left Subtree) - Height(Right Subtree). An AVL tree requires this factor to be -1, 0, or +1 for all nodes.", "Good")
    add_flashcard(cs_id, t2, "What is the time complexity of BFS on an adjacency list graph?", 
                  "O(V + E), where V is the number of vertices and E is the number of edges.", "Easy")
    add_flashcard(cs_id, t5, "What happens when the load factor of a hash table exceeds 0.75?", 
                  "Most hash tables trigger a dynamic resize (usually doubling the bucket array capacity) and rehash existing entries to avoid high collision rates.", "Good")
    add_flashcard(os_id, t6, "What are the 4 Coffman conditions required for Deadlock?", 
                  "1. Mutual Exclusion\n2. Hold and Wait\n3. No Preemption\n4. Circular Wait", "Hard")
    add_flashcard(os_id, t7, "What is Belady's Anomaly?", 
                  "Belady's Anomaly is the counterintuitive phenomenon where increasing the number of page frames results in MORE page faults for FIFO page replacement.", "Good")
    add_flashcard(bio_id, t10, "What is the net ATP yield from 1 glucose molecule in aerobic respiration?", 
                  "Approximately 30 to 32 ATP molecules (2 from Glycolysis, 2 from Krebs Cycle, ~26-28 from Oxidative Phosphorylation).", "Good")

    # 4. Notes
    add_note(
        cs_id, t1, 
        "AVL Trees Cheatsheet & Rotations",
        "## AVL Tree Balancing Rules\n\n- **Invariance**: For every node $x$, $|h_{left} - h_{right}| \\le 1$.\n- **Left-Left (LL) Case**: Single Right Rotation at node $z$.\n- **Right-Right (RR) Case**: Single Left Rotation at node $z$.\n- **Left-Right (LR) Case**: Left rotation on child $y$, then Right rotation on $z$.\n- **Right-Left (RL) Case**: Right rotation on child $y$, then Left rotation on $z$.\n\n> Note: Lookup, Insertion, and Deletion are strictly guaranteed $O(\\log n)$.",
        "trees, algorithms, complexity"
    )
    
    add_note(
        os_id, t6,
        "Critical Section Problem & Peterson's Algorithm",
        "## Requirements for Critical Section Solution\n\n1. **Mutual Exclusion**: Only one process executes in the critical section at a time.\n2. **Progress**: If no process is in the critical section, only processes wishing to enter decide who goes next.\n3. **Bounded Waiting**: There is a limit on the number of times others can enter before a request is granted.\n\n### Peterson's Algorithm (2 processes):\n```c\nflag[i] = true;\nturn = j;\nwhile (flag[j] && turn == j);\n// Critical Section\nflag[i] = false;\n```",
        "concurrency, operating-systems, synchronization"
    )

    # 5. Study Sessions (Pomodoro focus sessions in the past 7 days)
    for i in range(7, 0, -1):
        past_date = datetime.now() - timedelta(days=i)
        # Log a couple focus sessions
        log_study_session(cs_id, t1, 50, "Focus", f"Covered AVL tree rotations Day -{i}")
        if i % 2 == 0:
            log_study_session(os_id, t6, 25, "Focus", f"Semaphore synchronization problems Day -{i}")
        if i % 3 == 0:
            log_study_session(bio_id, t10, 50, "Focus", f"Krebs cycle reaction steps Day -{i}")
            
    # Today's session
    log_study_session(cs_id, t3, 25, "Focus", "Shortest path Dijkstra walkthrough")

    # 6. Quiz Attempts
    quiz_details_1 = [
        {"question": "What is the worst-case lookup time in an AVL tree?", "user_answer": "O(log n)", "correct_answer": "O(log n)", "is_correct": True},
        {"question": "Which rotation resolves a Left-Right imbalance?", "user_answer": "Left then Right", "correct_answer": "Left then Right", "is_correct": True},
        {"question": "Does BFS use a stack or a queue?", "user_answer": "Queue", "correct_answer": "Queue", "is_correct": True},
        {"question": "What is the load factor formula?", "user_answer": "n / k", "correct_answer": "n / k", "is_correct": True},
        {"question": "Can Dijkstra handle negative weight cycles?", "user_answer": "Yes", "correct_answer": "No", "is_correct": False}
    ]
    import json
    record_quiz_attempt(
        subject_id=cs_id,
        topic_id=t1,
        quiz_title="CS201 Midterm Prep: Trees & Graphs",
        score=4,
        total_questions=5,
        percentage=80.0,
        difficulty="Medium",
        time_taken_seconds=185,
        details_json=json.dumps(quiz_details_1)
    )

    # 7. Sample Study Plan
    plan_id = create_study_plan(
        subject_id=cs_id,
        title="CS201 3-Week Finals Sprint",
        exam_date=exam_cs,
        available_hours_per_day=2.5,
        total_allocated_hours=14.0
    )
    
    plan_items = [
        {"day_number": 1, "scheduled_date": (today + timedelta(days=1)).isoformat(), "topic_id": t1, "session_title": "AVL Trees & Balance Factors", "allocated_hours": 2.0, "activity_type": "Study"},
        {"day_number": 2, "scheduled_date": (today + timedelta(days=2)).isoformat(), "topic_id": t1, "session_title": "AVL Tree Rotation Code Lab", "allocated_hours": 1.5, "activity_type": "Practice"},
        {"day_number": 3, "scheduled_date": (today + timedelta(days=3)).isoformat(), "topic_id": t3, "session_title": "Dijkstra Algorithm Deep Dive", "allocated_hours": 2.5, "activity_type": "Study"},
        {"day_number": 4, "scheduled_date": (today + timedelta(days=4)).isoformat(), "topic_id": t3, "session_title": "Shortest Path Problem Sets", "allocated_hours": 2.0, "activity_type": "Practice"},
        {"day_number": 5, "scheduled_date": (today + timedelta(days=5)).isoformat(), "topic_id": t4, "session_title": "Dynamic Programming: Knapsack", "allocated_hours": 2.5, "activity_type": "Study"},
        {"day_number": 6, "scheduled_date": (today + timedelta(days=6)).isoformat(), "topic_id": t4, "session_title": "DP LCS & Memoization Tables", "allocated_hours": 2.0, "activity_type": "Study"},
        {"day_number": 7, "scheduled_date": (today + timedelta(days=7)).isoformat(), "topic_id": t1, "session_title": "Comprehensive Mock Test 1", "allocated_hours": 1.5, "activity_type": "Quiz"}
    ]
    add_study_plan_items(plan_id, plan_items)
    
    return True
