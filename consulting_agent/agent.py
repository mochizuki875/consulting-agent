"""
Multi-Agent Consultation System

The root_agent receives user questions, sends them simultaneously to
macedonian_agent and japanese_agent, and after receiving both responses,
objectively synthesizes them to present a final answer.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
from google.adk.models.lite_llm import LiteLlm

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# Model configuration
MODEL_NAME = os.getenv("MODEL_NAME", "ollama/gpt-oss:20b")
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:11434")


# Agent with Macedonian perspective
macedonian_agent = LlmAgent(
    name="macedonian_agent",
    model=LiteLlm(model=MODEL_NAME, api_base=API_BASE_URL),
    description="Assistant providing opinions from a Macedonian cultural perspective",
    instruction="""You are an assistant with Macedonian sensibilities.
Answer questions based on Macedonian culture, history, values, and lifestyle.
Emphasize uniquely Macedonian perspectives and viewpoints.
Keep your responses concise and clear, around 2-3 sentences for each language.

Provide your response in both English and Japanese using the following format:
【Macedonian】
[English response]
<Write your actual English response here>


[Japanese response]
<Write your actual Japanese response here (マケドニアの視点からの日本語回答)>""",
    output_key="macedonian_opinion"  # Save to session state
)

# Agent with Japanese perspective
japanese_agent = LlmAgent(
    name="japanese_agent",
    model=LiteLlm(model=MODEL_NAME, api_base=API_BASE_URL),
    description="Assistant providing opinions from a Japanese cultural perspective",
    instruction="""You are an assistant with Japanese sensibilities.
Answer questions based on Japanese culture, history, values, and lifestyle.
Emphasize uniquely Japanese perspectives and viewpoints.
Keep your responses concise and clear, around 2-3 sentences for each language.

Provide your response in both English and Japanese using the following format:
【Japanese】
[English response]
<Write your actual English response here>


[Japanese response]
<Write your actual Japanese response here (日本の視点からの日本語回答)>""",
    output_key="japanese_opinion"  # Save to session state
)

# Agent that executes both agents in parallel
parallel_consultation_agent = ParallelAgent(
    name="parallel_consultation",
    sub_agents=[macedonian_agent, japanese_agent],
    description="Collect opinions in parallel from both Macedonian and Japanese perspectives"
)

# Agent that synthesizes both opinions
synthesis_agent = LlmAgent(
    name="synthesis_agent",
    model=LiteLlm(model=MODEL_NAME, api_base=API_BASE_URL),
    description="Objectively integrates multiple cultural perspectives and provides a balanced final answer",
    instruction="""You are an objective assistant who respects cultural diversity.

The following opinions from two different cultural perspectives are provided:

**Macedonian Perspective:**
{macedonian_opinion}

**Japanese Perspective:**
{japanese_opinion}

Your role is to:
1. First, briefly summarize the key points of each perspective
2. Clarify commonalities and differences between the two
3. Provide an objective and balanced final view that incorporates both perspectives

Provide your response in both English and Japanese using the following structure:

[English Response]
- 【Macedonian Perspective】: (key points)
- 【Japanese Perspective】: (key points)
- 【Comprehensive View】: (objective conclusion integrating both perspectives)

[Japanese Response / 日本語での回答]
- 【マケドニア人の視点】: (要点)
- 【日本人の視点】: (要点)
- 【総合的な見解】: (両方の視点を統合した客観的な結論)

Be polite and easy to understand in both languages."""
)

# Main root_agent: executes parallel processing → synthesis processing in sequence
root_agent = SequentialAgent(
    name="root_agent",
    sub_agents=[parallel_consultation_agent, synthesis_agent],
    description="Coordinator that analyzes user questions from multiple cultural perspectives and provides integrated answers"
)
