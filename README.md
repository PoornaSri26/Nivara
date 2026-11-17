# Nivara: Evidence-Informed Mental Wellness Companion

> **"Understand your thoughts. Build your balance."**

Nivara is a personal, evidence-informed mental wellness platform engineered beyond basic conversational chatbots. It combines **out-of-band deterministic safety orchestration**, **LangGraph-style structured CBT workflows**, **user-controlled longitudinal memory ("True Memory")**, and an **Emotional Intelligence Dashboard**.

---

## 🌟 Key Features

1. **Dual-Gate Safety Orchestrator**:
   * **Gate 1 (Deterministic)**: Regex and rule-based catch of self-harm, suicidal ideation, and acute crises with immediate halt and regional helpline escalation (988 in US/CA, 116 123 in UK, 14416 in India).
   * **Gate 1.5 (Clinical Boundaries)**: Strict refusals against medication dosage recommendations, diagnostic labeling, and delusion reinforcement.
   * **Gate 2 (Heuristic / ML Risk Classifier)**: Nuanced risk scoring.
   * **Output Guardrails**: Post-generation verification blocking unintended clinical claims.
2. **"True Memory" System (User Agency & Auditability)**:
   * Categorizes memories into `DIRECT_USER_FACT` vs `INFERRED_PATTERN`.
   * Proposes memories to the user before permanently saving them.
   * Explicit controls: audit, confirm, edit, delete, or toggle Privacy Mode at any time.
3. **Clinical Self-Help Modules**:
   * **7-Column Thought Record**: Interactive cognitive restructuring (Situation, Automatic Thought, Emotion, Distortions, Evidence For, Evidence Against, Balanced Thought).
   * **Behavioral Activation**: Scheduling micro-actions rated on Mastery and Pleasure.
   * **Grounding & Somatic Pacer**: Box Breathing (4s Inhale, 4s Hold, 4s Exhale, 4s Rest) and 5-4-3-2-1 Sensory Grounding.
   * **"Just Listen" Mode**: Non-directive Rogerian validation with zero unsolicited advice.
4. **Emotional Intelligence Dashboard**:
   * Longitudinal mood and coping confidence tracking (7, 30, and 90 days).
   * Cognitive distortion distribution bars and trigger heatmaps.
   * Clinician-grounded notice (observations are correlations, not diagnostic labels).
5. **Evaluation Agent & Clinician Rubric**:
   * Automated scoring on Empathy, CBT Fidelity, and Boundary Compliance on every turn.
6. **Weekly Clinician Summary Report & Data Portability**:
   * Generate and export clinical-grade Markdown reports summarizing weekly trends, distortion distributions, and behavioral rhythms.
   * One-click data export and Daily 2-Minute Check-in flow.

---

## 📁 Repository Structure

```
nivara/
├── docker-compose.yml                  # Full stack: PostgreSQL 16 + pgvector & FastAPI
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI entry point
│   │   ├── config.py                   # Configuration and settings
│   │   ├── models/                     # SQLAlchemy models & Pydantic schemas
│   │   ├── safety/                     # Dual-Gate Safety Orchestrator & crisis resources
│   │   ├── agents/                     # LangGraph StateGraph, CBT, Reflection, Memory, Just Listen, Evaluation
│   │   ├── memory/                     # True Memory lifecycle service & vector search
│   │   ├── services/                   # Multi-provider LLM service & Weekly Report generator
│   │   ├── exercises/                  # Thought Record, Behavioral Activation, Grounding
│   │   └── api/                        # REST API endpoints (chat, memory, exercises, dashboard)
│   ├── tests/                          # 150+ adversarial red-team benchmarks & state tests
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── index.html                      # Complete interactive single-page app
│   ├── app.js                          # UI reactive state & fallback engine
│   └── styles.css                      # Calming, mindful Nivara design system
└── docs/
    ├── ARCHITECTURE.md                 # Deep technical architecture specification
    └── CLINICAL_SAFETY_RUBRIC.md       # Clinical rubric, safety tiers, and red-team tests
```

---

## 🚀 Getting Started

### 1. Running the Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
* API Documentation will be available at: `http://localhost:8000/docs`

### 2. Running Safety Red-Team Tests
```bash
cd backend
python -m unittest tests/test_safety_redteam.py
python -m unittest tests/test_state_machine.py
```

### 3. Running the Frontend
You can open `frontend/index.html` directly in any modern browser!
* The frontend includes a built-in interactive client-side simulation engine so you can immediately test the conversational flow, box breathing pacer, True Memory management, and Thought Records even without a running backend server.
* When the FastAPI backend is running on `http://localhost:8000`, the frontend automatically communicates with the live API.
