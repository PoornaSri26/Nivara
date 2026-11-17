"""
Supervisor Orchestrator: Master LangGraph-Style State Machine.
Coordinates:
1. Safety Orchestrator (Dual-Gate)
2. Reflection Agent (Cognitive Distortions & Triggers)
3. Memory Agent (True Memory retrieval & proposals)
4. Dispatcher: Just Listen vs. CBT Thought Record vs. Guided CBT
5. Safety Output Guardrail
6. Evaluation Agent Quality Auditing
"""

from typing import Dict, Any, List
from app.agents.state import ConversationState
from app.safety.orchestrator import SafetyOrchestrator
from app.agents.reflection_agent import ReflectionAgent
from app.agents.just_listen_agent import JustListenAgent
from app.agents.cbt_agent import CBTAgent
from app.agents.memory_agent import MemoryAgent
from app.agents.evaluation_agent import EvaluationAgent

class SupervisorOrchestrator:
    def __init__(self, region: str = "US"):
        self.safety = SafetyOrchestrator(user_region=region)

    def process_turn(self, state: ConversationState) -> ConversationState:
        user_text = state.user_message.strip()

        # Step 1: Safety Assessment (Out-of-band Gate 1 & Gate 2)
        safety_eval = self.safety.assess_input(user_text)
        if not safety_eval.is_safe:
            state.safety_halt = True
            state.agent_response = safety_eval.override_response or "Please reach out to emergency resources."
            state.safety_payload = safety_eval.crisis_payload
            state.quick_replies = ["View Crisis Hotlines", "Exit to Safety Mode", "I am safe now"]
            return state

        # Step 2: Cognitive Distortion & Trigger Analysis
        detected = ReflectionAgent.detect_distortions(user_text)
        state.detected_distortions = [d["name"] for d in detected]
        state.identified_triggers = ReflectionAgent.extract_triggers(user_text)

        # Step 3: True Memory Extraction (Proposals)
        new_proposals = MemoryAgent.extract_prospective_memories(user_text, state.detected_distortions)
        state.proposed_memories.extend(new_proposals)

        # Step 4: Dispatcher based on Mode
        if state.current_mode == "JUST_LISTEN":
            reply = JustListenAgent.respond(user_text)
            state.quick_replies = [
                "Keep talking", 
                "Switch to a structured exercise", 
                "I feel heard, thank you"
            ]
        elif state.current_mode == "THOUGHT_RECORD":
            cbt_step_result = CBTAgent.process_step(
                current_step=state.exercise_step or "SITUATION",
                user_input=user_text,
                detected_distortions=state.detected_distortions
            )
            reply = cbt_step_result["reply"]
            state.exercise_step = cbt_step_result["next_step"]
            state.quick_replies = cbt_step_result["suggested_replies"]
        else: # "GUIDED_CBT" default
            reflection = ReflectionAgent.generate_balanced_perspective(user_text, state.detected_distortions)
            
            # Incorporate memory continuity if available
            memory_context = ""
            if state.relevant_memories:
                first_mem = state.relevant_memories[0]
                memory_context = f"\n\n*(Earlier, you noted {first_mem.get('content', '')}. Does that feel connected here?)*"

            reply = f"{reflection}{memory_context}\n\nWould you like to examine this in a **7-Column Thought Record**, try a **Grounding Exercise**, or just talk it through?"
            state.quick_replies = [
                "Start Thought Record",
                "Try Box Breathing",
                "Just listen to me",
                "Tell me more about this pattern"
            ]

        # Step 5: Output Guardrail Check
        sanitized_reply = self.safety.assess_output(reply)
        state.agent_response = sanitized_reply

        # Step 6: Evaluation Agent
        rubric = EvaluationAgent.evaluate_turn(user_text, sanitized_reply, state.current_mode)
        state.clinical_rubric_score = rubric["composite_score"]

        return state

