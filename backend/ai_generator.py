import json
from typing import List, Optional, Dict, Any

from openai import OpenAI


class AIGenerator:
    """Handles interactions with DeepSeek's OpenAI-compatible API for generating responses"""
    
    SYSTEM_PROMPT = """ You are an AI assistant specialized in course materials and educational content with access to a comprehensive search tool for course information.

Search Tool Usage:
- Use the search tool **only** for questions about specific course content or detailed educational materials
- **One search per query maximum**
- Synthesize search results into accurate, fact-based responses
- If search yields no results, state this clearly without offering alternatives

Response Protocol:
- **General knowledge questions**: Answer using existing knowledge without searching
- **Course-specific questions**: Search first, then answer
- **No meta-commentary**:
 - Provide direct answers only — no reasoning process, search explanations, or question-type analysis
 - Do not mention "based on the search results"


All responses must be:
1. **Brief, Concise and focused** - Get to the point quickly
2. **Educational** - Maintain instructional value
3. **Clear** - Use accessible language
4. **Example-supported** - Include relevant examples when they aid understanding
Provide only the direct answer to what was asked.
"""
    
    def __init__(self, api_key: str, model: str, base_url: Optional[str] = None):
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY is not set. Please configure it in your .env file.")
        
        client_kwargs = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url
        
        self.client = OpenAI(**client_kwargs)
        self.model = model
        self.base_params = {
            "model": self.model,
            "temperature": 0,
            "max_tokens": 800
        }
    
    def generate_response(
        self,
        query: str,
        conversation_history: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_manager=None
    ) -> str:
        """
        Generate AI response with optional tool usage and conversation context.
        """
        system_content = (
            f"{self.SYSTEM_PROMPT}\n\nPrevious conversation:\n{conversation_history}"
            if conversation_history
            else self.SYSTEM_PROMPT
        )
        
        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": query}
        ]
        
        tool_payload = self._format_tools(tools)
        chat_params = {
            **self.base_params,
            "messages": messages
        }
        if tool_payload:
            chat_params["tools"] = tool_payload
            chat_params["tool_choice"] = "auto"
        
        response = self.client.chat.completions.create(**chat_params)
        assistant_message = response.choices[0].message
        
        if getattr(assistant_message, "tool_calls", None) and tool_manager:
            return self._handle_tool_execution(assistant_message, messages, tool_payload, tool_manager)
        
        return self._extract_text(assistant_message)
    
    def _format_tools(self, tools: Optional[List[Dict[str, Any]]]) -> Optional[List[Dict[str, Any]]]:
        """Convert internal tool schema to OpenAI/DeepSeek compatible format."""
        if not tools:
            return None
        
        formatted = []
        for tool in tools:
            name = tool.get("name")
            if not name:
                continue
            formatted.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": tool.get("description", ""),
                    "parameters": tool.get("input_schema", {})
                }
            })
        return formatted or None
    
    def _handle_tool_execution(
        self,
        assistant_message,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]],
        tool_manager
    ) -> str:
        """Execute requested tools and ask DeepSeek for a final response."""
        message_dict = assistant_message.model_dump() if hasattr(assistant_message, "model_dump") else assistant_message
        tool_calls = message_dict.get("tool_calls", [])
        
        assistant_entry = {
            "role": "assistant",
            "content": self._extract_text(message_dict)
        }
        if tool_calls:
            assistant_entry["tool_calls"] = tool_calls
        messages.append(assistant_entry)
        
        for tool_call in tool_calls:
            function_data = tool_call.get("function", {})
            arguments = function_data.get("arguments") or "{}"
            try:
                parsed_args = json.loads(arguments)
            except json.JSONDecodeError:
                parsed_args = {}
            result = tool_manager.execute_tool(function_data.get("name"), **parsed_args)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.get("id"),
                "content": result
            })
        
        followup_params = {
            **self.base_params,
            "messages": messages
        }
        if tools:
            followup_params["tools"] = tools
            followup_params["tool_choice"] = "none"
        
        final_response = self.client.chat.completions.create(**followup_params)
        return self._extract_text(final_response.choices[0].message)
    
    def _extract_text(self, message: Any) -> str:
        """Normalize response text from OpenAI SDK structures."""
        if hasattr(message, "model_dump"):
            message = message.model_dump()
        
        content = message.get("content") if isinstance(message, dict) else getattr(message, "content", "")
        if isinstance(content, str):
            return content
        
        if isinstance(content, list):
            collected = []
            for part in content:
                if isinstance(part, dict):
                    text_value = part.get("text")
                    if text_value:
                        collected.append(text_value)
                else:
                    text_attr = getattr(part, "text", None)
                    if text_attr:
                        collected.append(text_attr)
            return "\n".join(collected).strip()
        
        return ""
