import os
import json
import pickle
from typing import Dict, Any, List, Optional
from datetime import datetime
import streamlit as st

class StateManager:
    """
    Manages persistent state for business plans and chat history
    Uses Streamlit session state and optional file persistence
    """
    
    def __init__(self):
        self.data_dir = "data"
        self.ensure_data_directory()
    
    def ensure_data_directory(self):
        """Ensure data directory exists"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def save_business_plan(self, business_plan: Dict[str, Any], plan_id: Optional[str] = None) -> str:
        """
        Save business plan to persistent storage
        Returns the plan ID for future reference
        """
        try:
            if not plan_id:
                plan_id = self.generate_plan_id(business_plan)
            
            # Add metadata
            business_plan_with_metadata = {
                "plan_id": plan_id,
                "created_at": business_plan.get("created_at", datetime.now().isoformat()),
                "last_updated": datetime.now().isoformat(),
                "version": business_plan.get("version", 1),
                **business_plan
            }
            
            # Save to file
            filename = f"business_plan_{plan_id}.json"
            filepath = os.path.join(self.data_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(business_plan_with_metadata, f, indent=2, ensure_ascii=False)
            
            return plan_id
            
        except Exception as e:
            st.error(f"Failed to save business plan: {str(e)}")
            return ""
    
    def load_business_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Load business plan from persistent storage"""
        try:
            filename = f"business_plan_{plan_id}.json"
            filepath = os.path.join(self.data_dir, filename)
            
            if not os.path.exists(filepath):
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            st.error(f"Failed to load business plan: {str(e)}")
            return None
    
    def list_business_plans(self) -> List[Dict[str, Any]]:
        """List all saved business plans"""
        try:
            plans = []
            
            for filename in os.listdir(self.data_dir):
                if filename.startswith("business_plan_") and filename.endswith(".json"):
                    try:
                        filepath = os.path.join(self.data_dir, filename)
                        with open(filepath, 'r', encoding='utf-8') as f:
                            plan = json.load(f)
                            
                        # Extract summary info
                        plans.append({
                            "plan_id": plan.get("plan_id", ""),
                            "business_name": plan.get("business_name", "Unnamed Business"),
                            "industry": plan.get("industry", ""),
                            "location": plan.get("location", ""),
                            "created_at": plan.get("created_at", ""),
                            "last_updated": plan.get("last_updated", ""),
                            "stage": self.determine_plan_stage(plan)
                        })
                    except Exception:
                        continue  # Skip corrupted files
            
            # Sort by last updated
            plans.sort(key=lambda x: x.get("last_updated", ""), reverse=True)
            return plans
            
        except Exception as e:
            st.error(f"Failed to list business plans: {str(e)}")
            return []
    
    def save_chat_history(self, chat_history: List[Dict[str, Any]], plan_id: Optional[str] = None) -> bool:
        """Save chat history to persistent storage"""
        try:
            if not plan_id:
                plan_id = st.session_state.get("current_plan_id", "default")
            
            filename = f"chat_history_{plan_id}.json"
            filepath = os.path.join(self.data_dir, filename)
            
            chat_data = {
                "plan_id": plan_id,
                "saved_at": datetime.now().isoformat(),
                "message_count": len(chat_history),
                "chat_history": chat_history
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(chat_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            st.error(f"Failed to save chat history: {str(e)}")
            return False
    
    def load_chat_history(self, plan_id: str) -> List[Dict[str, Any]]:
        """Load chat history from persistent storage"""
        try:
            filename = f"chat_history_{plan_id}.json"
            filepath = os.path.join(self.data_dir, filename)
            
            if not os.path.exists(filepath):
                return []
            
            with open(filepath, 'r', encoding='utf-8') as f:
                chat_data = json.load(f)
            
            return chat_data.get("chat_history", [])
            
        except Exception as e:
            st.error(f"Failed to load chat history: {str(e)}")
            return []
    
    def generate_plan_id(self, business_plan: Dict[str, Any]) -> str:
        """Generate unique plan ID based on business details"""
        
        # Use business name if available, otherwise generate from timestamp
        business_name = business_plan.get("business_name", "")
        if business_name:
            # Clean business name for use as ID
            clean_name = "".join(c.lower() for c in business_name if c.isalnum() or c.isspace())
            clean_name = "_".join(clean_name.split())[:20]  # Max 20 chars
            timestamp = datetime.now().strftime("%m%d_%H%M")
            return f"{clean_name}_{timestamp}"
        else:
            # Use timestamp-based ID
            return datetime.now().strftime("plan_%Y%m%d_%H%M%S")
    
    def determine_plan_stage(self, business_plan: Dict[str, Any]) -> str:
        """Determine what stage a business plan is in"""
        
        stages = ["idea", "research", "planning", "costing", "launch"]
        
        # Check for launch stage indicators
        if (business_plan.get("launch_timeline") or 
            business_plan.get("launch_checklist")):
            return "launch"
        
        # Check for costing stage indicators
        if (business_plan.get("financial_projections") or 
            business_plan.get("estimated_startup_cost")):
            return "costing"
        
        # Check for planning stage indicators
        if (business_plan.get("business_model") or 
            business_plan.get("marketing_strategy") or
            business_plan.get("operations_plan")):
            return "planning"
        
        # Check for research stage indicators
        if business_plan.get("market_data"):
            return "research"
        
        # Default to idea stage
        return "idea"
    
    def delete_business_plan(self, plan_id: str) -> bool:
        """Delete a business plan and its associated files"""
        try:
            # Delete business plan file
            plan_file = os.path.join(self.data_dir, f"business_plan_{plan_id}.json")
            if os.path.exists(plan_file):
                os.remove(plan_file)
            
            # Delete associated chat history
            chat_file = os.path.join(self.data_dir, f"chat_history_{plan_id}.json")
            if os.path.exists(chat_file):
                os.remove(chat_file)
            
            return True
            
        except Exception as e:
            st.error(f"Failed to delete business plan: {str(e)}")
            return False
    
    def export_business_plan_data(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Export complete business plan data including chat history"""
        try:
            business_plan = self.load_business_plan(plan_id)
            if not business_plan:
                return None
            
            chat_history = self.load_chat_history(plan_id)
            
            return {
                "business_plan": business_plan,
                "chat_history": chat_history,
                "exported_at": datetime.now().isoformat(),
                "export_version": "1.0"
            }
            
        except Exception as e:
            st.error(f"Failed to export business plan data: {str(e)}")
            return None
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        try:
            if not os.path.exists(self.data_dir):
                return {
                    "total_plans": 0,
                    "total_size_mb": 0,
                    "data_directory": self.data_dir,
                    "status": "empty"
                }
            
            files = os.listdir(self.data_dir)
            plan_files = [f for f in files if f.startswith("business_plan_")]
            
            total_size = 0
            for filename in files:
                filepath = os.path.join(self.data_dir, filename)
                if os.path.isfile(filepath):
                    total_size += os.path.getsize(filepath)
            
            return {
                "total_plans": len(plan_files),
                "total_files": len(files),
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "data_directory": self.data_dir,
                "status": "active" if plan_files else "empty"
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "status": "error"
            }
    
    def cleanup_old_files(self, days_old: int = 30) -> int:
        """Clean up files older than specified days"""
        try:
            if not os.path.exists(self.data_dir):
                return 0
            
            cutoff_time = datetime.now().timestamp() - (days_old * 24 * 3600)
            cleaned_count = 0
            
            for filename in os.listdir(self.data_dir):
                filepath = os.path.join(self.data_dir, filename)
                
                if os.path.isfile(filepath):
                    file_time = os.path.getmtime(filepath)
                    if file_time < cutoff_time:
                        os.remove(filepath)
                        cleaned_count += 1
            
            return cleaned_count
            
        except Exception as e:
            st.error(f"Failed to cleanup old files: {str(e)}")
            return 0
