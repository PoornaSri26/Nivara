# Nivara: System & Technical Architecture

*Understand your thoughts. Build your balance.*

Nivara is an evidence-informed mental wellness platform engineered with an emphasis on **trustworthy personalization, clinical boundary enforcement, and user-auditable longitudinal memory**.

---

## 1. High-Level Architectural Diagram

```
                  ┌──────────────────────────────────────────────┐
                  │       Frontend Client (Web / Mobile)         │
                  │  (Guided CBT, Just Listen, EI Dashboard,     │
                  │   Thought Records, Somatic Box Breathing)    │
                  └───────────────────────┬──────────────────────┘
                                          │ HTTPS / WebSocket
                                          ▼
                  ┌──────────────────────────────────────────────┐
                  │            FastAPI Gateway Layer             │
                  └───────────────────────┬──────────────────────┘
                                          │
                 ┌────────────────────────┴────────────────────────┐
                 │                                                 │
                 ▼                                                 ▼
   ┌───────────────────────────┐                   ┌───────────────────────────────┐
   │ 🚨 OUT-OF-BAND SAFETY     │                   │ 🛑 PERSISTENT EMERGENCY SOS   │
   │    ORCHESTRATOR           │                   │ • Instant Exit to Safe State  │
   │ • Gate 1: Deterministic   │                   │ • Multi-Region Crisis Lines   │
   │   Regex / Crisis Rules    │                   │   (US/CA 988, UK 116 123,     │
   │ • Gate 2: Latent Risk     │                   │    IN 14416, Int'l directory) │
   │   Classifier & Boundaries │                   └───────────────────────────────┘
   └─────────────┬─────────────┘
                 │ (Pass: No Acute Risk)
                 ▼
   ┌─────────────────────────────────────────────────────────────┐
   │             LANGGRAPH-STYLE SUPERVISOR ORCHESTRATOR         │
   │  Maintains dialogue phase, intent routing, and constraints  │
   └───────┬──────────────┬──────────────┬──────────────┬────────┘
           │              │              │              │
           ▼              ▼              ▼              ▼
   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
   │  CBT Agent  │ │ Reflection  │ │ True Memory │ │ Just Listen │
   │ • 7-Column  │ │ Agent       │ │ Agent       │ │ Mode        │
   │   Thought   │ • Distortion  │ • Prospective │ • Rogerian    │
   │   Records   │   Taxonomy    │   Extraction  │   Validation  │
   │ • Behavioral│ • Trigger     │ • Confidence  │ • Zero Advice │
   │   Activation│   Mapping     │   Scoring     │ • Empathy     │
   └───────┬─────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
           │              │               │               │
           └──────────────┴───────┬───────┴───────────────┘
                                  ▼
   ┌─────────────────────────────────────────────────────────────┐
   │            OUTPUT GUARDRAIL & CLINICAL EVALUATION           │
   │ • No diagnostic statements or medication dosage leaks       │
   │ • Evaluation Agent scoring turn on clinical rubric          │
   └──────────────────────────────┬──────────────────────────────┘
                                  │
                                  ▼
   ┌─────────────────────────────────────────────────────────────┐
   │                PERSISTENCE LAYER (PostgreSQL / SQLite)      │
   │ • Users & Encrypted Sessions • Confirmed & Proposed Memories│
   │ • Thought Records & Tasks   • Safety Audits & Mood Logs    │
   └─────────────────────────────────────────────────────────────┘
```

---

## 2. Core Subsystems

### A. Dual-Gate Safety Orchestrator
The safety orchestrator runs **out-of-band** prior to model reasoning:
1. **Gate 1 (Deterministic Rules)**: Regex pattern matchers identify explicit self-harm, suicidal ideation, or homicidal intent with zero network latency. If triggered, execution halts immediately and serves region-specific crisis resources.
2. **Gate 1.5 (Clinical Boundaries)**: Regex checks intercept medication adjustment requests, diagnostic queries (*"Do I have bipolar disorder?"*), and delusion reinforcement, issuing empathetic redirects.
3. **Gate 2 (Probabilistic Risk Evaluation)**: Evaluates sentiment markers and latent despair cues.
4. **Output Guardrails**: Intercepts LLM outputs to guarantee zero accidental clinical diagnoses or medical prescriptions escape to the user.

### B. "True Memory" Architecture
Unlike conventional chat models that silently vectorize chat histories, Nivara treats memory as an **empowering, user-controlled asset**:
* **Source Classification**: Explicit user statements are classified as `DIRECT_USER_FACT` (confidence 0.95-1.0); detected patterns are classified as `INFERRED_PATTERN` (confidence 0.60-0.85).
* **Collaborative Inquiry**: Nivara never stores inferred triggers or distortions without proposing them to the user first.
* **Privacy Mode**: Users can toggle Privacy Mode at any time; this halts all long-term memory retrieval and extraction.
* **TTL & Expiration**: Proposed memories that remain unconfirmed expire automatically after 14 days.

### C. Clinical Modules
* **7-Column Thought Record**: Guided cognitive restructuring identifying Situation, Automatic Thought, Initial Emotion Intensity, Distortions, Evidence For, Evidence Against, and Balanced Alternative Thought.
* **Behavioral Activation**: Activity scheduling across *Mastery* and *Pleasure* categories to combat depressive avoidance and lethargy.
* **Grounding & Somatic Relaxation**: Animated Box Breathing (4s Inhale, 4s Hold, 4s Exhale, 4s Rest) and 5-4-3-2-1 Sensory Grounding.
* **"Just Listen" Mode**: Rogerian non-directive empathetic reflection. Strictly omits unsolicited advice, exercises, or analysis.

### D. Emotional Intelligence Dashboard
Presents longitudinal trends without clinical reductionism:
* Mood and coping confidence tracked over 7, 30, and 90 days.
* Cognitive distortion distribution bars.
* Situational trigger frequency heatmaps.
* Clear clinical notice framing data as user-reported observations, not medical assessments.

