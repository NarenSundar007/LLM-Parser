import json
import re
from typing import Dict, Any, List
from loguru import logger

from .models import ParsedQuery, QueryIntent
from .config import settings

class LLMParser:
    """Handles query parsing and logic evaluation using Groq or OpenAI LLM."""
    
    def __init__(self):
        self.provider = settings.llm_provider
        self.model = settings.llm_model
        self.temperature = settings.temperature
        self.max_tokens = settings.max_tokens
        
        if self.provider == "groq":
            try:
                # Try different import methods for Groq
                try:
                    from groq import Groq
                    import httpx
                    
                    # Create custom HTTP client to avoid proxy issues
                    custom_client = httpx.Client()
                    
                    # Initialize without proxy settings to avoid conflicts
                    self.client = Groq(
                        api_key=settings.groq_api_key,
                        http_client=custom_client
                    )
                    logger.info(f"Initialized Groq client with model: {self.model}")
                except (ImportError, AttributeError, TypeError) as e:
                    # Handle different groq package versions and proxy issues
                    logger.warning(f"Standard Groq import failed: {e}, trying alternative")
                    import groq
                    if hasattr(groq, 'Client'):
                        self.client = groq.Client(api_key=settings.groq_api_key)
                    elif hasattr(groq, 'Groq'):
                        self.client = groq.Groq(api_key=settings.groq_api_key)
                    else:
                        raise ImportError("Cannot find Groq client class")
                    logger.info(f"Initialized Groq client (alternative) with model: {self.model}")
            except Exception as e:
                logger.error(f"Failed to initialize Groq: {e}")
                # Fall back to OpenAI if available
                if settings.openai_api_key:
                    try:
                        self.provider = "openai"
                        from openai import OpenAI
                        # Initialize OpenAI without proxy settings to avoid conflicts
                        self.client = OpenAI(
                            api_key=settings.openai_api_key,
                            # Remove any proxy-related parameters
                        )
                        self.model = "gpt-3.5-turbo"
                        logger.warning("Falling back to OpenAI due to Groq initialization error")
                    except Exception as openai_error:
                        logger.error(f"OpenAI initialization also failed: {openai_error}")
                        self.provider = "fallback"
                        self.client = None
                        logger.warning("Using fallback mode - limited functionality")
                else:
                    # Use fallback mode without external APIs
                    self.provider = "fallback"
                    self.client = None
                    logger.warning("Using fallback mode - limited functionality")
        else:
            try:
                from openai import OpenAI
                # Initialize OpenAI without proxy settings
                self.client = OpenAI(
                    api_key=settings.openai_api_key,
                    # Remove any proxy-related parameters
                )
                logger.info(f"Initialized OpenAI client with model: {self.model}")
            except Exception as openai_error:
                logger.error(f"OpenAI initialization failed: {openai_error}")
                self.provider = "fallback"
                self.client = None
                logger.warning("Using fallback mode - limited functionality")
    
    async def parse_query(self, query: str, context: Dict[str, Any] = None) -> ParsedQuery:
        """Parse natural language query into structured format."""
        
        system_prompt = """You are an expert query parser for document analysis systems.
Your task is to analyze user queries and extract structured information.

Parse the user query and return a JSON object with these fields:
- intent: One of [coverage_check, eligibility, compliance, definition, procedure, general]
- target_subject: The main subject/topic of the query
- filter_conditions: List of conditions or filters mentioned
- keywords: Important keywords for semantic search

Examples:
Query: "Does this policy cover knee surgery?"
Response: {
    "intent": "coverage_check",
    "target_subject": "knee surgery",
    "filter_conditions": [],
    "keywords": ["policy", "cover", "knee surgery", "medical procedure"]
}

Query: "What are the eligibility requirements for dental coverage for employees over 50?"
Response: {
    "intent": "eligibility", 
    "target_subject": "dental coverage",
    "filter_conditions": ["employees over 50"],
    "keywords": ["eligibility", "requirements", "dental coverage", "employees", "age 50"]
}

Return only valid JSON, no additional text."""

        user_prompt = f"Query: {query}"
        if context:
            user_prompt += f"\nContext: {json.dumps(context)}"
        
        try:
            response = await self._call_llm(system_prompt, user_prompt)
            
            # Clean and parse JSON response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            # Parse JSON response
            parsed_data = json.loads(response)
            
            # Validate and create ParsedQuery object
            return ParsedQuery(
                intent=QueryIntent(parsed_data.get("intent", "general")),
                target_subject=parsed_data.get("target_subject", ""),
                filter_conditions=parsed_data.get("filter_conditions", []),
                keywords=parsed_data.get("keywords", []),
                original_query=query
            )
            
        except Exception as e:
            logger.error(f"Failed to parse query: {str(e)}")
            # Fallback to basic parsing
            return self._fallback_parse(query)
    
    def _fallback_parse(self, query: str) -> ParsedQuery:
        """Fallback parsing when LLM fails."""
        logger.warning("Using fallback query parsing")
        
        # Simple keyword-based intent detection
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["cover", "coverage", "covers", "include"]):
            intent = QueryIntent.COVERAGE_CHECK
        elif any(word in query_lower for word in ["eligible", "eligibility", "qualify"]):
            intent = QueryIntent.ELIGIBILITY
        elif any(word in query_lower for word in ["comply", "compliance", "regulation"]):
            intent = QueryIntent.COMPLIANCE
        elif any(word in query_lower for word in ["define", "definition", "what is", "meaning"]):
            intent = QueryIntent.DEFINITION
        elif any(word in query_lower for word in ["procedure", "process", "how to", "steps"]):
            intent = QueryIntent.PROCEDURE
        else:
            intent = QueryIntent.GENERAL
        
        # Extract basic keywords
        keywords = re.findall(r'\b\w+\b', query)
        keywords = [k for k in keywords if len(k) > 2]  # Filter short words
        
        return ParsedQuery(
            intent=intent,
            target_subject=query[:100],  # Use first 100 chars as subject
            filter_conditions=[],
            keywords=keywords,
            original_query=query
        )
    
    async def evaluate_logic(self, query: str, relevant_clauses: List[str], 
                           context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Evaluate whether clauses answer the query and provide reasoning."""
        
        system_prompt = """You are an expert document analyst specializing in policy and legal document interpretation.
Your task is to evaluate whether given clauses answer a user's query and provide detailed reasoning.

Analyze the query and relevant clauses, then return a JSON object with:
- answer: Direct yes/no/partial answer to the query
- meets_criteria: Boolean indicating if the query is fully answered
- applicable_conditions: List of conditions that apply
- rationale: Detailed explanation of your reasoning
- confidence_score: Float between 0-1 indicating confidence
- supporting_evidence: List of specific text snippets that support the answer

Be precise, factual, and cite specific clause text in your reasoning."""

        clauses_text = "\n\n".join([f"Clause {i+1}: {clause}" for i, clause in enumerate(relevant_clauses)])
        
        user_prompt = f"""Query: {query}

Relevant Clauses:
{clauses_text}

Context: {json.dumps(context) if context else "None"}

Provide your analysis as JSON only."""

        try:
            response = await self._call_llm(system_prompt, user_prompt)
            
            # Clean and parse JSON response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            return json.loads(response)
            
        except Exception as e:
            logger.error(f"Failed to evaluate logic: {str(e)}")
            return self._fallback_logic_evaluation(query, relevant_clauses)
    
    async def parse_and_evaluate_combined(self, query: str, relevant_clauses: List[str]) -> Dict[str, Any]:
        """Combined parsing and evaluation in one API call for accuracy."""
        
        system_prompt = """You are an expert insurance policy document analyst. Parse the query AND evaluate the clauses in ONE response.

CRITICAL INSTRUCTIONS:
- Extract EXACT numbers, time periods, percentages, and amounts from the document
- For waiting periods: State the EXACT number (e.g., "30 days", "36 months", "2 years")
- For percentages: Include the EXACT percentage (e.g., "5%", "10%") 
- For definitions: Include ALL technical criteria and requirements mentioned
- For sub-limits: Include EXACT percentages and amounts
- For conditions: List ALL conditions, not just summaries

Return ONLY a valid JSON object with these exact fields:
- intent: One of [coverage_check, eligibility, compliance, definition, procedure, general]
- target_subject: Main subject/topic of the query  
- answer: Complete answer as a SINGLE STRING with ALL specific details, numbers, percentages, and time periods
- applicable_conditions: List of condition strings with exact details
- confidence_score: Float between 0-1 indicating confidence

IMPORTANT: 
- Return ONLY the JSON object. No additional text, explanations, or comments.
- The "answer" field must be a STRING, never an object or nested structure
- Be COMPLETE and ACCURATE. Include ALL relevant details from the document."""

        clauses_text = "\n\n".join([f"Clause {i+1}: {clause}" for i, clause in enumerate(relevant_clauses[:3])])  # Use complete clause text and 3 clauses
        
        user_prompt = f"""Query: {query}

Top Relevant Clauses from Insurance Policy:
{clauses_text}

Analyze the query against these clauses and provide comprehensive analysis as JSON only. Include ALL exact numbers, time periods, percentages, and technical details mentioned in the clauses."""

        try:
            response = await self._call_llm(system_prompt, user_prompt, timeout=15)  # Increased timeout for thorough analysis
            
            # Clean and parse JSON response more aggressively
            response = response.strip()
            
            # Remove code block markers
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            
            # Find the first { and last } to extract just the JSON
            try:
                start_idx = response.find('{')
                end_idx = response.rfind('}')
                if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
                    response = response[start_idx:end_idx+1]
                
                response = response.strip()
                result = json.loads(response)
            except (json.JSONDecodeError, ValueError) as json_error:
                logger.warning(f"Initial JSON parsing failed: {json_error}, trying line-by-line cleanup")
                
                # More aggressive cleanup - split by lines and reconstruct JSON
                lines = response.split('\n')
                json_lines = []
                in_json = False
                brace_count = 0
                
                for line in lines:
                    stripped_line = line.strip()
                    if stripped_line.startswith('{'):
                        in_json = True
                        brace_count += stripped_line.count('{') - stripped_line.count('}')
                        json_lines.append(stripped_line)
                    elif in_json:
                        brace_count += stripped_line.count('{') - stripped_line.count('}')
                        json_lines.append(stripped_line)
                        if brace_count <= 0:
                            break
                
                if json_lines:
                    clean_json = '\n'.join(json_lines)
                    result = json.loads(clean_json)
                else:
                    raise json.JSONDecodeError("Could not extract valid JSON", response, 0)
            
            # Ensure all required fields
            defaults = {
                "intent": "general",
                "target_subject": query[:50],
                "answer": "Unable to determine",
                "applicable_conditions": [],
                "confidence_score": 0.5
            }
            
            for key, default_value in defaults.items():
                if key not in result:
                    result[key] = default_value
            
            return result
            
        except Exception as e:
            logger.error(f"Combined parse and evaluate failed: {str(e)}")
            return {
                "intent": "general",
                "target_subject": query[:50],
                "answer": "Unable to process query",
                "applicable_conditions": [],
                "confidence_score": 0.0
            }
    
    async def generate_fast_response(self, query: str, combined_analysis: Dict[str, Any], best_clause: str) -> Dict[str, Any]:
        """Generate comprehensive final response using combined analysis."""
        
        system_prompt = """Generate final comprehensive answer as a valid JSON object.

CRITICAL INSTRUCTIONS:
- Include ALL exact numbers, time periods, percentages from the analysis
- For waiting periods: State EXACT duration (e.g., "30 days", "36 months", "2 years")  
- For percentages: Include EXACT percentage values (e.g., "5%", "10%")
- For definitions: Include ALL technical criteria and requirements
- For sub-limits: Include EXACT percentage limits and amounts
- Do NOT summarize or abbreviate - include complete details

Return ONLY a JSON object with these exact fields:
- answer: Complete detailed answer as a SINGLE STRING with ALL specific numbers and details
- conditions: List of condition strings with exact details
- confidence: 0-1

IMPORTANT: 
- Return ONLY the JSON object. No additional text or explanations.
- The "answer" field must be a STRING, never an object or nested structure
- Be COMPLETE and include ALL exact details from the analysis."""

        user_prompt = f"""Query: {query}

Analysis Answer: {combined_analysis.get('answer', 'N/A')}
Conditions: {combined_analysis.get('applicable_conditions', [])}
Best Supporting Clause: {best_clause[:500]}

Generate comprehensive JSON response with ALL exact details:"""

        try:
            response = await self._call_llm(system_prompt, user_prompt, timeout=12)  # Increased timeout for comprehensive response
            
            # Clean and parse JSON response more aggressively
            response = response.strip()
            
            # Remove code block markers
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            
            # Find the first { and last } to extract just the JSON
            try:
                start_idx = response.find('{')
                end_idx = response.rfind('}')
                if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
                    response = response[start_idx:end_idx+1]
                
                response = response.strip()
                result = json.loads(response)
            except (json.JSONDecodeError, ValueError) as json_error:
                logger.warning(f"Fast response JSON parsing failed: {json_error}, trying line-by-line cleanup")
                
                # More aggressive cleanup - split by lines and reconstruct JSON
                lines = response.split('\n')
                json_lines = []
                in_json = False
                brace_count = 0
                
                for line in lines:
                    stripped_line = line.strip()
                    if stripped_line.startswith('{'):
                        in_json = True
                        brace_count += stripped_line.count('{') - stripped_line.count('}')
                        json_lines.append(stripped_line)
                    elif in_json:
                        brace_count += stripped_line.count('{') - stripped_line.count('}')
                        json_lines.append(stripped_line)
                        if brace_count <= 0:
                            break
                
                if json_lines:
                    clean_json = '\n'.join(json_lines)
                    result = json.loads(clean_json)
                else:
                    raise json.JSONDecodeError("Could not extract valid JSON", response, 0)
            
            # Ensure required fields are present
            required_fields = ["answer", "conditions", "confidence"]
            for field in required_fields:
                if field not in result:
                    if field == "answer":
                        result[field] = combined_analysis.get("answer", "Information not available")
                    elif field == "conditions":
                        result[field] = combined_analysis.get("applicable_conditions", [])
                    elif field == "confidence":
                        result[field] = combined_analysis.get("confidence_score", 0.5)
            
            return result
            
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.error(f"Fast response generation failed: {str(e)}")
            
            # Create response from combined analysis
            return {
                "answer": combined_analysis.get("answer", "Unable to process query"),
                "conditions": combined_analysis.get("applicable_conditions", []),
                "confidence": combined_analysis.get("confidence_score", 0.0)
            }
    
    async def _call_llm(self, system_prompt: str, user_prompt: str, timeout: int = 10) -> str:
        """Make API call to Groq or OpenAI with timeout and retry logic."""
        import asyncio
        import time
        
        async def make_api_call():
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            if self.provider == "groq" and self.client:
                # Groq API call with faster settings
                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        temperature=0.1,  # Lower temperature for faster response
                        max_tokens=min(800, self.max_tokens),  # Limit tokens for speed
                        timeout=timeout
                    )
                    return response.choices[0].message.content.strip()
                except Exception as groq_error:
                    logger.error(f"Groq API call failed: {groq_error}")
                    return self._fallback_response(user_prompt)
            elif self.provider == "openai":
                # OpenAI API call (new v1.0+ syntax)
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.1,
                    max_tokens=min(800, self.max_tokens),
                    timeout=timeout
                )
                return response.choices[0].message.content.strip()
            else:
                # Fallback mode - basic response
                return self._fallback_response(user_prompt)
        
        try:
            # Add timeout to the entire operation
            start_time = time.time()
            result = await asyncio.wait_for(make_api_call(), timeout=timeout)
            elapsed = time.time() - start_time
            if elapsed > 5:  # Log slow calls
                logger.warning(f"Slow LLM call took {elapsed:.2f}s")
            return result
            
        except asyncio.TimeoutError:
            logger.error(f"LLM API call timed out after {timeout}s")
            return self._fallback_response(user_prompt)
        except Exception as e:
            logger.error(f"LLM API call failed: {str(e)}")
            return self._fallback_response(user_prompt)
    
    def _fallback_response(self, user_prompt: str) -> str:
        """Generate a basic response when LLM is not available."""
        return json.dumps({
            "answer": "The system is currently unable to process this query due to LLM service unavailability. Please check your API configuration and try again.",
            "conditions": [],
            "clause": "No clause information available",
            "confidence": 0.0,
            "rationale": "The system is currently unable to access LLM services for detailed analysis."
        })
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text using simple NLP."""
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'this', 'that', 'these', 'those', 'i', 'me', 'my', 'we', 'us', 'our',
            'you', 'your', 'he', 'him', 'his', 'she', 'her', 'it', 'its', 'they',
            'them', 'their'
        }
        
        # Extract words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        keywords = [word for word in words if word not in stop_words]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for keyword in keywords:
            if keyword not in seen:
                seen.add(keyword)
                unique_keywords.append(keyword)
        
        return unique_keywords[:20]  # Limit to top 20 keywords
