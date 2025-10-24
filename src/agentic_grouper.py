"""
Agentic grouping module - LLM-powered knowledge cluster creation.
"""

import json
from typing import List, Dict, Any, Optional
from langchain.schema import Document
from openai import OpenAI
from src.config import get_settings, validate_config
from src.logger import get_logger

logger = get_logger(__name__)


class AgenticGrouper:
    """Use LLM agents to analyze and regroup chunks into knowledge clusters."""
    
    def __init__(self, model: Optional[str] = None, batch_size: Optional[int] = None):
        """
        Initialize the agentic grouper.
        
        Args:
            model: OpenRouter model to use (defaults to config)
            batch_size: Number of chunks to process per batch (defaults to config)
        """
        logger.info("Initializing AgenticGrouper")
        validate_config()
        settings = get_settings()
        
        self.model = model or settings.openrouter_model
        self.batch_size = batch_size or settings.grouping_batch_size
        self.preview_length = settings.grouping_preview_length
        
        logger.info(f"Model: {self.model}, Batch size: {self.batch_size}, Preview length: {self.preview_length}")
        
        # Initialize OpenAI client with OpenRouter endpoint
        self.client = OpenAI(
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
        )
        logger.debug("OpenAI client initialized successfully")
    
    def _create_grouping_prompt(self, chunks: List[Document]) -> str:
        """
        Create a prompt for the LLM to analyze and group chunks.
        
        Args:
            chunks: List of document chunks
            
        Returns:
            Formatted prompt string
        """
        # Create compact chunk summaries for analysis
        chunk_info = []
        for idx, chunk in enumerate(chunks):
            # Use configurable preview length
            preview = chunk.page_content[:self.preview_length]
            if len(chunk.page_content) > self.preview_length:
                preview += "..."
            
            # Create compact representation
            chunk_info.append({
                "id": idx,
                "text": preview.replace("\n", " ").strip(),  # Compact format
                "page": chunk.metadata.get("page", 0),
            })
        
        prompt = f"""Analyze these {len(chunks)} text chunks and group them into 5-15 meaningful knowledge clusters.

Chunks:
{json.dumps(chunk_info, indent=None)}

Return a JSON object with this exact structure (NO markdown, NO code blocks, ONLY the JSON):
{{
  "groups": [
    {{
      "group_id": "id",
      "title": "title",
      "summary": "summary",
      "theme": "theme",
      "chunk_ids": [0,1,2],
      "importance": "high|medium|low"
    }}
  ]
}}

CRITICAL RULES:
- Each chunk belongs to exactly ONE group
- Create cohesive, thematic groupings
- Include ALL chunk IDs 0-{len(chunks) - 1}
- Return ONLY raw JSON (no markdown, no ```json, no code blocks)
- Ensure valid JSON syntax (proper commas, quotes, brackets)"""
        return prompt
    
    def _call_llm(self, prompt: str) -> str:
        """
        Call the LLM via OpenRouter.
        
        Args:
            prompt: The prompt to send
            
        Returns:
            LLM response text
        """
        try:
            logger.debug(f"Calling LLM with model: {self.model}")
            logger.debug(f"Prompt length: {len(prompt)} characters")
            
            # Models that support system messages (Claude, GPT-4, etc.)
            models_with_system_support = [
                'anthropic/', 'openai/', 'meta-llama/', 'mistralai/', 'cohere/'
            ]
            
            supports_system = any(self.model.startswith(prefix) for prefix in models_with_system_support)
            
            if supports_system:
                # Use system message for compatible models
                messages = [
                    {
                        "role": "system",
                        "content": "You are an expert at analyzing and organizing knowledge. You always return valid JSON.",
                    },
                    {"role": "user", "content": prompt},
                ]
            else:
                # Merge system instruction into user message for models like Gemma
                logger.debug(f"Model {self.model} may not support system messages, using merged prompt")
                merged_prompt = (
                    "You are an expert at analyzing and organizing knowledge. You always return valid JSON.\n\n"
                    f"{prompt}"
                )
                messages = [
                    {"role": "user", "content": merged_prompt},
                ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,  # Lower temperature for more consistent grouping
            )
            
            result = response.choices[0].message.content
            logger.debug(f"LLM response received: {len(result)} characters")
            return result
        except Exception as e:
            logger.error(f"Error calling OpenRouter: {str(e)}", exc_info=True)
            raise RuntimeError(f"Error calling OpenRouter: {str(e)}")
    
    def _fix_json_issues(self, json_str: str) -> str:
        """
        Attempt to fix common JSON formatting issues.
        
        Args:
            json_str: Potentially malformed JSON string
            
        Returns:
            Fixed JSON string
        """
        # Remove trailing commas before closing brackets/braces
        import re
        
        # Fix trailing commas before ]
        json_str = re.sub(r',(\s*])', r'\1', json_str)
        
        # Fix trailing commas before }
        json_str = re.sub(r',(\s*})', r'\1', json_str)
        
        # Fix missing commas between array elements (common issue)
        # This is tricky, so we're conservative here
        
        return json_str
    
    def _parse_grouping_response(self, response: str) -> Dict[str, Any]:
        """
        Parse the LLM's grouping response.
        
        Args:
            response: JSON response from LLM
            
        Returns:
            Parsed grouping schema
        """
        try:
            # Clean up response - remove markdown code blocks if present
            cleaned_response = response.strip()
            
            # Remove markdown code fence if present
            if cleaned_response.startswith("```"):
                # Find the actual JSON start (after ```json or ```)
                lines = cleaned_response.split('\n')
                # Skip first line (```json or ```)
                lines = lines[1:]
                # Remove last line if it's ``` 
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                cleaned_response = '\n'.join(lines)
            
            # Extract JSON from response (in case there's extra text)
            start_idx = cleaned_response.find("{")
            end_idx = cleaned_response.rfind("}") + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError(f"No JSON object found in response")
            
            json_str = cleaned_response[start_idx:end_idx]
            
            # Try to fix common JSON issues
            json_str = self._fix_json_issues(json_str)
            
            # Attempt to parse
            parsed = json.loads(json_str)
            
            # Validate structure
            if "groups" not in parsed:
                raise ValueError("Response missing 'groups' key")
            
            return parsed
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {str(e)}")
            logger.error(f"Cleaned response preview: {cleaned_response[:500]}...")
            raise ValueError(f"Failed to parse LLM response as JSON: {str(e)}\nResponse preview: {response[:200]}...")
        except Exception as e:
            logger.error(f"Unexpected error parsing response: {str(e)}")
            raise ValueError(f"Failed to parse LLM response: {str(e)}")
    
    def _group_batch(self, chunks: List[Document], batch_offset: int = 0) -> List[Dict[str, Any]]:
        """
        Group a batch of chunks using LLM analysis.
        
        Args:
            chunks: List of document chunks to process
            batch_offset: Offset for chunk IDs (for multi-batch processing)
            
        Returns:
            List of groups for this batch
        """
        logger.debug(f"Grouping batch with {len(chunks)} chunks (offset: {batch_offset})")
        
        # Create and send the grouping prompt
        prompt = self._create_grouping_prompt(chunks)
        response = self._call_llm(prompt)
        
        # Parse the grouping schema
        grouping_schema = self._parse_grouping_response(response)
        logger.debug(f"Parsed {len(grouping_schema.get('groups', []))} groups from LLM response")
        
        # Create grouped documents
        groups = []
        for group_def in grouping_schema.get("groups", []):
            # Collect chunks for this group
            group_chunks = []
            for chunk_id in group_def.get("chunk_ids", []):
                if 0 <= chunk_id < len(chunks):
                    group_chunks.append(chunks[chunk_id])
            
            if not group_chunks:
                continue
            
            # Merge chunk contents
            merged_content = "\n\n---\n\n".join(
                chunk.page_content for chunk in group_chunks
            )
            
            # Collect metadata from all chunks
            pages = sorted(set(
                chunk.metadata.get("page", 0) for chunk in group_chunks
            ))
            
            # Adjust chunk IDs with batch offset
            adjusted_chunk_ids = [cid + batch_offset for cid in group_def.get("chunk_ids", [])]
            
            # Create group document
            group = {
                "group_id": group_def.get("group_id", f"group_{len(groups)}_{batch_offset}"),
                "title": group_def.get("title", "Untitled Group"),
                "summary": group_def.get("summary", ""),
                "theme": group_def.get("theme", ""),
                "importance": group_def.get("importance", "medium"),
                "content": merged_content,
                "chunk_count": len(group_chunks),
                "chunk_ids": adjusted_chunk_ids,
                "pages": pages,
                "metadata": {
                    "source": group_chunks[0].metadata.get("source", ""),
                    "doc_id": group_chunks[0].metadata.get("doc_id", ""),
                },
            }
            
            groups.append(group)
            logger.debug(f"Created group '{group['title']}' with {group['chunk_count']} chunks")
        
        logger.info(f"Batch processing complete: {len(groups)} groups created")
        return groups
    
    def group_chunks(self, chunks: List[Document], batch_size: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Group chunks into knowledge clusters using LLM analysis.
        For large documents, processes chunks in batches to avoid context limits.
        
        Args:
            chunks: List of document chunks
            batch_size: Number of chunks to process per batch (uses configured default if None)
            
        Returns:
            List of groups, each containing merged content and metadata
        """
        if not chunks:
            logger.warning("No chunks provided for grouping")
            return []
        
        # Use configured batch size if not specified
        batch_size = batch_size or self.batch_size
        total_chunks = len(chunks)
        
        logger.info(f"Starting chunk grouping: {total_chunks} chunks total")
        
        # If chunks fit in one batch, process normally
        if total_chunks <= batch_size:
            logger.info(f"Processing {total_chunks} chunks in a single batch")
            print(f"Processing {total_chunks} chunks in a single batch...")
            return self._group_batch(chunks)
        
        # For large documents, process in batches
        num_batches = (total_chunks + batch_size - 1) // batch_size
        logger.info(f"Processing {total_chunks} chunks in {num_batches} batches of {batch_size}")
        print(f"Processing {total_chunks} chunks in batches of {batch_size}...")
        all_groups = []
        
        for batch_idx in range(0, total_chunks, batch_size):
            batch_end = min(batch_idx + batch_size, total_chunks)
            batch_chunks = chunks[batch_idx:batch_end]
            
            print(f"  ⏳ Processing batch {batch_idx // batch_size + 1}/{(total_chunks + batch_size - 1) // batch_size} (chunks {batch_idx}-{batch_end-1})...")
            
            try:
                batch_groups = self._group_batch(batch_chunks, batch_offset=batch_idx)
                all_groups.extend(batch_groups)
                logger.info(f"Batch {batch_idx // batch_size + 1} successful: {len(batch_groups)} groups created")
                print(f"  [OK] Created {len(batch_groups)} groups from this batch")
            except Exception as e:
                logger.error(f"Error processing batch {batch_idx // batch_size + 1}: {str(e)}", exc_info=True)
                print(f"  [ERROR] Error processing batch {batch_idx // batch_size + 1}: {str(e)}")
                # Fallback: create individual groups for failed batches
                logger.warning(f"Using fallback: creating individual groups for {len(batch_chunks)} chunks")
                for i, chunk in enumerate(batch_chunks):
                    fallback_group = {
                        "group_id": f"fallback_group_{batch_idx + i}",
                        "title": f"Section from page {chunk.metadata.get('page', 'unknown')}",
                        "summary": "Auto-generated group (batch processing failed)",
                        "theme": "general",
                        "importance": "medium",
                        "content": chunk.page_content,
                        "chunk_count": 1,
                        "chunk_ids": [batch_idx + i],
                        "pages": [chunk.metadata.get("page", 0)],
                        "metadata": chunk.metadata,
                    }
                    all_groups.append(fallback_group)
        
        logger.info(f"Chunk grouping complete: {len(all_groups)} total groups created from {total_chunks} chunks")
        print(f"[DONE] Total groups created: {len(all_groups)}")
        return all_groups
    
    def create_group_documents(self, groups: List[Dict[str, Any]]) -> List[Document]:
        """
        Convert group dictionaries to LangChain Document objects.
        
        Args:
            groups: List of group dictionaries
            
        Returns:
            List of Document objects
        """
        documents = []
        
        for group in groups:
            doc = Document(
                page_content=group["content"],
                metadata={
                    "group_id": group["group_id"],
                    "title": group["title"],
                    "summary": group["summary"],
                    "theme": group["theme"],
                    "importance": group["importance"],
                    "chunk_count": group["chunk_count"],
                    "pages": group["pages"],
                    "source": group["metadata"].get("source", ""),
                    "doc_id": group["metadata"].get("doc_id", ""),
                    "type": "knowledge_group",
                },
            )
            documents.append(doc)
        
        return documents


def group_chunks(chunks: List[Document]) -> List[Dict[str, Any]]:
    """
    Convenience function to group chunks.
    
    Args:
        chunks: List of document chunks
        
    Returns:
        List of knowledge groups
    """
    grouper = AgenticGrouper()
    return grouper.group_chunks(chunks)

