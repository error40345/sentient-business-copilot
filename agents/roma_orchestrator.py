import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

# Import ROMA framework
from roma_dspy import RecursiveSolver
from roma_dspy.config import ConfigManager


class ROMAOrchestrator:
    """
    Real ROMA framework orchestrator for business planning
    Uses recursive task decomposition with DSPy-powered agents
    """
    
    def __init__(self, config):
        """Initialize ROMA orchestrator with business copilot configuration"""
        self.config = config
        
        # Initialize ROMA framework
        self._initialize_roma()
        
        # Task execution history for tracing
        self.execution_history = []
        
    def _initialize_roma(self):
        """Initialize ROMA RecursiveSolver with business_copilot profile"""
        # Get project root directory
        project_root = Path(__file__).parent.parent
        config_dir = project_root / "config"
        
        # Transform DATABASE_URL to use asyncpg driver for ROMA
        if "DATABASE_URL" in os.environ:
            original_url = os.environ["DATABASE_URL"]
            if original_url.startswith("postgresql://"):
                # Replace postgresql:// with postgresql+asyncpg://
                transformed_url = original_url.replace("postgresql://", "postgresql+asyncpg://", 1)
                
                # Remove sslmode parameter (asyncpg doesn't accept it)
                # asyncpg uses SSL by default for secure connections
                if "?sslmode=" in transformed_url:
                    transformed_url = transformed_url.split("?sslmode=")[0]
                elif "&sslmode=" in transformed_url:
                    parts = transformed_url.split("&sslmode=")
                    transformed_url = parts[0] + ("&" + parts[1].split("&", 1)[1] if "&" in parts[1] else "")
                
                os.environ["DATABASE_URL"] = transformed_url
                print(f"✓ Transformed DATABASE_URL to use asyncpg driver")
        
        # Create ROMA config manager
        self.roma_config_manager = ConfigManager(config_dir=config_dir)
        
        # Load business_copilot profile
        self.roma_config = self.roma_config_manager.load_config(profile="business_copilot")
        
        # Customize runtime settings for Streamlit
        if hasattr(self.roma_config, 'runtime') and self.roma_config.runtime:
            self.roma_config.runtime.max_depth = 1  # Reduced to 1 for faster responses
            self.roma_config.runtime.verbose = False
            self.roma_config.runtime.enable_logging = True
            self.roma_config.runtime.timeout = 120  # 2 minutes timeout
        
        # Create ROMA solver (disable checkpoints for Streamlit)
        self.roma_solver = RecursiveSolver(
            config=self.roma_config,
            enable_checkpoints=False
        )
        
        print("✅ ROMA framework initialized successfully")
    
    def process_request(self, user_input: str, current_stage: str, business_plan: Dict, 
                       chat_history: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Main orchestration method using ROMA framework
        """
        return self._process_with_roma(user_input, current_stage, business_plan, chat_history)
    
    def _process_with_roma(self, user_input: str, current_stage: str, 
                          business_plan: Dict, chat_history: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Process request using ROMA framework"""
        
        # Log the request
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.log_task(task_id, "roma_solver", user_input, current_stage)
        
        # Enrich task with business context
        enriched_task = self._enrich_task_with_context(user_input, current_stage, business_plan, chat_history)
        
        # Use synchronous solve method on the solver instance
        result = self.roma_solver.solve(enriched_task)
        
        # Extract and format the result
        answer = ""
        if hasattr(result, 'result') and result.result is not None:
            answer = str(result.result)
        else:
            answer = str(result)
        
        # Parse business plan updates from the answer if possible
        business_plan_update = self._extract_business_data(answer, current_stage)
        
        # Determine next stage
        next_stage = self._determine_next_stage(current_stage, user_input, answer)
        
        return {
            "message": answer,
            "business_plan_update": business_plan_update if business_plan_update else None,
            "next_stage": next_stage if next_stage != current_stage else None,
            "roma_execution_id": getattr(result, 'task_id', None)
        }
    
    def _enrich_task_with_context(self, user_input: str, current_stage: str, 
                                  business_plan: Dict, chat_history: Optional[List[Dict]] = None) -> str:
        """Enrich user task with business context for better ROMA processing"""
        
        context_parts = []
        
        # Add detailed system guidance for comprehensive responses
        system_guidance = """
You are a professional business consultant. Provide helpful, well-structured business advice.

**TONE REQUIREMENTS:**
- Use professional, polite, and respectful language
- Be calm, supportive, and encouraging
- Avoid profanity or aggressive language
- Maintain a friendly yet professional tone

**RESPONSE REQUIREMENTS:**
- Provide concise, actionable insights (400-600 words)
- Use web search when you need current data
- Include specific numbers and examples when available
- Structure information with clear headings
- Focus on practical, immediately useful advice
"""
        
        # Add current stage context with detailed objectives
        stage_context = {
            "idea": """💡 IDEA STAGE - Provide analysis of the business idea:
            
            Include these sections (400-600 words total):
            - Market Overview: Basic market size and trends (search if needed)
            - Target Customers: Who will buy this?
            - Competition: 2-3 main competitors
            - Viability: Initial cost estimate and revenue potential
            - Key Risks: Top 3 risks
            - Next Steps: 3-5 recommendations
            
            Keep it concise and actionable.""",
            
            "research": """🔍 RESEARCH STAGE - Provide market research insights:
            
            Include (400-600 words total):
            - Market Size: Current size and growth rate (search if needed)
            - Customers: Key segments and demographics
            - Competition: Top 3-4 competitors and their positioning
            - Trends: 2-3 major industry trends
            - Barriers: Main entry barriers
            
            Be concise and data-driven.""",
            
            "planning": """📋 PLANNING STAGE - Provide business plan guidance:
            
            Include (400-600 words total):
            - Business Model: Revenue streams and pricing
            - Operations: Key processes and tools needed
            - Marketing: Main channels and tactics
            - Team: Essential roles and timeline
            - Milestones: 6-month roadmap
            
            Keep it practical and actionable.""",
            
            "costing": """💰 COSTING STAGE - Provide financial analysis:
            
            Include (400-600 words total):
            - Startup Costs: Major expense categories with estimates
            - Monthly Costs: Operating expenses breakdown
            - Revenue: Pricing and sales projections
            - Break-even: Timeline estimate
            - Funding: Total capital needed
            
            Show key calculations.""",
            
            "launch": """🚀 LAUNCH STAGE - Provide launch plan:
            
            Include (400-600 words total):
            - Legal: Registration steps and licenses needed
            - Setup: Key equipment and tools
            - Marketing: Pre-launch and launch tactics
            - Timeline: 90-day action plan
            - Risks: Top 3 risks to watch
            
            Be practical and specific."""
        }
        
        if current_stage in stage_context:
            context_parts.append(stage_context[current_stage])
        
        # Add existing business plan context
        if business_plan.get("business_name"):
            context_parts.append(f"Business: {business_plan['business_name']}")
        if business_plan.get("industry"):
            context_parts.append(f"Industry: {business_plan['industry']}")
        if business_plan.get("target_region"):
            context_parts.append(f"Region: {business_plan['target_region']}")
        
        # Build enriched task with system guidance
        context_str = ' | '.join(context_parts) if context_parts else ''
        enriched = f"{system_guidance}\n\n[Business Context: {context_str}]\n\nUser Request: {user_input}"
        
        return enriched
    
    def _extract_business_data(self, answer: str, current_stage: str) -> Optional[Dict]:
        """Extract structured business plan data from ROMA's answer"""
        
        # Simple extraction based on stage
        # This is a simplified version - could be enhanced with LLM parsing
        updates = {}
        
        answer_lower = answer.lower()
        
        # Extract business name if mentioned
        if "business name" in answer_lower or "company name" in answer_lower:
            # Simple extraction - could be improved
            for line in answer.split('\n'):
                if "name:" in line.lower() or "business:" in line.lower():
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        updates["business_name"] = parts[1].strip()
        
        # Stage-specific extractions
        if current_stage == "research" and ("market" in answer_lower or "industry" in answer_lower):
            updates["has_market_research"] = True
            
        if current_stage == "planning" and ("plan" in answer_lower or "strategy" in answer_lower):
            updates["has_business_plan"] = True
            
        if current_stage == "costing" and ("cost" in answer_lower or "$" in answer):
            updates["has_financial_projections"] = True
            
        if current_stage == "launch" and ("launch" in answer_lower or "register" in answer_lower):
            updates["has_launch_plan"] = True
        
        return updates if updates else None
    
    def _determine_next_stage(self, current_stage: str, user_input: str, answer: str) -> str:
        """Determine if we should progress to the next stage"""
        
        stages = ["idea", "research", "planning", "costing", "launch"]
        
        # Simple progression logic
        progression_keywords = {
            "idea": ["start research", "market research", "analyze market"],
            "research": ["create plan", "business plan", "develop strategy"],
            "planning": ["calculate costs", "financial", "budget"],
            "costing": ["launch", "register", "start business"]
        }
        
        combined_text = (user_input + " " + answer).lower()
        
        try:
            current_idx = stages.index(current_stage)
            
            # Check if we should progress
            if current_stage in progression_keywords:
                keywords = progression_keywords[current_stage]
                if any(kw in combined_text for kw in keywords) and current_idx < len(stages) - 1:
                    return stages[current_idx + 1]
            
        except ValueError:
            pass
        
        return current_stage
    
    def log_task(self, task_id: str, agent: str, task: str, stage: str):
        """Log task execution for tracing (ROMA observability)"""
        log_entry = {
            "task_id": task_id,
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "task": task,
            "stage": stage
        }
        self.execution_history.append(log_entry)
        
        # Keep only last 100 entries
        if len(self.execution_history) > 100:
            self.execution_history = self.execution_history[-100:]
    
    def get_execution_history(self) -> List[Dict]:
        """Get recent execution history"""
        return self.execution_history.copy()
    
    def get_roma_status(self) -> Dict[str, Any]:
        """Get ROMA framework status"""
        return {
            "roma_enabled": True,
            "config_profile": "business_copilot",
            "execution_count": len(self.execution_history),
            "last_execution": self.execution_history[-1] if self.execution_history else None
        }
