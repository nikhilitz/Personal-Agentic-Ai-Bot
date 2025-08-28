# /Users/nikhilgupta/Desktop/Mem0nic/nodes/generate_mail.py
import os
import json
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate
from langchain.prompts.chat import SystemMessagePromptTemplate, HumanMessagePromptTemplate

load_dotenv()

def generate_mail_with_llm(state):
    """
    Generates a professional email for a job application using LLM.
    """
    if not hasattr(state, "company_description") or not state.company_description:
        raise ValueError("MemeBotState.company_description must be set.")
    if not hasattr(state, "designation") or not state.designation:
        raise ValueError("MemeBotState.designation must be set.")
    
    cv_text = """
    NIKHIL GUPTA
    Deoria, UP | gptnikhill@gmail.com | +918948100690 | LinkedIn | GitHub | LeetCode | Portfolio: https://nikhil-portfolio-umber-ten.vercel.app/
    Career Snapshot
    Aspiring AI & Data Science Engineer and CSE undergraduate at IIIT Tiruchirappalli, seeking opportunities to leverage Generative AI, Agentic AI,
    Machine Learning, Data Science, computer vision, NLP, and LLMs to build intelligent, data-driven solutions that solve complex real-world
    problems and enhance digital experiences.
    Education
    Indian Institute of Information Technology, Tiruchirappalli | B.Tech, CSE (Expected 2026) | CGPA: 8+
    Technical Skills
    ● Languages & Databases: Python, C++, SQL, JavaScript, HTML, CSS
    ● AI/ML: PyTorch, TensorFlow, Scikit-learn, Hugging Face, LangChain, LangGraph,LangSmith, OpenCV
    ● Development: React, FastAPI, Docker, Streamlit, Git, Jupyter
    ● Focus Areas: Computer Vision, NLP, LLMs, RAG Pipelines, Data Analysis
    Experience
    Junior AI Intern | Finch ● JULY 2025
    ● Built a real-time AI surveillance system for RTSP streams using ArcFace (facial recognition, 75% → 85% TPR@FAR optimization) and
    YOLOv8 (threat detection).
    ● Enhanced recognition via Bayesian hyperparameter optimization and face-size filtering, achieving a 10%+ performance lift in real-world
    conditions.
    ● Integrated Agentic AI workflows with LangGraph, enabling automated alerts and decision-making (restricted-area entry → instant email
    alerts).
    ● Engineered a scalable pipeline with FAISS indexing for fast retrieval, PostgreSQL for event logging, and FastAPI for secure access,
    ensuring production readiness.
    ● Tech Stack: Python | ArcFace | YOLOv8 | FAISS | PostgreSQL | FastAPI | LangGraph | OpenCV | NLP
    CONTRIBUTOR - AI & ML RESEARCH CLUB
    ● Conducted a technical workshop on “Attention Is All You Need” for 50+ students
    Projects
    ● Vehicle Monitor System [ Visit Repo ]
    ○ Real-time system tracking where a vehicle was detected, by which camera, and at what time.
    ○ Supports human-friendly queries with a heuristic-based parser for fast insights.
    ○ Tech: Python | OpenCV | YOLOv8 | Pandas | Numpy | Flask | NLP
    ● Vision.ai [ Visit Repo ]
    ○ AI-powered image captioning with speech, helping visually impaired users understand images.
    ○ Uses CNN + Transformer models for accurate caption generation in a web app.
    ○ Tech: Python | PyTorch | CNN + Transformer | gTTS / PyTTSx3 | Streamlit
    ● AskTube [ Visit Repo ]
    ○ YouTube Q&A assistant delivering fast, context-aware answers from videos using a RAG pipeline.
    ○ Efficient semantic search via FAISS for accurate information retrieval.
    ○ Tech: Python | LangChain | FAISS | OpenAI API | YouTube API | Streamlit
    Achievements & Certifications
    ● Google Cloud Certified: Generative AI | APR 2024
    ● Ethical Hacking Program, Physics Wallah | DEC 2024
    ● Solved 250+ problems on LeetCode
    ● AI & ML Bootcamp (Udemy) Certified | JULY 2024
    """

    api_key = os.getenv("OPENAI_API_KEY")
    api_base = os.getenv("OPENAI_API_BASE")

    llm = ChatOpenAI(
        model_name="provider-6/gpt-5-nano",
        temperature=0.7,
        openai_api_key=api_key,
        openai_api_base=api_base,
    )
    
    system_prompt_template = """
    You are a professional assistant for generating job application emails. 
    You will be provided with a company description, a job designation, and a user's CV.
    Your task is to write a concise and professional email expressing interest in the position.
    The email should be well-structured.
    Do NOT mention the CV is "attached," as it will be sent in a separate action.
    
    You MUST respond with a JSON object containing two keys: "subject" and "body".
    DO NOT include any other text or explanation. The response should be ONLY the JSON object.
    """
    
    human_prompt_template = """
    Company Description: {company_description}
    Job Designation: {designation}
    User's CV: {cv}
    """
    
    chat_prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_prompt_template),
        HumanMessagePromptTemplate.from_template(human_prompt_template)
    ])
    
    formatted_prompt = chat_prompt.format_messages(
        company_description=state.company_description,
        designation=state.designation,
        cv=cv_text
    )

    response = llm.invoke(formatted_prompt)
    raw_text = response.content

    try:
        cleaned_text = raw_text.strip()
        
        if cleaned_text.startswith("```json") and cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[7:-3].strip()

        json_response = json.loads(cleaned_text)
        state.mail_subject = json_response["subject"].strip()
        state.mail_body = json_response["body"].strip()
        print(f"✅ Email generated for {state.designation} at {state.company_email_id}")
    except (json.JSONDecodeError, KeyError) as e:
        print(f"DEBUG: Raw LLM response was:\n---\n{raw_text}\n---")
        raise ValueError(f"LLM response format is incorrect. Failed to parse JSON: {e}")
    
    return state
