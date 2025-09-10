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
    if re.search(r'\bc#\b|\bc sharp\b', message_lower):
        detected_tech.append('c#')
    for tech in tech_to_career:
        if tech == 'c#':
            continue
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

def split_message(text, limit=2000):
    """
    Split `text` into a list of strings each <= limit characters.
    Prefer splitting at paragraph boundaries, then lines, then hard-slice if needed.
    """
    if not text:
        return []
    if len(text) <= limit:
        return [text]

    paragraphs = text.split("\n\n")
    chunks = []
    current = ""

    for p in paragraphs:
        candidate = (current + "\n\n" + p) if current else p
        if len(candidate) <= limit:
            current = candidate
        else:
            if current:
                chunks.append(current)
                current = ""
            # Paragraph too long -> split by lines
            if len(p) <= limit:
                current = p
            else:
                lines = p.split("\n")
                sub = ""
                for line in lines:
                    cand = (sub + "\n" + line) if sub else line
                    if len(cand) <= limit:
                        sub = cand
                    else:
                        if sub:
                            chunks.append(sub)
                            sub = ""
                        # If single line is still too long, hard-slice the line
                        for i in range(0, len(line), limit):
                            chunks.append(line[i:i+limit])
                if sub:
                    current = sub

    if current:
        chunks.append(current)

    # final safeguard: ensure all chunks <= limit
    final_chunks = []
    for ch in chunks:
        if len(ch) <= limit:
            final_chunks.append(ch)
        else:
            for i in range(0, len(ch), limit):
                final_chunks.append(ch[i:i+limit])
    return final_chunks

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

    # If you wanted stateless bot (no conversation memory), you can remove the memory logic.
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
                    response += f"To become a **{career.title()}**, you should learn:\n- " \
                                + "\n- ".join(techs) + f"\n\n*{desc}*\n\n"
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
                    response += f"With **{tech.title()}** skills, you could pursue these careers:\n\n"
                    for career in careers:
                        desc = job_descriptions.get(career.lower(), "No description available.")
                        response += f"- **{career}**: {desc}\n\n"
            if response:
                response += "Would you like more details about any of these careers? Just ask about a specific one!"
                return response
            else:
                return "I don't have career path data for that technology yet."
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
        chunks = split_message(response, limit=2000)
        try:
            for chunk in chunks:
                await message.channel.send(chunk)
        except discord.HTTPException:
            # fallback: send as text file if sending chunks still fails
            try:
                tmp_path = "long_response.txt"
                with open(tmp_path, "w", encoding="utf-8") as f:
                    f.write(response)
                await message.channel.send(file=discord.File(tmp_path))
            except Exception:
                await message.channel.send("Sorry — I couldn't send the full response because it's too long.")

if __name__ == "__main__":
    client.run(TOKEN)
