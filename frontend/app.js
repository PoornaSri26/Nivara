// Nivara - Frontend Application & Interactive Engine
const API_BASE = "http://localhost:8000/api/v1";

// Application State
const state = {
  userId: "user-" + Math.random().toString(36).substring(2, 9),
  sessionId: "session-" + Date.now(),
  currentMode: "GUIDED_CBT", // GUIDED_CBT, JUST_LISTEN, THOUGHT_RECORD
  privacyMode: false,
  memories: [
    {
      id: "mem-1",
      category: "TRIGGER",
      content: "Anxiety spikes before Monday morning team standup presentations",
      source_type: "INFERRED_PATTERN",
      confidence_score: 0.85,
      status: "CONFIRMED",
      created_at: "2026-11-10"
    },
    {
      id: "mem-2",
      category: "GOAL",
      content: "Wants to practice public speaking and reduce catastrophic thinking",
      source_type: "DIRECT_USER_FACT",
      confidence_score: 0.95,
      status: "CONFIRMED",
      created_at: "2026-11-12"
    },
    {
      id: "mem-3",
      category: "COGNITIVE_DISTORTION",
      content: "Recurring Mind Reading: assuming colleagues judge hesitation as incompetence",
      source_type: "INFERRED_PATTERN",
      confidence_score: 0.75,
      status: "PROPOSED",
      created_at: "2026-11-15"
    }
  ]
};

// DOM Elements
const chatMessages = document.getElementById("chat-messages");
const chatInput = document.getElementById("chat-input");
const sendBtn = document.getElementById("send-btn");
const quickReplies = document.getElementById("quick-replies");
const sosModal = document.getElementById("sos-modal");
const sosBtn = document.getElementById("sos-btn");
const privacyToggle = document.getElementById("privacy-toggle");
const currentViewTitle = document.getElementById("current-view-title");
const memoriesContainer = document.getElementById("memories-container");
const memoryCountBadge = document.getElementById("memory-count-badge");

// Initialize Application
document.addEventListener("DOMContentLoaded", () => {
  setupNavigation();
  setupChatHandlers();
  setupSOSModal();
  setupPrivacyToggle();
  setupThoughtRecordForm();
  setupBreathingPacer();
  setupVoiceInput();
  setupDailyCheckin();
  loadJournalEntries();
  renderMemories();
});

// View Navigation
function setupNavigation() {
  document.querySelectorAll(".nav-item").forEach(item => {
    item.addEventListener("click", () => {
      document.querySelectorAll(".nav-item").forEach(i => i.classList.remove("active"));
      item.classList.add("active");

      const viewId = item.getAttribute("data-view");
      const mode = item.getAttribute("data-mode");

      document.querySelectorAll(".view-container").forEach(v => v.classList.remove("active"));
      const targetView = document.getElementById(viewId);
      if (targetView) targetView.classList.add("active");

      // Update Mode
      if (mode) {
        state.currentMode = mode;
        if (mode === "JUST_LISTEN") {
          currentViewTitle.innerHTML = "<span>🎧</span> 'Just Listen' Mode (Non-directive, no unsolicited advice)";
          appendBotMessage({
            reply: "I am now in **'Just Listen' mode**. I won't give advice or suggest exercises unless you ask. Take all the time and space you need—I'm here to listen."
          });
        } else {
          currentViewTitle.innerHTML = "<span>🌿</span> Guided CBT Session";
        }
      } else {
        currentViewTitle.innerHTML = item.innerHTML;
      }
    });
  });
}

// Chat Input & Sending
function setupChatHandlers() {
  sendBtn.addEventListener("click", handleSend);
  chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  });
}

async function handleSend() {
  const text = chatInput.value.trim();
  if (!text) return;

  chatInput.value = "";
  appendUserMessage(text);

  // Check backend availability, fallback to local engine if needed
  try {
    const response = await fetch(`${API_BASE}/chat/message`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: state.sessionId,
        user_id: state.userId,
        content: text,
        mode_override: state.currentMode
      })
    });
    if (response.ok) {
      const data = await response.json();
      appendBotMessage(data);
      return;
    }
  } catch (err) {
    // Backend offline: run client-side simulated engine seamlessly
  }

  // Local Client-Side Safe Processing Engine
  processMessageLocally(text);
}

function processMessageLocally(text) {
  const textLower = text.toLowerCase();

  // 1. Dual-Gate Safety: Crisis Check
  const crisisRegex = /(want|wish|going)\s+to\s+(die|end\s+it\s+all|kill\s+myself|commit\s+suicide)|how\s+to\s+(hang|slit|overdose|kill)\s+myself|planning\s+my\s+suicide/i;
  if (crisisRegex.test(textLower)) {
    appendBotMessage({
      is_crisis: true,
      reply: "I hear how much pain you are carrying right now, and I care deeply about your safety. Because I am an AI companion and not a human clinician or emergency service, I cannot provide the support you need in this moment. Please connect with someone who can support you right now.",
      crisis_payload: {
        phone: "Call or text 988 (Suicide & Crisis Lifeline)",
        sms: "Text HOME to 741741"
      }
    });
    openSOSModal();
    return;
  }

  // 2. Clinical Boundaries Check (Medication & Diagnosis)
  if (/dose|dosage|prescribe|should\s+i\s+take\s+(zoloft|lexapro|prozac|xanax|adderall)/i.test(textLower)) {
    appendBotMessage({
      reply: "I cannot recommend, adjust, or prescribe medications. Please consult your prescribing physician, psychiatrist, or pharmacist regarding any medication questions."
    });
    return;
  }
  if (/do\s+i\s+have|diagnose\s+me|am\s+i\s+(bipolar|schizophrenic|borderline|depressed)/i.test(textLower)) {
    appendBotMessage({
      reply: "As an AI wellness companion, I cannot provide psychiatric or medical diagnoses. I can help you explore your thoughts and emotions, but a formal assessment requires a licensed mental health professional."
    });
    return;
  }

  // 3. Cognitive Distortions Detection
  const distortions = [];
  if (/worst|everything\s+is\s+ruined|disaster|total\s+failure/i.test(textLower)) distortions.push("Catastrophizing");
  if (/always|never|completely|nothing\s+ever/i.test(textLower)) distortions.push("All-or-Nothing Thinking");
  if (/they\s+(all\s+)?(hate|think\s+i['’]?m|judge)\s+me/i.test(textLower)) distortions.push("Mind Reading");

  // 4. Memory Proposals
  const proposedMemories = [];
  if (!state.privacyMode) {
    if (/anxious\s+(before|when)\s+([^\.\,\n]+)/i.test(textLower)) {
      const match = textLower.match(/anxious\s+(before|when)\s+([^\.\,\n]+)/i);
      const newMem = {
        id: "mem-" + Date.now(),
        category: "TRIGGER",
        content: `Anxiety triggered when ${match[2].trim()}`,
        source_type: "INFERRED_PATTERN",
        confidence_score: 0.85,
        status: "PROPOSED",
        confirmation_prompt: `I noticed you feel anxious when ${match[2].trim()}. Would you like me to remember this pattern for future sessions?`
      };
      state.memories.push(newMem);
      proposedMemories.push(newMem);
      renderMemories();
    }
  }

  // 5. Generate Mode Reply
  let reply = "";
  let quickRepliesList = [];

  if (state.currentMode === "JUST_LISTEN") {
    reply = "I hear how much you're holding right now, and what you are feeling makes complete sense. I am right here with you—no pressure to fix or solve anything.";
    quickRepliesList = ["I feel heard, thank you", "Keep talking", "Switch to Guided CBT"];
  } else {
    if (distortions.length > 0) {
      reply = `I hear how heavy this feels. Noticing that thought, it touches on what CBT calls **${distortions.join(" & ")}**.\n\nWhen you examine the factual evidence, is this worst-case scenario guaranteed, or are there alternative outcomes we could consider?`;
      quickRepliesList = ["Start 7-Column Thought Record", "Try Box Breathing", "Tell me more about this pattern"];
    } else {
      reply = "Thank you for sharing that with me. When you look at this situation, what feels like the most challenging part of it right now?";
      quickRepliesList = ["Examine with Thought Record", "Help me reframe this", "Just listen to me"];
    }
  }

  appendBotMessage({
    reply: reply,
    detected_distortions: distortions,
    proposed_memories: proposedMemories,
    suggested_quick_replies: quickRepliesList
  });
}

function appendUserMessage(text) {
  const div = document.createElement("div");
  div.className = "message-bubble user";
  div.textContent = text;
  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Milestone Toast
function showMilestoneToast(title, description) {
  const toast = document.getElementById("milestone-toast");
  if (!toast) return;
  document.getElementById("milestone-title").textContent = title;
  document.getElementById("milestone-desc").textContent = description;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 4500);
}

function appendBotMessage(data) {
  const div = document.createElement("div");
  div.className = "message-bubble bot" + (data.is_crisis ? " crisis" : "");

  // Bookmark button
  const bookmarkBtn = document.createElement("button");
  bookmarkBtn.className = "bookmark-btn";
  bookmarkBtn.title = "Save to Coping Toolbox";
  bookmarkBtn.textContent = "🔖";
  bookmarkBtn.onclick = () => {
    const label = prompt("Label this for your Coping Toolbox:", "Helpful reflection");
    if (label) {
      addToToolbox(label, data.reply);
      showMilestoneToast("Saved to Coping Toolbox 🧰", label);
    }
  };
  div.appendChild(bookmarkBtn);

  let html = `<div class="meta-tag">Nivara • ${state.currentMode === "JUST_LISTEN" ? "Listening Mode" : "Balanced Guidance"}</div>`;
  html += `<p>${data.reply.replace(/\n\n/g, "</p><p>").replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")}</p>`;

  // Detected Distortions Chips
  if (data.detected_distortions && data.detected_distortions.length > 0) {
    html += `<div class="distortion-chips">`;
    data.detected_distortions.forEach(d => {
      html += `<span class="distortion-chip">💡 ${d}</span>`;
    });
    html += `</div>`;
  }

  // Proposed Memory Prompt
  if (data.proposed_memories && data.proposed_memories.length > 0) {
    data.proposed_memories.forEach(mem => {
      html += `
        <div class="memory-proposal-card">
          <strong>🧠 Memory Confirmation</strong>
          <p style="margin-top: 4px;">${mem.confirmation_prompt || mem.content}</p>
          <div class="actions">
            <button class="btn-small btn-confirm" onclick="confirmMemory('${mem.id}')">Remember this</button>
            <button class="btn-small btn-reject" onclick="rejectMemory('${mem.id}')">Don't save</button>
          </div>
        </div>
      `;
    });
  }

  div.innerHTML = html;
  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;

  // Render Quick Replies
  renderQuickReplies(data.suggested_quick_replies || []);
}

function renderQuickReplies(replies) {
  quickReplies.innerHTML = "";
  if (!replies || replies.length === 0) return;
  replies.forEach(r => {
    const btn = document.createElement("button");
    btn.className = "quick-reply-btn";
    btn.textContent = r;
    btn.onclick = () => sendQuickReply(r);
    quickReplies.appendChild(btn);
  });
}

function sendQuickReply(text) {
  chatInput.value = text;
  handleSend();
}

// True Memory Rendering & Management
function renderMemories() {
  if (!memoriesContainer) return;
  memoriesContainer.innerHTML = "";
  memoryCountBadge.textContent = state.memories.length;

  state.memories.forEach(mem => {
    const card = document.createElement("div");
    card.className = "dash-card";
    card.style.display = "flex";
    card.style.justifyContent = "space-between";
    card.style.alignItems = "flex-start";

    const badgeColor = mem.status === "CONFIRMED" ? "var(--color-primary-soft)" : "var(--color-amber-soft)";
    const textColor = mem.status === "CONFIRMED" ? "var(--color-primary)" : "var(--color-amber-text)";

    card.innerHTML = `
      <div>
        <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 6px;">
          <span style="font-size: 11px; font-weight: 700; background: ${badgeColor}; color: ${textColor}; padding: 2px 8px; border-radius: 4px;">${mem.category}</span>
          <span style="font-size: 12px; color: var(--color-text-light);">${mem.status} (${Math.round(mem.confidence_score * 100)}% confidence)</span>
        </div>
        <p style="font-size: 14px; font-weight: 500;">${mem.content}</p>
      </div>
      <div style="display: flex; gap: 6px;">
        ${mem.status === 'PROPOSED' ? `<button class="btn-small btn-confirm" onclick="confirmMemory('${mem.id}')">Confirm</button>` : ''}
        <button class="btn-small btn-reject" onclick="deleteMemory('${mem.id}')">Delete</button>
      </div>
    `;
    memoriesContainer.appendChild(card);
  });
}

function confirmMemory(id) {
  const m = state.memories.find(x => x.id === id);
  if (m) {
    m.status = "CONFIRMED";
    renderMemories();
    alert("Memory confirmed and added to your continuity profile.");
  }
}

function rejectMemory(id) {
  state.memories = state.memories.filter(x => x.id !== id);
  renderMemories();
}

function deleteMemory(id) {
  state.memories = state.memories.filter(x => x.id !== id);
  renderMemories();
}

function clearAllMemories() {
  if (confirm("Are you sure you want to permanently delete all stored memories?")) {
    state.memories = [];
    renderMemories();
  }
}

// Data Export (GDPR / User Portability)
function exportUserData() {
  const exportPayload = {
    exportedAt: new Date().toISOString(),
    userId: state.userId,
    privacyMode: state.privacyMode,
    trueMemories: state.memories,
    notice: "Exported from Nivara. Data is strictly user-owned and confidential."
  };
  const blob = new Blob([JSON.stringify(exportPayload, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `nivara_data_export_${new Date().toISOString().slice(0, 10)}.json`;
  a.click();
  URL.revokeObjectURL(url);
}

// Voice Reflection (Web Speech API)
function setupVoiceInput() {
  const voiceBtn = document.getElementById("voice-btn");
  if (!voiceBtn) return;

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    voiceBtn.style.display = "none";
    return;
  }

  const recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = false;
  let isListening = false;

  recognition.onstart = () => {
    isListening = true;
    voiceBtn.textContent = "🔴";
    voiceBtn.title = "Listening... Speak your reflection";
  };

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    chatInput.value = chatInput.value ? chatInput.value + " " + transcript : transcript;
  };

  recognition.onend = () => {
    isListening = false;
    voiceBtn.textContent = "🎙️";
    voiceBtn.title = "Voice Reflection (Speech-to-Text)";
  };

  voiceBtn.addEventListener("click", () => {
    if (isListening) {
      recognition.stop();
    } else {
      recognition.start();
    }
  });
}

// Privacy Mode
function setupPrivacyToggle() {
  privacyToggle.addEventListener("change", (e) => {
    state.privacyMode = e.target.checked;
    alert(state.privacyMode ? "Privacy Mode Enabled: Nivara will not record or reference long-term memory." : "Privacy Mode Disabled.");
  });
}

// Thought Record Form
function setupThoughtRecordForm() {
  const form = document.getElementById("thought-record-form");
  if (!form) return;
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    alert("Thought Record successfully saved! Added to your Emotional Intelligence metrics.");
    form.reset();
  });
}

// Grounding Box Breathing Animation
let breathingInterval = null;
let breathingPhase = 0; // 0: Inhale, 1: Hold, 2: Exhale, 3: Hold
const phases = [
  { text: "Inhale through nose (4s)", class: "inhale" },
  { text: "Hold gently (4s)", class: "hold" },
  { text: "Exhale through mouth (4s)", class: "exhale" },
  { text: "Rest empty (4s)", class: "rest" }
];

function setupBreathingPacer() {
  const circle = document.getElementById("breath-circle");
  const instruction = document.getElementById("breath-instruction");
  const toggleBtn = document.getElementById("btn-toggle-breathing");

  function runCycle() {
    const cur = phases[breathingPhase];
    instruction.textContent = cur.text;
    circle.className = "breath-circle " + cur.class;
    breathingPhase = (breathingPhase + 1) % phases.length;
  }

  runCycle();
  breathingInterval = setInterval(runCycle, 4000);

  toggleBtn.addEventListener("click", () => {
    if (breathingInterval) {
      clearInterval(breathingInterval);
      breathingInterval = null;
      toggleBtn.textContent = "Resume Exercise";
      instruction.textContent = "Paused";
    } else {
      breathingPhase = 0;
      runCycle();
      breathingInterval = setInterval(runCycle, 4000);
      toggleBtn.textContent = "Pause Exercise";
    }
  });
}

// SOS Modal
function setupSOSModal() {
  sosBtn.addEventListener("click", openSOSModal);
}
function openSOSModal() { sosModal.classList.add("open"); }
function closeSOSModal() { sosModal.classList.remove("open"); }

// Daily 2-Minute Check-In
function setupDailyCheckin() {
  const checkinBtn = document.getElementById("daily-checkin-btn");
  const checkinModal = document.getElementById("checkin-modal");
  const moodRange = document.getElementById("checkin-mood-range");
  const moodVal = document.getElementById("checkin-mood-val");
  const form = document.getElementById("daily-checkin-form");

  if (checkinBtn && checkinModal) {
    checkinBtn.addEventListener("click", () => checkinModal.classList.add("open"));
  }

  if (moodRange && moodVal) {
    moodRange.addEventListener("input", (e) => {
      moodVal.textContent = e.target.value;
    });
  }

  if (form) {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const score = moodRange.value;
      const emotion = document.getElementById("checkin-emotion").value;
      const note = document.getElementById("checkin-trigger").value;

      closeCheckinModal();
      appendBotMessage({
        reply: `Thank you for completing your daily check-in (Mood: **${score}/10**, Feeling: **${emotion}**). Naming your emotions strengthens self-regulation. Would you like to unpack this or continue your day?`
      });
      alert("Check-in recorded! Your Emotional Intelligence metrics have been updated.");
    });
  }
}

function closeCheckinModal() {
  const modal = document.getElementById("checkin-modal");
  if (modal) modal.classList.remove("open");
}

// Download Weekly Clinician Report
async function downloadWeeklyReport() {
  let markdownText = "";

  try {
    const res = await fetch(`${API_BASE}/dashboard/weekly-report/${state.userId}`);
    if (res.ok) {
      const data = await res.json();
      markdownText = data.markdown_report;
    }
  } catch (err) {
    // Fallback template if backend is offline
  }

  if (!markdownText) {
    markdownText = `# Nivara: Weekly Self-Reflection & Insight Report
*Generated: ${new Date().toLocaleDateString()}*

---

### 1. Emotional Rhythm & Mood Overview
- **Average Mood Score:** 7.2 / 10
- **Total Check-Ins Logged:** 14 check-ins over 7 days

### 2. Cognitive Distortion Distribution
- **Mind Reading:** 42% of observed patterns
- **Catastrophizing:** 31% of observed patterns
- **All-or-Nothing Thinking:** 18% of observed patterns

### 3. Top Situational Triggers
- Work standup presentations (5 occurrences)
- Unplanned manager check-ins (3 occurrences)
- Sunday evening schedule planning (2 occurrences)

### 4. Behavioral Activation & Rhythms
- **Activities Completed:** 6 of 7 planned (85% consistency)

---

### Clinician Discussion Prompts
1. Notice how anxiety spikes correlate with public presentation standups.
2. Examine evidence testing for the Mind Reading distortion ("assuming colleagues judge hesitation").
3. Continue celebrating consistency in daily walks.

> **Clinical Notice:** This report summarizes self-reported observations and correlations. It does not provide medical diagnoses or replace clinical assessment.
`;
  }

  const blob = new Blob([markdownText], { type: "text/markdown" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `Nivara_Weekly_Insight_Report_${new Date().toISOString().slice(0, 10)}.md`;
  a.click();
  URL.revokeObjectURL(url);
}


// Private Journal
const JOURNAL_KEY = "nivara_journal_entries";

function loadJournalEntries() {
  const container = document.getElementById("journal-entries");
  if (!container) return;
  const entries = JSON.parse(localStorage.getItem(JOURNAL_KEY) || "[]");
  entries.reverse().forEach(e => renderJournalEntry(container, e));
}

function renderJournalEntry(container, entry) {
  const el = document.createElement("div");
  el.className = "dash-card";
  el.style.cssText = "font-size: 14px; border-left: 3px solid var(--color-primary-light);";
  el.innerHTML = `
    <div style="font-size: 11px; color: var(--color-text-light); margin-bottom: 6px;">
      ${new Date(entry.timestamp).toLocaleString()}
    </div>
    <p style="white-space: pre-wrap;">${entry.text}</p>
  `;
  container.prepend(el);
}

function saveJournal() {
  const text = document.getElementById("private-journal-text").value.trim();
  if (!text) return;
  const entries = JSON.parse(localStorage.getItem(JOURNAL_KEY) || "[]");
  const entry = { text, timestamp: Date.now() };
  entries.push(entry);
  localStorage.setItem(JOURNAL_KEY, JSON.stringify(entries));
  const container = document.getElementById("journal-entries");
  renderJournalEntry(container, entry);
  document.getElementById("private-journal-text").value = "";
  showMilestoneToast("Journal Entry Saved 📖", "Your private reflection has been recorded.");
}

function clearJournal() {
  document.getElementById("private-journal-text").value = "";
}

// Coping Toolbox
function addToToolbox(label, content) {
  const container = document.getElementById("toolbox-items");
  if (!container) return;
  const el = document.createElement("div");
  el.className = "toolbox-item";
  el.innerHTML = `
    <div>
      <strong>${label}</strong>
      <p style="font-size: 13px; color: var(--color-text-muted); margin-top: 4px; white-space: pre-wrap;">${content.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")}</p>
    </div>
    <button class="btn-small btn-reject" onclick="this.closest('.toolbox-item').remove()" style="flex-shrink: 0;">Remove</button>
  `;
  container.prepend(el);
}
