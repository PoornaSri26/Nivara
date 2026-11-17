"""
State Machine & Agent Integration Tests.
Verifies distortion classification, True Memory proposals, Just Listen mode,
Clinician Rubric scoring, and the NivaraStateGraph pipeline.
"""

import unittest
from app.agents.graph import NivaraStateGraph
from app.agents.supervisor import SupervisorOrchestrator
from app.agents.state import ConversationState
from app.agents.reflection_agent import ReflectionAgent
from app.agents.just_listen_agent import JustListenAgent
from app.agents.evaluation_agent import EvaluationAgent
from app.memory.vector_search import VectorSearchService, cosine_similarity

class TestStateMachine(unittest.TestCase):
    def setUp(self):
        self.supervisor = SupervisorOrchestrator()
        self.graph = NivaraStateGraph()

    def test_distortion_detection(self):
        # 1. Catastrophizing & All-or-Nothing
        text = "Everything is completely ruined, this is the worst day of my entire life."
        distortions = ReflectionAgent.detect_distortions(text)
        distortion_names = [d["name"] for d in distortions]
        self.assertIn("Catastrophizing", distortion_names)
        self.assertIn("All-or-Nothing Thinking", distortion_names)

        # 2. Mind Reading
        text2 = "I know they all think I'm stupid and they hate working with me."
        distortions2 = ReflectionAgent.detect_distortions(text2)
        distortion_names2 = [d["name"] for d in distortions2]
        self.assertIn("Mind Reading", distortion_names2)

    def test_just_listen_mode_omits_advice(self):
        text = "I am just exhausted from working 70 hours a week and nobody appreciates it."
        state = ConversationState(
            session_id="test-session",
            user_id="test-user",
            current_mode="JUST_LISTEN",
            user_message=text
        )
        updated_state = self.graph.execute(state)
        reply = updated_state.agent_response.lower()

        # Should not instruct or prescribe
        self.assertNotIn("you should", reply)
        self.assertNotIn("here is what you need to do", reply)
        # Should contain empathetic validating language
        self.assertTrue(any(word in reply for word in ["hear", "exhausted", "valid", "with you", "holding space"]))

    def test_graph_grounding_flow(self):
        state = ConversationState(
            session_id="test-session",
            user_id="test-user",
            current_mode="GROUNDING",
            user_message="I'm feeling very overwhelmed physically"
        )
        updated_state = self.graph.execute(state)
        self.assertIn("Box Breathing", updated_state.agent_response)
        self.assertIn("Inhale deeply", updated_state.agent_response)

    def test_true_memory_proposes_goal_and_trigger(self):
        text = "I always get anxious before my team presentation and I want to practice public speaking."
        state = ConversationState(
            session_id="test-session",
            user_id="test-user",
            current_mode="GUIDED_CBT",
            user_message=text
        )
        updated_state = self.graph.execute(state)
        
        proposals = updated_state.proposed_memories
        self.assertGreaterEqual(len(proposals), 1)
        categories = [p["category"] for p in proposals]
        self.assertTrue("TRIGGER" in categories or "GOAL" in categories)

    def test_semantic_vector_memory_retrieval(self):
        user_memories = [
            {"id": "1", "content": "Anxiety triggered by public speaking and presentations", "status": "CONFIRMED"},
            {"id": "2", "content": "Enjoys gardening and walking in nature", "status": "CONFIRMED"},
            {"id": "3", "content": "Conflict with landlord over lease terms", "status": "PROPOSED"}  # Should be excluded because not confirmed
        ]
        query = "I have to give a talk in front of the whole company tomorrow and my hands are shaking"
        ranked = VectorSearchService.rank_memories(query, user_memories, top_k=1)
        self.assertEqual(len(ranked), 1)
        self.assertEqual(ranked[0]["id"], "1")
        self.assertIn("public speaking", ranked[0]["content"])

    def test_evaluation_agent_scoring(self):
        reply = "I hear how much pain you're in. That makes complete sense. Let's look at the evidence together."
        rubric = EvaluationAgent.evaluate_turn("I feel like a failure", reply, "GUIDED_CBT")
        self.assertGreaterEqual(rubric["composite_score"], 0.70)
        self.assertEqual(rubric["boundary_score"], 1.0)
        self.assertTrue(rubric["passes_rubric"])

if __name__ == "__main__":
    unittest.main()
