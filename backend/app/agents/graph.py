"""
LangGraph-Style State Machine & Conditional Directed Graph for Nivara.
Nodes:
  1. safety_triage_node: Dual-gate out-of-band evaluation.
  2. router_node: Intent analysis & mode selection.
  3. cbt_node: Socratic cognitive exploration.
  4. just_listen_node: Non-directive validation.
  5. thought_record_node: 7-Column restructuring progression.
  6. grounding_node: Somatic regulation & breathing pacing.
  7. memory_node: Prospective pattern & goal extraction.
  8. guardrail_node: Post-generation boundary sanitizer.
  9. evaluation_node: Clinician rubric scoring.
"""

from typing import Dict, Any, Callable
from app.agents.state import ConversationState
from app.safety.orchestrator import SafetyOrchestrator
from app.agents.reflection_agent import ReflectionAgent
from app.agents.just_listen_agent import JustListenAgent
from app.agents.cbt_agent import CBTAgent
from app.agents.memory_agent import MemoryAgent
from app.agents.evaluation_agent import EvaluationAgent
from app.exercises.grounding import get_grounding_exercise

class NivaraStateGraph:
    def __init__(self, region: str = "US"):
        self.safety = SafetyOrchestrator(user_region=region)

    # Node 1: Safety Triage
    def node_safety_triage(self, state: ConversationState) -> ConversationState:
        assessment = self.safety.assess_input(state.user_message)
        if not assessment.is_safe:
            state.safety_halt = True
            state.agent_response = assessment.override_response or "Please contact emergency services."
            state.safety_payload = assessment.crisis_payload
            state.quick_replies = ["View Crisis Hotlines", "Emergency Help", "Return to Calm"]
        return state

    # Node 2: Reflection & Distortions
    def node_reflection(self, state: ConversationState) -> ConversationState:
        if state.safety_halt:
            return state
        detected = ReflectionAgent.detect_distortions(state.user_message)
        state.detected_distortions = [d["name"] for d in detected]
        state.identified_triggers = ReflectionAgent.extract_triggers(state.user_message)
        return state

    # Node 3: Dispatcher / Mode Execution
    def node_cbt_flow(self, state: ConversationState) -> ConversationState:
        if state.safety_halt:
            return state

        if state.current_mode == "JUST_LISTEN":
            state.agent_response = JustListenAgent.respond(state.user_message)
            state.quick_replies = ["Keep talking", "Switch to Guided CBT", "I feel heard"]

        elif state.current_mode == "THOUGHT_RECORD":
            step_res = CBTAgent.process_step(
                current_step=state.exercise_step or "SITUATION",
                user_input=state.user_message,
                detected_distortions=state.detected_distortions
            )
            state.agent_response = step_res["reply"]
            state.exercise_step = step_res["next_step"]
            state.quick_replies = step_res["suggested_replies"]

        elif state.current_mode == "GROUNDING":
            exercise = get_grounding_exercise("BOX_BREATHING")
            state.agent_response = (
                f"### {exercise['title']}\n"
                f"{exercise['rationale']}\n\n"
                + "\n".join(f"- {s}" for s in exercise["instructions"])
            )
            state.quick_replies = ["Start Pacer", "Done Breathing", "Back to Conversation"]

        else: # Default Guided CBT
            reflection = ReflectionAgent.generate_balanced_perspective(state.user_message, state.detected_distortions)
            memory_note = ""
            if state.relevant_memories:
                first = state.relevant_memories[0]
                memory_note = f"\n\n*(Earlier, you mentioned {first.get('content', '')}. Does that feel relevant here?)*"
            
            state.agent_response = f"{reflection}{memory_note}\n\nWould you like to examine this in a **Thought Record**, try **Grounding**, or talk it through?"
            state.quick_replies = ["Start Thought Record", "Try Box Breathing", "Just listen to me", "Keep exploring"]

        return state

    # Node 4: Memory Extraction
    def node_memory_extraction(self, state: ConversationState) -> ConversationState:
        if state.safety_halt:
            return state
        proposals = MemoryAgent.extract_prospective_memories(state.user_message, state.detected_distortions)
        state.proposed_memories.extend(proposals)
        return state

    # Node 5: Output Guardrail & Clinician Rubric
    def node_guardrail_and_eval(self, state: ConversationState) -> ConversationState:
        if not state.safety_halt:
            state.agent_response = self.safety.assess_output(state.agent_response)
            rubric = EvaluationAgent.evaluate_turn(state.user_message, state.agent_response, state.current_mode)
            state.clinical_rubric_score = rubric["composite_score"]
        return state

    # Graph Execution Pipeline
    def execute(self, initial_state: ConversationState) -> ConversationState:
        state = self.node_safety_triage(initial_state)
        if state.safety_halt:
            return state

        state = self.node_reflection(state)
        state = self.node_cbt_flow(state)
        state = self.node_memory_extraction(state)
        state = self.node_guardrail_and_eval(state)
        return state

