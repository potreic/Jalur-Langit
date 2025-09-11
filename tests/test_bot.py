import unittest
import sys
import os
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import bot 

# --- Configure logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename=os.path.join(os.path.dirname(__file__), "test.log"),
    filemode="w"
)

# --- Mock Discord-like classes ---
class MockChannel:
    def __init__(self, id):
        self.id = id

class MockMessage:
    def __init__(self, content, channel_id=12345):
        self.content = content
        self.channel = MockChannel(channel_id)


class TestBotLogic(unittest.TestCase):
    def setUp(self):
        """Clear memory before each test"""
        bot.conversation_memory.clear()

    def test_detect_tech_single_word(self):
        logging.info("1. Running test_detect_tech_single_word...")
        detected = bot.detect_tech("i know python and java")
        self.assertIn("python", detected)
        self.assertIn("java", detected)
        logging.info("PASSED")

    def test_detect_tech_multi_word(self):
        logging.info("2. Running test_detect_tech_multi_word...")
        detected = bot.detect_tech("what about machine learning?")
        self.assertIn("machine learning", detected)
        logging.info("PASSED")

    def test_detect_career(self):
        logging.info("3. Running test_detect_career...")
        detected = bot.detect_career("skills for a devops engineer")
        self.assertIn("devops engineer", detected)
        logging.info("PASSED")

    def test_get_intent_ask_skills(self):
        logging.info("4. Running test_get_intent_ask_skills...")
        intent = bot.get_intent("what skills do i need to be a data scientist")
        self.assertEqual(intent, "ask_skills")
        logging.info("PASSED")

    def test_get_response_ask_skills_successful(self):
        logging.info("5. Running test_get_response_ask_skills_successful...")
        mock_message = MockMessage("what skills to be a data scientist?")
        response = bot.get_response(mock_message)
        self.assertIn("To become a **Data Scientist**", response)
        self.assertIn("Python (Pandas, NumPy)", response)
        logging.info("PASSED")

    def test_get_response_follow_up_question(self):
        logging.info("6. Running test_get_response_follow_up_question...")
        # First message to set memory
        msg1 = MockMessage("skills for frontend developer", channel_id=111)
        bot.get_response(msg1)

        # Follow-up in same channel
        msg2 = MockMessage("what about backend developer?", channel_id=111)
        response = bot.get_response(msg2)
        self.assertIn("To become a **Backend Developer**", response)
        self.assertIn("SQL / NoSQL Databases", response)
        logging.info("PASSED")

    def test_get_response_unknown_input(self):
        logging.info("7. Running test_get_response_unknown_input...")
        mock_message = MockMessage("can you tell me a joke?")
        response = bot.get_response(mock_message)
        self.assertIn("I specialize in tech career guidance", response)
        logging.info("PASSED")


if __name__ == "__main__":
    unittest.main(verbosity=2)
