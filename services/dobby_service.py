import os
import requests
from typing import Dict, Any, Optional, List
import json
import re

class DobbyService:
    """
    Service wrapper for Dobby-70B via Fireworks AI API
    Handles business planning and analysis generation
    """
    
    def __init__(self, config):
        self.config = config
        self.fireworks_api_key = os.getenv("FIREWORKS_API_KEY", "")
        
        self.base_url = "https://api.fireworks.ai/inference/v1"
        self.model_name = "accounts/sentientfoundation/models/dobby-unhinged-llama-3-3-70b-new"
        
        # Default generation parameters
        self.generation_params = {
            "temperature": 0.5,
            "max_tokens": 2048,
            "top_p": 0.95,
            "top_k": 40,
            "presence_penalty": 0,
            "frequency_penalty": 0.3
        }
    
    def generate_response(self, prompt: str, chat_history: Optional[List[Dict]] = None, **kwargs) -> str:
        """Generate response using Dobby-70B via Fireworks AI with conversation history"""
        
        try:
            # Prepare the request
            headers = {
                "Authorization": f"Bearer {self.fireworks_api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            # Merge custom parameters with defaults
            generation_params = {**self.generation_params, **kwargs}
            
            # Build messages array with conversation history
            messages = [
                {
                    "role": "system",
                    "content": """You are a professional business advisor helping entrepreneurs plan and launch their businesses. 

CRITICAL RULES - MUST FOLLOW:
1. LANGUAGE: Use ONLY professional, respectful, calm, and polite language
2. NO PROFANITY: Absolutely NO curse words, vulgar terms, or offensive language of any kind
3. NO SLANG: Avoid inappropriate slang or casual profanity
4. TONE: Be supportive, encouraging, helpful, and professional at all times
5. CONTEXT: Remember and reference previous conversation context
6. CONTINUITY: Continue the discussion on the same topic unless the user changes it
7. ACCURACY: Provide specific, actionable advice with real numbers and data

FORMATTING REQUIREMENTS:
8. STRUCTURE: Organize responses with clear sections using headers (## or **)
9. SPACING: Add blank lines between major topics and sections for readability
10. BULLETS: Use bullet points (•, -, or numbered lists) for lists and key points
11. CLARITY: Keep paragraphs concise (2-4 sentences max)
12. VISUAL BREAKS: Use horizontal spacing to separate different aspects of your advice

Example format:
## Market Opportunity

[2-3 sentences about market]

## Competition Analysis

[2-3 sentences about competition]

## Key Success Factors

• Factor 1
• Factor 2
• Factor 3

You are a respected business consultant - maintain that professional standard with clear, well-organized responses.
Your reputation depends on being helpful, knowledgeable, calm, professional, and easy to read."""
                }
            ]
            
            # Add conversation history (last 10 messages for context without exceeding token limits)
            if chat_history:
                for msg in chat_history[-10:]:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # Add current user prompt
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            payload = {
                "model": self.model_name,
                "messages": messages,
                **generation_params
            }
            
            # Make the API call with shorter timeout
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=15  # 15 second timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                raw_response = result["choices"][0]["message"]["content"].strip()
                # Clean response to ensure professionalism
                return self._sanitize_response(raw_response)
            else:
                # Handle API errors gracefully
                error_msg = f"Fireworks API error: {response.status_code}"
                if response.status_code == 401:
                    error_msg += " - Invalid API key"
                elif response.status_code == 429:
                    error_msg += " - Rate limit exceeded"
                elif response.status_code == 503:
                    error_msg += " - Service temporarily unavailable"
                
                # Return fallback response for demo purposes
                return self.generate_fallback_response(prompt, error_msg)
                
        except requests.exceptions.Timeout:
            return self.generate_fallback_response(prompt, "Request timeout")
        except requests.exceptions.ConnectionError:
            return self.generate_fallback_response(prompt, "Connection error")
        except Exception as e:
            return self.generate_fallback_response(prompt, f"Unexpected error: {str(e)}")
    
    def generate_fallback_response(self, prompt: str, error: str) -> str:
        """Generate fallback response when Dobby API is unavailable"""
        
        prompt_lower = prompt.lower()
        
        # Business plan fallback
        if "business plan" in prompt_lower or "comprehensive" in prompt_lower:
            return """
            **Business Plan Framework**
            
            Here's a structured approach to develop your business plan:
            
            **1. Executive Summary**
            - Define your business concept and value proposition
            - Identify your target market and competitive advantage
            - Outline financial projections and funding needs
            
            **2. Market Analysis**
            - Research your industry size and growth trends
            - Analyze your competition and market positioning
            - Define your ideal customer profile
            
            **3. Operations Plan**
            - Detail your day-to-day operations
            - Identify required resources and staffing
            - Establish quality control processes
            
            **4. Marketing Strategy**
            - Develop your brand positioning
            - Choose effective marketing channels
            - Create customer acquisition and retention plans
            
            **5. Financial Projections**
            - Estimate startup costs and ongoing expenses
            - Project revenue streams and break-even analysis
            - Plan for cash flow management
            
            *Note: AI service temporarily unavailable, but this framework will guide your planning process.*
            """
        
        # Financial analysis fallback
        elif "cost" in prompt_lower or "financial" in prompt_lower or "budget" in prompt_lower:
            return """
            **Financial Planning Guidelines**
            
            **Startup Costs to Consider:**
            - Legal and licensing fees: $500-2,000
            - Initial equipment and setup: $2,000-10,000
            - Marketing and branding: $1,000-5,000
            - Working capital (3-6 months expenses): Variable
            - Professional services: $1,000-3,000
            
            **Monthly Operating Expenses:**
            - Rent/lease: Location dependent
            - Utilities and services: $200-800
            - Insurance: $300-1,000
            - Marketing: 5-10% of projected revenue
            - Miscellaneous: 10-15% buffer
            
            **Revenue Planning:**
            - Research similar businesses in your area
            - Start with conservative estimates
            - Plan for seasonal variations
            - Build in growth assumptions after 6-12 months
            
            *Note: These are general estimates. Research local costs for accuracy.*
            """
        
        # Launch planning fallback
        elif "launch" in prompt_lower or "register" in prompt_lower:
            return """
            **Business Launch Checklist**
            
            **Legal Structure & Registration:**
            - Choose business structure (LLC, Corporation, etc.)
            - Register business name
            - Obtain EIN from IRS
            - Apply for required licenses and permits
            
            **Financial Setup:**
            - Open business bank account
            - Set up accounting system
            - Obtain business insurance
            - Establish business credit
            
            **Operations Setup:**
            - Secure business location
            - Purchase equipment and inventory
            - Set up utilities and services
            - Hire and train staff
            
            **Marketing Launch:**
            - Develop branding and marketing materials
            - Build website and online presence
            - Plan launch event or promotion
            - Establish customer service procedures
            
            **Timeline:** Most businesses need 8-12 weeks from start to launch.
            
            *Note: Consult local business resources for region-specific requirements.*
            """
        
        # Marketing strategy fallback
        elif "marketing" in prompt_lower:
            return """
            **Marketing Strategy Framework**
            
            **Target Customer Analysis:**
            - Define demographic and psychographic profiles
            - Identify pain points and needs
            - Understand buying behaviors and preferences
            
            **Marketing Mix (4 Ps):**
            - Product: Unique value proposition
            - Price: Competitive pricing strategy
            - Place: Distribution channels
            - Promotion: Marketing tactics and messaging
            
            **Digital Marketing Channels:**
            - Social media marketing (Facebook, Instagram, LinkedIn)
            - Search engine optimization (SEO)
            - Email marketing campaigns
            - Content marketing and blogging
            
            **Traditional Marketing:**
            - Local networking events
            - Print advertising (if relevant)
            - Direct mail campaigns
            - Referral programs
            
            **Budget Allocation:**
            - Start with 5-10% of projected revenue
            - Focus on highest ROI channels first
            - Track and measure all activities
            
            *Note: Marketing service analysis temporarily unavailable.*
            """
        
        # General business advice fallback
        else:
            return f"""
            **Business Advisory Response**
            
            Thank you for your question about business planning. While our advanced AI advisor is temporarily unavailable, here are some key principles to consider:
            
            **Key Success Factors:**
            - Validate your business idea with potential customers
            - Start lean and test your assumptions
            - Focus on solving real problems for your target market
            - Build strong financial management practices
            - Invest in customer relationships and retention
            
            **Next Steps:**
            - Conduct thorough market research
            - Develop a minimum viable product/service
            - Create a detailed business plan
            - Secure adequate funding
            - Build a strong team and advisor network
            
            **Resources to Explore:**
            - Local Small Business Development Centers (SBDC)
            - Industry associations and trade groups
            - Online business planning tools
            - Professional business advisors
            
            Please try again later for more detailed analysis, or consult with local business experts for personalized guidance.
            
            *Service Note: {error}*
            """
    
    def _sanitize_response(self, response: str) -> str:
        """Remove inappropriate language while preserving formatting"""
        
        cleaned = response
        
        # Replace inappropriate words with professional alternatives
        # Pattern list maintained separately for content filtering
        replacements = {
            r'\bf[*u]ck\w*\b': 'very',
            r'\bs[*h]it\w*\b': 'issues',
            r'\bd[*a]mn\w*\b': 'very',
            r'\bh[*e]ll\b': 'difficulty',
            r'\ba[*s]s\b': '',
            r'\ba[*s]shole\w*\b': 'person',
            r'\bb[*i]tch\w*\b': 'complaint',
            r'\bc[*r]ap\w*\b': 'issues',
            r'\bb[*a]stard\w*\b': 'person',
            r'\bd[*i]ck\w*\b': 'person',
            r'\bp[*i]ss\w*\b': 'upset'
        }
        
        for pattern, replacement in replacements.items():
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
        
        # Remove excessive emphasis
        cleaned = re.sub(r'!{2,}', '!', cleaned)
        
        # Clean up multiple spaces on the same line (but preserve newlines and indentation)
        # Split by lines, clean each line, then rejoin
        lines = cleaned.split('\n')
        cleaned_lines = []
        for line in lines:
            if not line.strip():
                # Preserve blank lines
                cleaned_lines.append('')
            else:
                # Capture leading whitespace (indentation)
                leading_match = re.match(r'^(\s*)', line)
                leading_spaces = leading_match.group(1) if leading_match else ''
                
                # Get the content after leading whitespace
                content = line[len(leading_spaces):]
                
                # Clean up multiple spaces/tabs only in the content (not leading indentation)
                cleaned_content = re.sub(r'[ \t]{2,}', ' ', content)
                
                # Combine preserved indentation with cleaned content, remove trailing spaces
                cleaned_lines.append(leading_spaces + cleaned_content.rstrip())
        
        # Rejoin with newlines, preserving blank lines and indentation
        return '\n'.join(cleaned_lines)
    
    def health_check(self) -> Dict[str, Any]:
        """Check if Dobby service is available"""
        
        try:
            # Test with a simple prompt
            test_response = self.generate_response("Hello, are you working?", max_tokens=50)
            
            is_fallback = "temporarily unavailable" in test_response or "Service Note:" in test_response
            
            return {
                "status": "degraded" if is_fallback else "healthy",
                "message": "Dobby-70B service operational" if not is_fallback else "Using fallback responses",
                "model": self.model_name,
                "has_api_key": bool(self.fireworks_api_key),
                "fallback_mode": is_fallback
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Service check failed: {str(e)}"
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the Dobby model"""
        
        return {
            "model_name": "Dobby-70B (Unhinged Llama 3.3)",
            "provider": "Fireworks AI",
            "parameters": "70 billion",
            "specialty": "Business planning and unfiltered advice",
            "personality": "Direct, opinionated, pro-business",
            "best_for": [
                "Business plan generation",
                "Financial analysis",
                "Marketing strategy",
                "Operational planning",
                "Risk assessment"
            ]
        }
