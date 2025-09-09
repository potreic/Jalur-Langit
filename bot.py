import os
import re
import random
import discord
from dotenv import load_dotenv

# Load Bot's Token
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("DISCORD_TOKEN not found. Check your .env file and variable name.")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Technology to career mapping with more specific roles
tech_to_career = {
    "python": ["Data Scientist", "Backend Developer", "Machine Learning Engineer", "Python Developer"],
    "javascript": ["Frontend Developer", "Fullstack Developer", "Web Developer", "JavaScript Developer"],
    "java": ["Enterprise Developer", "Android Developer", "Backend Engineer", "Java Developer"],
    "html": ["Frontend Developer", "Web Designer", "UI Developer"],
    "css": ["Frontend Developer", "Web Designer", "UI Developer"],
    "react": ["Frontend Developer", "React Developer", "UI Engineer"],
    "node": ["Backend Developer", "Fullstack Developer", "API Developer", "Node.js Developer"],
    "sql": ["Database Administrator", "Data Analyst", "Backend Developer", "Database Developer"],
    "aws": ["DevOps Engineer", "Cloud Architect", "Infrastructure Engineer", "Cloud Engineer"],
    "docker": ["DevOps Engineer", "Site Reliability Engineer", "Backend Developer"],
    "machine learning": ["Data Scientist", "ML Engineer", "AI Developer", "Machine Learning Specialist"],
    "cybersecurity": ["Security Analyst", "Ethical Hacker", "Security Engineer", "Cybersecurity Specialist"]
}

# Career to technology mapping
career_to_tech = {
    "web developer": ["HTML", "CSS", "JavaScript", "React", "Node.js"],
    "frontend developer": ["HTML", "CSS", "JavaScript", "React", "Vue", "Angular"],
    "backend developer": ["Python", "Java", "Node.js", "SQL", "API Development"],
    "data scientist": ["Python", "R", "SQL", "Machine Learning", "Statistics"],
    "devops engineer": ["AWS", "Docker", "Kubernetes", "CI/CD", "Linux"],
    "mobile developer": ["Swift", "Kotlin", "React Native", "Flutter", "Java"],
    "ui ux designer": ["Figma", "Sketch", "Adobe XD", "User Research", "Wireframing"]
}

# Enhanced job descriptions including specific roles from tech_to_career
job_descriptions = {
    "web developer": "Web developers build and maintain websites. They work on both the front-end (what users see) and back-end (server-side) components.",
    "frontend developer": "Frontend developers focus on the visual aspects of websites that users interact with. They use HTML, CSS, and JavaScript.",
    "backend developer": "Backend developers work on server-side logic, databases, and application integration. They ensure the frontend has data when needed.",
    "data scientist": "Data scientists analyze and interpret complex data to help organizations make decisions. They use statistics and machine learning.",
    "devops engineer": "DevOps engineers bridge development and operations teams. They automate processes and manage infrastructure.",
    "mobile developer": "Mobile developers create applications for smartphones and tablets, working with iOS or Android platforms.",
    "ui ux designer": "UI/UX designers focus on user experience and interface design. They create wireframes and prototypes.",
    "machine learning engineer": "Machine Learning Engineers design and implement machine learning applications and systems.",
    "ai developer": "AI Developers create artificial intelligence solutions, including natural language processing and computer vision systems.",
    "cloud architect": "Cloud Architects design and manage cloud computing strategies and infrastructure for organizations.",
    "security analyst": "Security Analysts protect computer systems and networks from cyber threats and security breaches.",
    "database administrator": "Database Administrators manage and maintain database systems, ensuring data integrity and availability.",
    "python developer": "Python Developers specialize in building applications using the Python programming language.",
    "javascript developer": "JavaScript Developers focus on building applications using JavaScript, both on frontend and backend.",
    "java developer": "Java Developers create applications using the Java programming language, often for enterprise systems.",
    "react developer": "React Developers specialize in building user interfaces using the React JavaScript library.",
    "node.js developer": "Node.js Developers build server-side applications using the Node.js JavaScript runtime.",
    "cloud engineer": "Cloud Engineers implement and maintain cloud infrastructure and services.",
    "cybersecurity specialist": "Cybersecurity Specialists protect systems and networks from digital attacks and threats.",
    "database developer": "Database Developers design and implement database solutions and write complex queries.",
    "ethical hacker": "Ethical Hackers test systems for vulnerabilities to help organizations improve their security.",
    "infrastructure engineer": "Infrastructure Engineers design and maintain the hardware and software infrastructure of organizations.",
    "ml engineer": "ML Engineers design, build, and deploy machine learning models and systems.",
    "machine learning specialist": "Machine Learning Specialists focus on developing and implementing ML algorithms and solutions.",
    "api developer": "API Developers design and build application programming interfaces for software systems.",
    "ui engineer": "UI Engineers implement user interfaces with a focus on both design and technical implementation."
}


    
def detect_tech(message):
    message_lower = message.lower()
    detected_tech = []
    
    for tech in tech_to_career:
        # Use word boundaries to ensure we're matching the whole word
        if re.search(r'\b' + re.escape(tech) + r'\b', message_lower):
            detected_tech.append(tech)
    
    return detected_tech

def detect_career(message):
    message_lower = message.lower()
    
    # More comprehensive career detection
    career_keywords = {
        "web developer": r"web.*dev|website.*dev|front.?end|back.?end|full.?stack|web.*programmer",
        "frontend developer": r"front.?end|ui.*dev|user.?interface|client.?side|front.*end",
        "backend developer": r"back.?end|server.?side|api.*dev|database.*dev|back.*end",
        "data scientist": r"data.*scien|machine.*learning|ai.*dev|artificial.*intelligence|analytics|ml.*engineer",
        "devops engineer": r"devops|deployment|infrastructure|cloud|aws|azure|ci.?cd|continuous",
        "mobile developer": r"mobile.*dev|ios.*dev|android.*dev|app.*dev|application.*dev|flutter|react.*native",
        "ui ux designer": r"ui.*design|ux.*design|user.*experience|user.*interface|design|ux.*ui|ui.*ux",
        "python developer": r"python.*dev|dev.*python",
        "javascript developer": r"javascript.*dev|js.*dev|dev.*javascript",
        "java developer": r"java.*dev|dev.*java",
        "react developer": r"react.*dev|dev.*react",
        "node.js developer": r"node.*dev|dev.*node",
        "cloud engineer": r"cloud.*engineer|engineer.*cloud",
        "cybersecurity specialist": r"cyber.*specialist|security.*specialist",
        "database administrator": r"database.*admin|db.*admin|dba",
        "machine learning engineer": r"ml.*engineer|machine.*learning.*engineer",
        "ai developer": r"ai.*dev|artificial.*intelligence.*dev",
        "cloud architect": r"cloud.*architect|architect.*cloud",
        "security analyst": r"security.*analyst|cyber.*analyst",
        "ethical hacker": r"ethical.*hacker|white.*hat|pen.*test",
        "infrastructure engineer": r"infrastructure.*engineer|engineer.*infrastructure",
        "api developer": r"api.*dev|dev.*api",
        "ui engineer": r"ui.*engineer|engineer.*ui"
    }
    
    detected_careers = []
    for career, pattern in career_keywords.items():
        if re.search(pattern, message_lower):
            detected_careers.append(career)
    
    return detected_careers

def get_response(message):
    message_lower = message.lower()

    absurd_inputs = ["hmm", "uh", "...", "hmmm", "hmm.", "hmm?", "umm", "hmm!", "hmm.."]
    career_keywords = ["career", "job", "skill", "technology", "tech", "learn", "become", "field", "role", "stack", "tools"]
    if any(message_lower.strip() == ai for ai in absurd_inputs):
        # Only respond if the message does NOT mention any career/skill keywords
        if not any(kw in message_lower for kw in career_keywords):
            return "Do you need help about careers or skills in IT fields?"

    # Exit condition
    if re.search(r'\b(exit|quit|bye|goodbye)\b', message_lower):
        return "Goodbye! 👋"
    
    # Thank you response
    if re.search(r'\b(thanks|thank you|appreciate it|thx)\b', message_lower):
        return "You're welcome! If you have more questions, feel free to ask me."
    
    # Greeting response
    if re.search(r'\b(hi|hello|hey|greetings|howdy|good|morning|evening|night)\b', message_lower):
        return "👋 Hello! I can help you with tech career guidance. "
    
    # Check if user is asking about careers for a technology
    career_tech_pattern = r'career|job|what.*do|pursue|with.*skill|become|path|opportunity|ca|profficent|pretty good|familiar|expert|know|knowledge|work|role|roles|field|field of|field in|field with'
    if re.search(career_tech_pattern, message_lower):
        techs = detect_tech(message)
        if techs:
            response = ""
            for tech in techs:
                careers = tech_to_career.get(tech, [])
                if careers:
                    response += f"With {tech.title()} skills, you could pursue these careers:\n"
                    for career in careers:
                        # Convert to lowercase to match our job_descriptions keys
                        career_lower = career.lower()
                        desc = job_descriptions.get(career_lower, "No description available.")
                        response += f"- {career}: {desc}\n"
                    response += "\n"
            return response if response else "I'm not sure which technology you're referring to. Could you specify?"
    
    # Check if user is asking about skills/technologies for a career
    career_query_pattern = r'skill|learn|need|require|what.*become|how.*become|technolog|tech|stack|tools|knowledge|study|want.*be|to be'
    if re.search(career_query_pattern, message_lower) or any(word in message_lower for word in ["become a", "to be a"]):
        careers = detect_career(message)
        if careers:
            response = ""
            for career in careers:
                techs = career_to_tech.get(career, [])
                if techs:
                    desc = job_descriptions.get(career, "No description available.")
                    response += f"To become a {career.title()}, you should learn these technologies:\n- " + "\n- ".join(techs) + f"\n\n{desc}\n\n"
            return response if response else "I'm not sure about that career path. Could you specify which tech career you're interested in?"
        else:
            # If we can't detect a specific career, provide general guidance
            return "If you're interested in a tech career, here are some common paths:\n\n" \
                   "• Web Development: HTML, CSS, JavaScript, React/Node.js\n" \
                   "• Data Science: Python, SQL, Machine Learning, Statistics\n" \
                   "• DevOps: AWS, Docker, Kubernetes, CI/CD\n" \
                   "• Mobile Development: iOS (Swift), Android (Kotlin/Java), Cross-platform (Flutter/React Native)\n\n" \
                   "Which specific career are you interested in?"
    
    # Default response for other queries
    return "I specialize in tech career guidance. You can ask me:\n• What skills do I need to become a [job title]?\n• What careers can I pursue with [technology] skills?"

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    response = get_response(message.content)
    if response:
        await message.channel.send(response)

client.run(TOKEN)