import os
import re
import discord
from dotenv import load_dotenv
from knowledge_base import *

# Load Bot's Token
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("DISCORD_TOKEN not found. Check your .env file and variable name.")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

conversation_memory = {}

def detect_tech(message):
    message_lower = message.lower()
    detected_tech = []
    
    # Handle C# separately first
    if re.search(r'\bc#\b|\bc sharp\b', message_lower):
        detected_tech.append('c#')
    
    # Check for all other technologies
    for tech in tech_to_career:
        if tech == 'c#':  # Skip C# as we already handled it
            continue
        
        # Create pattern based on whether the tech has spaces
        if ' ' in tech:
            pattern = r'{}'.format(re.escape(tech))
        else:
            pattern = r'\b{}\b'.format(re.escape(tech))
            
        if re.search(pattern, message_lower):
            detected_tech.append(tech)
    
    return list(set(detected_tech))

def detect_career(message):
    message_lower = message.lower()
    detected_careers = []
    for career, pattern in career_keywords.items():
        if re.search(pattern, message_lower):
            detected_careers.append(career)
    return detected_careers

def get_intent(message_lower):
    scores = {intent: 0 for intent in intent_keywords}
    for intent, patterns in intent_keywords.items():
        for pattern in patterns:
            if re.search(pattern, message_lower):
                scores[intent] += 1
    best_intent = max(scores, key=scores.get)
    return best_intent if scores[best_intent] > 0 else None

def prioritize_careers(detected_careers):
    careers_set = set(detected_careers)
    for high_priority, low_priority in career_priorities:
        if high_priority in careers_set and low_priority in careers_set:
            careers_set.discard(low_priority)
    return list(careers_set)

def get_response(message):
    message_lower = message.content.lower()
    channel_id = message.channel.id

    if re.search(r'\b(exit|quit|bye|goodbye)\b', message_lower):
        conversation_memory.pop(channel_id, None)
        return "Goodbye! 👋"
    
    if re.search(r'\b(thanks|thank you|appreciate it|thx)\b', message_lower):
        return "You're welcome! If you have more questions, feel free to ask."
    if re.search(r'\b(hi|hello|hey|greetings|howdy)\b', message_lower):
        return "👋 Hello! I can help you with tech career guidance."

    intent = get_intent(message_lower)
    detected_techs = detect_tech(message.content)
    detected_careers = detect_career(message.content)
    
    last_intent = conversation_memory.get(channel_id)
    if not intent and (detected_careers or detected_techs) and last_intent:
        intent = last_intent

    if intent == 'ask_skills':
        conversation_memory[channel_id] = 'ask_skills'
        prioritized_careers = prioritize_careers(detected_careers)
        if prioritized_careers:
            response = ""
            for career in prioritized_careers:
                techs = career_to_tech.get(career, [])
                if techs:
                    desc = job_descriptions.get(career, "")
                    response += f"To become a **{career.title()}**, you should learn:\n- " + "\n- ".join(techs) + f"\n\n*{desc}*\n\n"
            return response or "I don't have specific skill data for that career path yet."
        else:
            return "I can help with that! Which specific tech career are you interested in learning the skills for?"

    if intent == 'ask_careers':
        conversation_memory[channel_id] = 'ask_careers'
        if detected_techs:
            response = ""
            for tech in detected_techs:
                careers = tech_to_career.get(tech, [])
                if careers:
                    response += f"With **{tech.title()}** skills, you could pursue these careers:\n"
                    for career in careers:
                        # Find the career key (case-insensitive match)
                        career_key = next((k for k in job_descriptions.keys() if k.lower() == career.lower()), career)
                        desc = job_descriptions.get(career_key, "No description available.")
                        response += f"- **{career}**: {desc}\n"
                    response += "\n"
            return response or "I don't have career path data for that technology yet."
        else:
            return "I can definitely help with career paths. Which technology or skill are you proficient in?"
    
    if message_lower.strip() in acknowledgment_phrases and channel_id in conversation_memory:
        return "Great! Do you have any other questions about tech careers?"
            
    conversation_memory.pop(channel_id, None)
    return "I specialize in tech career guidance. You can ask me:\n• What skills do I need to become a [job title]?\n• What careers can I pursue with [technology] skills?"

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    response = get_response(message)
    if response:
        await message.channel.send(response)

if __name__ == "__main__":
    client.run(TOKEN)