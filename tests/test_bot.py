import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import bot

# --- Mock Classes to Simulate Discord Objects ---
class MockChannel:
    """A mock Discord channel object that only has an ID."""
    def __init__(self, id):
        self.id = id

class MockMessage:
    """A mock Discord message object that has content and a channel."""
    def __init__(self, content, channel_id=12345):
        self.content = content
        self.channel = MockChannel(channel_id)

# --- Main Test Class ---
class TestBotLogic(unittest.TestCase):

    def setUp(self):
        """This method runs before each test. It's useful for clearing state."""
        bot.conversation_memory.clear()

    # --- TEST CASE 1: Simple Technology Detection ---
    def test_detect_tech_single_word(self):
        """Tests the detection of single-word technologies like 'python'."""
        detected = bot.detect_tech("i know python and java")
        self.assertIn("python", detected)
        self.assertIn("java", detected)

    # --- TEST CASE 2: Multi-Word Technology Detection ---
    def test_detect_tech_multi_word(self):
        """Tests the detection of multi-word technologies like 'machine learning'."""
        detected = bot.detect_tech("what about machine learning?")
        self.assertIn("machine learning", detected)

    # --- TEST CASE 3: Career Detection ---
    def test_detect_career(self):
        """Tests career detection for a role like 'devops engineer'."""
        detected = bot.detect_career("skills for a devops engineer")
        self.assertIn("devops engineer", detected)

    # --- TEST CASE 4: Intent Detection for 'ask_skills' ---
    def test_get_intent_ask_skills(self):
        """Tests if the 'ask_skills' intent is detected correctly."""
        intent = bot.get_intent("what skills do i need to be a data scientist")
        self.assertEqual(intent, "ask_skills")

    # --- TEST CASE 5: Full Flow for 'ask_skills' ---
    def test_get_response_ask_skills_successful(self):
        """Tests the full get_response flow for a skill-related question."""
        mock_message = MockMessage("what skills to be a data scientist?")
        response = bot.get_response(mock_message)
        self.assertIn("To become a **Data Scientist**", response)
        self.assertIn("Python (Pandas, NumPy)", response)

    # --- TEST CASE 6: Full Flow with Conversational Memory ---
    def test_get_response_follow_up_question(self):
        """Tests if the bot remembers the previous conversation (context memory)."""
        # First message to populate the memory
        msg1 = MockMessage("skills for frontend developer", channel_id=111)
        bot.get_response(msg1)

        # Second message (the follow-up)
        msg2 = MockMessage("what about backend developer?", channel_id=111)
        response = bot.get_response(msg2)
        
        self.assertIn("To become a **Backend Developer**", response)
        self.assertIn("SQL / NoSQL Databases", response)
        
    # --- TEST CASE 7: Fallback Response for Unknown Input ---
    def test_get_response_unknown_input(self):
        """Tests if the bot provides the default fallback response for unclear input."""
        mock_message = MockMessage("can you tell me a joke?")
        response = bot.get_response(mock_message)
        self.assertIn("I specialize in tech career guidance", response)

# This allows you to run the file directly
if __name__ == '__main__':
    unittest.main()