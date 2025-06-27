import logging
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from typing import List, Dict, Any, Optional
import os
import requests
from .config import current_config

logger = logging.getLogger(__name__)

class MistralChat:
    def __init__(self, model_name: str = None):
        """
        Initialize Mistral LLM for chat functionality.
        
        Args:
            model_name: Name of the Mistral model to use
        """
        config = current_config.get_llm_config()
        self.model_name = model_name or config["model_name"]
        self.max_length = config["max_length"]
        self.temperature = config["temperature"]
        self.use_gpu = config["use_gpu"]
        self.quantization = config["quantization"]
        
        self.tokenizer = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() and self.use_gpu else "cpu"
        self._load_model()
    
    def _load_model(self):
        """Load the Mistral model and tokenizer."""
        try:
            logger.info(f"Loading LLM model: {self.model_name}")
            logger.info(f"Using device: {self.device}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            
            # Add padding token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model with quantization for memory efficiency
            model_kwargs = {
                "torch_dtype": torch.float16 if self.device == "cuda" else torch.float32,
                "trust_remote_code": True
            }
            
            if self.device == "cuda":
                model_kwargs["device_map"] = "auto"
                if self.quantization:
                    model_kwargs["load_in_8bit"] = True
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                **model_kwargs
            )
            
            logger.info("LLM model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading LLM model: {e}")
            raise
    
    def create_prompt(self, query: str, context_docs: List[Dict[str, Any]]) -> str:
        """
        Create a prompt for the LLM with context and query.
        
        Args:
            query: User's question
            context_docs: Retrieved relevant documents
            
        Returns:
            Formatted prompt string
        """
        # Format context documents
        context_text = ""
        for i, doc in enumerate(context_docs, 1):
            metadata = doc['metadata']
            context_text += f"Document {i}:\n"
            context_text += f"Title: {metadata.get('title', 'N/A')}\n"
            context_text += f"PMID: {metadata.get('pmid', 'N/A')}\n"
            context_text += f"Content: {doc['text']}\n\n"
        
        # Create the prompt - simplified for DialoGPT
        prompt = f"Context: {context_text}\nQuestion: {query}\nAnswer:"
        
        return prompt
    
    def generate_response(self, query: str, context_docs: List[Dict[str, Any]], max_length: int = None) -> str:
        """
        Generate a response using DialoGPT LLM.
        
        Args:
            query: User's question
            context_docs: Retrieved relevant documents
            max_length: Maximum length of the response
            
        Returns:
            Generated response text
        """
        max_length = max_length or self.max_length
        
        try:
            # Create prompt
            prompt = self.create_prompt(query, context_docs)
            
            # Tokenize input
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=1024
            )
            
            # Move to device
            if self.device == "cuda":
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_length,
                    temperature=self.temperature,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract only the generated part (after the prompt)
            if prompt in response:
                response = response[len(prompt):].strip()
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Sorry, er is een fout opgetreden bij het genereren van het antwoord: {str(e)}"
    
    def chat(self, query: str, context_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Main chat function that generates a response with metadata.
        
        Args:
            query: User's question
            context_docs: Retrieved relevant documents
            
        Returns:
            Dictionary with response and metadata
        """
        try:
            response = self.generate_response(query, context_docs)
            
            return {
                'response': response,
                'query': query,
                'context_count': len(context_docs),
                'context_sources': [
                    {
                        'pmid': doc['metadata'].get('pmid'),
                        'title': doc['metadata'].get('title'),
                        'distance': doc['distance']
                    }
                    for doc in context_docs
                ]
            }
            
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return {
                'response': f"Er is een fout opgetreden: {str(e)}",
                'query': query,
                'context_count': 0,
                'context_sources': []
            }

class OllamaChat:
    def __init__(self, model_name: str = None, base_url: str = None):
        config = current_config
        self.model_name = model_name or getattr(config, "LLM_MODEL", "mistral")
        self.base_url = base_url or getattr(config, "OLLAMA_BASE_URL", "http://localhost:11434")
        self.max_length = getattr(config, "LLM_MAX_LENGTH", 1024)
        self.temperature = getattr(config, "LLM_TEMPERATURE", 0.7)

    def create_prompt(self, query: str, context_docs: List[Dict[str, Any]]) -> str:
        context_text = ""
        for i, doc in enumerate(context_docs, 1):
            metadata = doc['metadata']
            context_text += f"Document {i}:\n"
            context_text += f"Title: {metadata.get('title', 'N/A')}\n"
            context_text += f"PMID: {metadata.get('pmid', 'N/A')}\n"
            context_text += f"Content: {doc['text']}\n\n"
        
        prompt = f"""[INST] Je bent een wetenschappelijke AI assistent die helpt bij het beantwoorden van vragen over PubMed artikelen. 

BELANGRIJK: 
- Geef een grondig onderbouwd antwoord gebaseerd op de wetenschappelijke context
- Verwijs naar specifieke bevindingen uit de artikelen
- Als er tegenstrijdige informatie is, benoem dit
- Als de context onvoldoende informatie bevat, zeg dat eerlijk
- Gebruik een professionele, wetenschappelijke toon

Context uit {len(context_docs)} wetenschappelijke artikelen:
{context_text}

Vraag: {query}

Geef een gedetailleerd, wetenschappelijk onderbouwd antwoord: [/INST]"""
        return prompt

    def chat(self, query: str, context_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        # Limit context to first 5 documents for faster response
        context_docs = context_docs[:5]
        
        prompt = self.create_prompt(query, context_docs)
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_length
            }
        }
        try:
            response = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=300)
            response.raise_for_status()
            data = response.json()
            response_text = data.get("response", "[Ollama gaf geen antwoord terug]")
            
            return {
                'response': response_text,
                'query': query,
                'context_count': len(context_docs),
                'context_sources': [
                    {
                        'pmid': doc['metadata'].get('pmid'),
                        'title': doc['metadata'].get('title'),
                        'distance': doc.get('distance', 0.0)
                    }
                    for doc in context_docs
                ]
            }
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            return {
                'response': f"Sorry, er is een fout opgetreden bij het genereren van het antwoord via Ollama: {str(e)}",
                'query': query,
                'context_count': 0,
                'context_sources': []
            }

# Factory functie om juiste chat backend te kiezen

def get_chat_backend():
    backend = getattr(current_config, "LLM_BACKEND", "transformers")
    if backend == "ollama":
        return OllamaChat()
    else:
        return MistralChat() 