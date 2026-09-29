"""
AI Service for StudyPilot AI.
Integrates with Google Gemini, OpenAI, and Groq LLM APIs.
Gracefully handles missing keys and offline environments with a high-quality
heuristic college AI engine. Never exposes keys and never hardcodes them.
"""

import json
import re
import requests
from typing import Dict, Any, List, Optional
import config

class AIService:
    def __init__(self):
        self.provider = config.get_active_provider()
        self.gemini_key = config.GEMINI_API_KEY
        self.openai_key = config.OPENAI_API_KEY
        self.groq_key = config.GROQ_API_KEY
    
    def refresh_keys(self, provider: Optional[str] = None, gemini_key: Optional[str] = None, 
                     openai_key: Optional[str] = None, groq_key: Optional[str] = None):
        """Allows dynamic configuration from UI Settings."""
        if provider:
            self.provider = provider
        if gemini_key is not None:
            self.gemini_key = gemini_key.strip()
        if openai_key is not None:
            self.openai_key = openai_key.strip()
        if groq_key is not None:
            self.groq_key = groq_key.strip()
            
        # Re-evaluate active provider if default
        if not provider or provider == "auto":
            if self.gemini_key:
                self.provider = "gemini"
            elif self.openai_key:
                self.provider = "openai"
            elif self.groq_key:
                self.provider = "groq"
            else:
                self.provider = "demo"

    def is_live(self) -> bool:
        """Returns True if a live LLM is configured and active."""
        if self.provider == "gemini" and self.gemini_key:
            return True
        if self.provider == "openai" and self.openai_key:
            return True
        if self.provider == "groq" and self.groq_key:
            return True
        return False

    def generate_text(self, prompt: str, system_prompt: str = "") -> Dict[str, Any]:
        """Dispatches request to active provider with fallback to demo engine."""
        if self.provider == "gemini" and self.gemini_key:
            res = self._call_gemini(prompt, system_prompt)
            if res.get("success"):
                return {"text": res["text"], "source": f"Google Gemini ({config.GEMINI_MODEL})", "is_demo": False}
        elif self.provider == "openai" and self.openai_key:
            res = self._call_openai(prompt, system_prompt)
            if res.get("success"):
                return {"text": res["text"], "source": f"OpenAI ({config.OPENAI_MODEL})", "is_demo": False}
        elif self.provider == "groq" and self.groq_key:
            res = self._call_groq(prompt, system_prompt)
            if res.get("success"):
                return {"text": res["text"], "source": f"Groq ({config.GROQ_MODEL})", "is_demo": False}
                
        # Fallback to local heuristic engine
        return {
            "text": self._local_heuristic_text(prompt, system_prompt),
            "source": "Local College Study Engine (Demo Mode)",
            "is_demo": True
        }

    # ========================================================
    # LIVE LLM API HANDLERS
    # ========================================================
    def _call_gemini(self, prompt: str, system_prompt: str = "") -> Dict[str, Any]:
        model = config.GEMINI_MODEL or "gemini-1.5-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.gemini_key}"
        
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        payload = {
            "contents": [{
                "parts": [{"text": full_prompt}]
            }],
            "generationConfig": {
                "temperature": 0.4,
                "maxOutputTokens": 2048,
            }
        }
        try:
            resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=25)
            if resp.status_code == 200:
                data = resp.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return {"success": True, "text": text}
            else:
                return {"success": False, "error": f"Gemini error {resp.status_code}: {resp.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _call_openai(self, prompt: str, system_prompt: str = "") -> Dict[str, Any]:
        model = config.OPENAI_MODEL or "gpt-4o-mini"
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openai_key}",
            "Content-Type": "application/json"
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.4,
            "max_tokens": 2048
        }
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=25)
            if resp.status_code == 200:
                data = resp.json()
                text = data["choices"][0]["message"]["content"]
                return {"success": True, "text": text}
            else:
                return {"success": False, "error": f"OpenAI error {resp.status_code}: {resp.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _call_groq(self, prompt: str, system_prompt: str = "") -> Dict[str, Any]:
        model = config.GROQ_MODEL or "llama-3.3-70b-versatile"
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.groq_key}",
            "Content-Type": "application/json"
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.4,
            "max_tokens": 2048
        }
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=25)
            if resp.status_code == 200:
                data = resp.json()
                text = data["choices"][0]["message"]["content"]
                return {"success": True, "text": text}
            else:
                return {"success": False, "error": f"Groq error {resp.status_code}: {resp.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ========================================================
    # SPECIALIZED AI APIS
    # ========================================================
    def generate_topic_explanation(self, topic: str, subject: str, mode: str, difficulty: str) -> Dict[str, Any]:
        """Generates comprehensive structured explanation for a topic."""
        system_prompt = (
            "You are StudyPilot AI, an elite college academic tutor and professor. "
            "Explain complex concepts clearly, thoroughly, and engagingly. "
            "Use standard Markdown, LaTeX math ($inline$ and $$display$$), and code snippets where relevant."
        )
        
        mode_instructions = {
            "Academic In-Depth": "Provide a rigorous academic breakdown: formal definition, core principles, step-by-step mathematical or architectural mechanics, edge cases, and exam insights.",
            "ELI5 & Intuitive Analogy": "Explain this using a brilliant, relatable real-world analogy. Avoid dry jargon initially, build intuitive understanding, then connect back to the formal term.",
            "Cheat Sheet & Quick Revision": "Produce high-density revision notes: key bullet points, formula tables, quick dos and don'ts, and memory mnemonics.",
            "Real-World Case Study": "Demonstrate how top industry engineers, scientists, or researchers apply this exact topic to solve real problems.",
            "Common Exam Pitfalls": "Highlight the top 5 traps and misconceptions that cause college students to lose marks on exams."
        }
        
        selected_mode_text = mode_instructions.get(mode, mode_instructions["Academic In-Depth"])
        
        prompt = f"""
Subject: {subject}
Topic: {topic}
Target Difficulty Level: {difficulty}
Explanation Style: {mode}

Instructions:
{selected_mode_text}

Format the response neatly with clear headers (##, ###), callout blockquotes (> Note:), and bullet points.
"""
        res = self.generate_text(prompt, system_prompt)
        
        # If in demo mode, enhance with specific topic knowledge
        if res.get("is_demo"):
            res["text"] = self._heuristic_explanation(topic, subject, mode, difficulty)
            
        return res

    def generate_quiz(self, topic: str, subject: str, num_questions: int = 5, difficulty: str = "Medium") -> List[Dict[str, Any]]:
        """Generates multiple choice questions with options and explanations."""
        system_prompt = (
            "You are an expert college exam question author. Output strictly valid JSON without markdown fences. "
            "The JSON must be an array of question objects."
        )
        prompt = f"""
Create {num_questions} multiple-choice questions for the following college topic:
Subject: {subject}
Topic: {topic}
Difficulty: {difficulty}

Each question object in the JSON array must follow this exact format:
{{
    "question": "Question text here?",
    "options": ["Option A text", "Option B text", "Option C text", "Option D text"],
    "correct_index": 0,
    "explanation": "Detailed explanation of why Option A is correct and why other choices are incorrect."
}}
Return ONLY valid JSON.
"""
        res = self.generate_text(prompt, system_prompt)
        raw_text = res["text"]
        
        # Clean json markdown fences if present
        clean_json = re.sub(r"^```json\s*", "", raw_text.strip(), flags=re.MULTILINE)
        clean_json = re.sub(r"^```\s*", "", clean_json.strip(), flags=re.MULTILINE)
        clean_json = clean_json.strip("` \n\r\t")
        
        try:
            parsed = json.loads(clean_json)
            if isinstance(parsed, list) and len(parsed) > 0 and "question" in parsed[0]:
                return parsed[:num_questions]
        except Exception:
            pass
            
        # Fallback to rich heuristic quiz generator
        return self._heuristic_quiz(topic, subject, num_questions, difficulty)

    def generate_flashcards(self, topic: str, subject: str, count: int = 5) -> List[Dict[str, str]]:
        """Generates flashcards (Front: Concept/Prompt, Back: Clear concise answer)."""
        system_prompt = "You are a flashcard generator for college students. Output strictly valid JSON."
        prompt = f"""
Create {count} high-yield flashcards for:
Subject: {subject}
Topic: {topic}

Return an array of JSON objects with:
[
  {{ "question": "Front of card (prompt or question)", "answer": "Back of card (clear explanation/formula)" }}
]
Return ONLY JSON.
"""
        res = self.generate_text(prompt, system_prompt)
        raw_text = res["text"]
        
        clean_json = re.sub(r"^```json\s*", "", raw_text.strip(), flags=re.MULTILINE)
        clean_json = re.sub(r"^```\s*", "", clean_json.strip(), flags=re.MULTILINE)
        clean_json = clean_json.strip("` \n\r\t")
        
        try:
            parsed = json.loads(clean_json)
            if isinstance(parsed, list) and len(parsed) > 0 and "question" in parsed[0]:
                return parsed[:count]
        except Exception:
            pass
            
        return self._heuristic_flashcards(topic, subject, count)

    def enhance_notes(self, content: str, action: str) -> str:
        """Processes notes with AI: Summarize, Extract Terms, Generate Questions, Format."""
        if not content.strip():
            return "Please provide some note content to enhance."
            
        system_prompt = "You are an expert academic study assistant specializing in note optimization."
        
        prompts = {
            "summarize": f"Summarize the following study notes into high-impact key takeaways, core mechanisms, and an executive TL;DR:\n\n{content}",
            "extract_terms": f"Extract all critical academic terms, definitions, theorems, and formulas from the following notes as a reference glossary:\n\n{content}",
            "generate_questions": f"Generate 5 challenging exam-style practice questions (with answers) based strictly on these notes:\n\n{content}",
            "polish_markdown": f"Format and polish the following study notes using modern GitHub-flavored markdown with clean headers, bullet points, callout blockquotes, and LaTeX math formatting where applicable:\n\n{content}"
        }
        
        prompt = prompts.get(action, prompts["summarize"])
        res = self.generate_text(prompt, system_prompt)
        if res.get("is_demo"):
            return self._heuristic_note_enhancement(content, action)
        return res["text"]

    # ========================================================
    # LOCAL HEURISTIC ACADEMIC ENGINES (100% Reliable Offline Fallback)
    # ========================================================
    def _local_heuristic_text(self, prompt: str, system_prompt: str) -> str:
        return (
            "### 📚 Academic Synthesis\n\n"
            "This concept is a cornerstone of modern curricula. It operates on foundational principles "
            "of decomposition, structural invariants, and systematic state transitions.\n\n"
            "#### Core Key Takeaways:\n"
            "- **Invariant Definition**: Establishes boundaries within which operations remain mathematically predictable.\n"
            "- **Complexity & Efficiency**: Typically optimized for space and time trade-offs ($O(n \\log n)$ or amortized constant time).\n"
            "- **Standard Practical Application**: Widely utilized in distributed systems, algorithmic trading, bioinformatics, and operating system kernels.\n\n"
            "> **Study Tip**: To master this topic for exams, focus on edge cases (null inputs, boundary conditions, and overflow limits)."
        )

    def _heuristic_explanation(self, topic: str, subject: str, mode: str, difficulty: str) -> str:
        """Dynamic heuristic generator producing rich, topic-relevant markdown."""
        topic_lower = topic.lower()
        
        if "avl" in topic_lower or "tree" in topic_lower:
            return (
                f"## 🌲 Master Class: {topic}\n\n"
                f"**Subject:** {subject} | **Difficulty:** {difficulty} | **Mode:** {mode}\n\n"
                "### 1. Formal Definition & Invariant\n"
                "An **AVL Tree** (named after Adelson-Velsky and Landis) is a self-balancing binary search tree. "
                "In an AVL tree, the heights of the two child subtrees of any node differ by at most one.\n\n"
                "$$\\text{Balance Factor } (BF) = \\text{Height}(Left) - \\text{Height}(Right) \\in \\{-1, 0, 1\\}$$\n\n"
                "If $|BF| > 1$, the tree is rebalanced using rotations.\n\n"
                "### 2. The 4 Fundamental Rebalancing Rotations\n\n"
                "| Case | Condition | Corrective Action |\n"
                "|---|---|---|\n"
                "| **Left-Left (LL)** | Inserted in left child of left subtree | Single **Right Rotation** at node $z$ |\n"
                "| **Right-Right (RR)** | Inserted in right child of right subtree | Single **Left Rotation** at node $z$ |\n"
                "| **Left-Right (LR)** | Inserted in right child of left subtree | **Left Rotation** on child $y$, then **Right Rotation** on $z$ |\n"
                "| **Right-Left (RL)** | Inserted in left child of right subtree | **Right Rotation** on child $y$, then **Left Rotation** on $z$ |\n\n"
                "### 3. Asymptotic Time & Space Complexity\n"
                "- **Search:** $O(\\log n)$ strictly guaranteed due to height bound $h \\le 1.44 \\log_2(n + 2)$.\n"
                "- **Insertion:** $O(\\log n)$ ($O(1)$ rotations after lookup).\n"
                "- **Deletion:** $O(\\log n)$ (may require up to $O(\\log n)$ rotations up to root).\n"
                "- **Space:** $O(n)$ where each node stores a height/balance factor integer.\n\n"
                "> 💡 **Exam Insight**: Remember that while Red-Black trees are faster for frequent insertions, "
                "AVL trees provide faster lookup times because they are more rigidly balanced."
            )
        elif "process" in topic_lower or "semaphore" in topic_lower or "lock" in topic_lower or "os" in topic_lower:
            return (
                f"## ⚙️ Operating Systems: {topic}\n\n"
                f"**Subject:** {subject} | **Difficulty:** {difficulty} | **Mode:** {mode}\n\n"
                "### 1. The Concurrency Challenge\n"
                "In preemptive multitasking environments, multiple processes or threads sharing shared memory "
                "create **Race Conditions** if execution timing alters final state variables.\n\n"
                "### 2. The 3 Golden Criteria for Mutual Exclusion\n"
                "1. **Mutual Exclusion**: If process $P_i$ is executing in its critical section, no other processes can enter.\n"
                "2. **Progress**: If no process is executing and some wish to enter, only those not in their remainder section can participate in the decision.\n"
                "3. **Bounded Waiting**: There must exist a bound on the number of times other processes are allowed to enter after a request is made.\n\n"
                "### 3. Counting Semaphores vs Mutex\n"
                "A **Semaphore** $S$ is an integer variable accessed solely through two standard atomic operations:\n\n"
                "```c\n"
                "wait(S) { // P() operation\n"
                "    while (S <= 0); // busy wait or block\n"
                "    S--;\n"
                "}\n\n"
                "signal(S) { // V() operation\n"
                "    S++;\n"
                "}\n"
                "```\n\n"
                "> ⚠️ **Exam Trap**: A common deadlock occurs when two processes wait for semaphores in inverse orders: "
                "e.g., $P_1$ acquires $A$ then asks for $B$; $P_2$ acquires $B$ then asks for $A$."
            )
        elif "dijkstra" in topic_lower or "graph" in topic_lower:
            return (
                f"## 🌐 Graph Algorithms: {topic}\n\n"
                f"**Subject:** {subject} | **Difficulty:** {difficulty} | **Mode:** {mode}\n\n"
                "### 1. Principle of Greedy Relaxation\n"
                "Dijkstra's algorithm solves the **Single-Source Shortest Path (SSSP)** problem for directed/undirected graphs "
                "with non-negative edge weights.\n\n"
                "$$\\text{Relaxation Step: if } d[u] + w(u, v) < d[v] \\implies d[v] = d[u] + w(u, v)$$\n\n"
                "### 2. Pseudocode with Min-Priority Queue\n"
                "```python\n"
                "import heapq\n\n"
                "def dijkstra(graph, start):\n"
                "    dist = {node: float('inf') for node in graph}\n"
                "    dist[start] = 0\n"
                "    pq = [(0, start)]\n\n"
                "    while pq:\n"
                "        d, u = heapq.heappop(pq)\n"
                "        if d > dist[u]: continue\n"
                "        for v, weight in graph[u]:\n"
                "            if dist[u] + weight < dist[v]:\n"
                "                dist[v] = dist[u] + weight\n"
                "                heapq.heappush(pq, (dist[v], v))\n"
                "    return dist\n"
                "```\n\n"
                "### 3. Complexity Breakdown\n"
                "- With adjacency matrix: $O(V^2)$\n"
                "- With binary heap: $O((V + E) \\log V)$\n"
                "- With Fibonacci heap: $O(E + V \\log V)$\n\n"
                "> 🚨 **Critical Rule**: Dijkstra fails with negative weights because once a node is settled (marked visited), "
                "its distance is assumed final. Use Bellman-Ford for negative edge weights!"
            )
        else:
            return (
                f"## 📖 Academic Guide: {topic}\n\n"
                f"**Subject:** {subject} | **Target Level:** {difficulty} | **Perspective:** {mode}\n\n"
                "### 1. Conceptual Framework\n"
                f"**{topic}** is an essential topic within {subject}. It serves as a foundational building block "
                "for higher-level applications and analytical problem solving.\n\n"
                "### 2. Core Mechanics & Principles\n"
                "- **Fundamental Theorem / Axiom**: Defines the structural constraints governing system behavior.\n"
                "- **State Relationships**: Explains how inputs, parameters, and environmental factors produce reliable outputs.\n"
                "- **Performance & Scalability**: Analyzes trade-offs between precision, speed, memory, and computational cost.\n\n"
                "### 3. Step-by-Step Analysis Strategy\n"
                "1. **Deconstruct the Given Problem**: Identify the known constraints and state boundaries.\n"
                "2. **Apply the Core Formula / Model**: Set up the governing equations or invariants.\n"
                "3. **Validate Invariants**: Ensure edge conditions do not violate system assumptions.\n\n"
                "> 📌 **Summary Takeaway**: Always verify both the base case and the inductive transition when working through {topic} on exams."
            )

    def _heuristic_quiz(self, topic: str, subject: str, num_questions: int, difficulty: str) -> List[Dict[str, Any]]:
        """Generates realistic college-grade multiple-choice questions."""
        base_pool = [
            {
                "question": f"Which of the following is the primary operational invariant for {topic}?",
                "options": [
                    "Maintaining bounded overhead and predictable state transitions",
                    "Minimizing all network round trips unconditionally",
                    "Forcing linear time traversal across all worst-case inputs",
                    "Eliminating auxiliary storage completely at the cost of correctness"
                ],
                "correct_index": 0,
                "explanation": "Correct! Foundational designs prioritize structural invariants that guarantee bounded operational behavior."
            },
            {
                "question": f"When scaling {topic} to large production systems, which bottleneck is most critical?",
                "options": [
                    "Static memory fragmentation",
                    "Lock contention and asymptotic algorithmic growth",
                    "Uncompressed string literals",
                    "Excessive floating point rounding errors"
                ],
                "correct_index": 1,
                "explanation": "Correct! As systems scale, algorithmic complexity ($O(n^2)$ vs $O(n \\log n)$) and synchronization contention dominate latency."
            },
            {
                "question": f"What is the standard time complexity for basic queries in an optimal implementation of {topic}?",
                "options": [
                    "O(1) to O(log n)",
                    "O(n!) factorial",
                    "O(n^3) cubic",
                    "O(2^n) exponential"
                ],
                "correct_index": 0,
                "explanation": "Correct! Well-constructed data structures or algorithms for this topic operate in logarithmic or amortized constant time."
            },
            {
                "question": f"Which condition causes an immediate failure or degraded state in {topic}?",
                "options": [
                    "Exceeding allocated buffer capacity or violating balance criteria",
                    "Running during daytime operational hours",
                    "Using 64-bit integer registers instead of 32-bit",
                    "Enabling compile-time dead-code elimination"
                ],
                "correct_index": 0,
                "explanation": "Correct! Violating balance invariants or exceeding buffer limits leads to overflow, degeneration, or runtime exceptions."
            },
            {
                "question": f"In university exam problem sets regarding {topic}, what is the most common student pitfall?",
                "options": [
                    "Neglecting edge cases such as empty sets, boundary roots, or cycle detection",
                    "Using too many explanatory comments in code",
                    "Drawing neat visual diagrams of the state machine",
                    "Calculating asymptotic bounds using Big-O notation"
                ],
                "correct_index": 0,
                "explanation": "Correct! College graders routinely deduct marks for missing edge cases (empty inputs, single elements, negative weights)."
            }
        ]
        return base_pool[:num_questions]

    def _heuristic_flashcards(self, topic: str, subject: str, count: int) -> List[Dict[str, str]]:
        pool = [
            {
                "question": f"What is the core definition of {topic} in {subject}?",
                "answer": f"{topic} is a foundational mechanism designed to manage state, solve structural constraints, and optimize operational throughput."
            },
            {
                "question": f"What is the primary trade-off when implementing {topic}?",
                "answer": "Time efficiency versus space overhead: achieving faster lookup or transition speeds usually requires additional index pointers or memoization tables."
            },
            {
                "question": f"How do you test for correctness in {topic}?",
                "answer": "Verify base cases (empty inputs, single element), verify induction step, and test boundary conditions against extreme values."
            },
            {
                "question": f"What mathematical notation describes the worst-case behavior of {topic}?",
                "answer": "Big-O notation (e.g. O(log n) or O(n)), which represents an asymptotic upper bound on runtime growth."
            },
            {
                "question": f"What is one real-world software system that relies heavily on {topic}?",
                "answer": "Database indexing engines (B-Trees / Hash maps), operating system memory managers, and network packet routers."
            }
        ]
        return pool[:count]

    def _heuristic_note_enhancement(self, content: str, action: str) -> str:
        if action == "summarize":
            return (
                "### 🎯 AI Note Summary & Key Takeaways\n\n"
                "- **Executive Core**: The notes outline the core structure and operational principles of the subject.\n"
                "- **Key Mechanism**: Highlights the transition rules, constraints, and formulas necessary for problem solving.\n"
                "- **Exam Focus**: Pay close attention to definitions, runtime bounds, and edge condition handling.\n\n"
                "#### Quick Review Questions:\n"
                "1. Can you explain the main mechanism in your own words without reading the notes?\n"
                "2. What happens if the primary invariant is violated?"
            )
        elif action == "extract_terms":
            words = list(set([w.strip(".,;:()") for w in content.split() if len(w) > 4]))[:8]
            terms_md = "### 📚 Extracted Terminology & Glossary\n\n"
            for w in words:
                terms_md += f"- **{w.capitalize()}**: Key concept referenced in the notes; review its formal mathematical definition.\n"
            return terms_md
        elif action == "generate_questions":
            return (
                "### 📝 Practice Exam Questions Generated from Notes\n\n"
                "1. **Conceptual**: State the primary definition and conditions under which this concept applies.\n"
                "   - *Answer*: Formulate based on section 1 of the notes.\n"
                "2. **Computational / Trace**: Given an initial input state, trace the next two execution steps.\n"
                "   - *Answer*: Step through the algorithm or formula sequentially.\n"
                "3. **Comparative**: How does this approach compare to naive brute-force methods in time complexity?\n"
                "   - *Answer*: Provides polynomial or logarithmic speedup by avoiding redundant recalculation."
            )
        else: # polish
            lines = [line.strip() for line in content.split("\n") if line.strip()]
            formatted = "### 📖 Cleaned Study Notes\n\n"
            for i, line in enumerate(lines):
                if i == 0:
                    formatted += f"#### {line}\n\n"
                elif ":" in line:
                    parts = line.split(":", 1)
                    formatted += f"- **{parts[0].strip()}**: {parts[1].strip()}\n"
                else:
                    formatted += f"- {line}\n"
            return formatted

# Global singleton instance
ai_service = AIService()
