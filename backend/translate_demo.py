# ===== SETUP =====
# We import the necessary libraries
from typing import Literal, Optional
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field
import os

# ===== SETUP =====
# Just like filling out a form, we need to define what information we'll collect during translation.
# Think of these as specialised containers that make sure we don't lose any information along the way.
class Translation(BaseModel):
    text: str = Field(..., description="The text to translate")
    translation: str = Field(..., description="The translated text")

class Grade(BaseModel):
    # Like a report card: did the translation pass or fail, and why?
    grade: Literal["Pass", "Fail"] = Field(..., description="Pass or Fail")
    reasoning: str = Field(..., description="Reasoning for the grade")

class State(BaseModel):
    # This is like a tracking system that follows your package (text) through different stages:
    # 1. Original text
    # 2. Corrected English version (like spell-check)
    # 3. The Mandarin translation
    # 4. Quality check results
    text: str
    proofread_english: Optional[str] = None
    mandarin_translation: Optional[str] = None
    translation_quality: Optional[Literal["Pass", "Fail"]] = None
    translation_quality_reasoning: Optional[str] = None


class Translator:
    def __init__(self, model: str, api_key: str):
        self.model = model
        self.api_key = api_key
        self.llm = self._init_llm()
        self.workflow = self._init_workflow()

    def _init_llm(self):
        if self.model.startswith("claude"):
            os.environ["ANTHROPIC_API_KEY"] = self.api_key
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(
                model=self.model,
                temperature=0
            )
        elif self.model.startswith("gpt"):
            os.environ["OPENAI_API_KEY"] = self.api_key
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=self.model,
                temperature=0
            )
        elif self.model.startswith('llama'):
            os.environ["GROQ_API_KEY"] = self.api_key
            from langchain_groq import ChatGroq
            return ChatGroq(
                model=self.model,
                temperature=0
            )
        elif self.model.startswith('gemini'):
            os.environ["GOOGLE_API_KEY"] = self.api_key
            from langchain_google_generativeai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                model=self.model,
                temperature=0
            )
        else:
            raise ValueError(f"Unsupported model: {self.model}")
    
    def proofread_english(self, state: State) -> State:
        """Step 1: Check and fix any English grammar or spelling mistakes"""
        messages = [
            SystemMessage(content="You are an expert English editor. Catch any obvious editorial errors, and amend it without changing the substance of the word. Do not make stylistic changes. Do not include comments in your response. Return just the amended text."),
            HumanMessage(content=f"Proofread and improve this text: {state.text}")
        ]
        
        response = self.llm.invoke(messages)
        state.proofread_english = response.content
        return state

    def translate_to_mandarin(self, state: State) -> State:
        """Step 2: Translate the corrected English into Mandarin"""
        messages = [
            SystemMessage(content="You are an expert translator specialising in Simplified Chinese (Mandarin). Localise it to Singapore Mandarin."),
            HumanMessage(content=f"Translate this text to natural, fluent Mandarin: {state.proofread_english}")
        ]

        if state.translation_quality:
            messages.append(HumanMessage(content=f"Previous Grade: {state.translation_quality.grade}\nPrevious Reasoning: {state.translation_quality.reasoning}"))

        translation_llm = self.llm.with_structured_output(Translation)
        response = translation_llm.invoke(messages)
        state.mandarin_translation = response.translation
        return state

    def check_translation_quality(self, state: State) -> State:
        """Step 3: Have an expert check if the translation is good"""
        messages = [
            SystemMessage(content="You are a bilingual expert in English and Mandarin. Evaluate translation quality."),
            HumanMessage(content=f"""
            Original English: {state.proofread_english}
            Mandarin Translation: {state.mandarin_translation}
            
            Grade this translation as Pass or Fail and explain why. Format as JSON with 'grade' and 'reasoning' fields.
            """)
        ]
        
        grade_llm = self.llm.with_structured_output(Grade)
        response = grade_llm.invoke(messages)
        state.translation_quality = response.grade
        state.translation_quality_reasoning = response.reasoning
        return state
    
    def should_retry(self,state: State):
        """If the translation isn't good enough, should we try again?"""
        if state.translation_quality == "Fail":
            return "retry"
        return "end"

    def _init_workflow(self):
        workflow = StateGraph(State)
        
        # Add nodes
        workflow.add_node("proofread", self.proofread_english)
        workflow.add_node("translate", self.translate_to_mandarin)
        workflow.add_node("check_quality", self.check_translation_quality)
        
        # Create edges
        workflow.set_entry_point("proofread")
        workflow.add_edge("proofread", "translate")
        workflow.add_edge("translate", "check_quality")
        
        # Add conditional retry logic
        workflow.add_conditional_edges(
            "check_quality",
            self.should_retry,
            {
                "retry": "translate",
                "end": END
            }
        )
        
        return workflow.compile()

    def translate_text(self, text: str) -> dict:
        result = self.workflow.invoke({"text": text})
        return result

def create_translator(model: str, api_key: str) -> Translator:
    return Translator(model=model, api_key=api_key)