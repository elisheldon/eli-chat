import json
import random
from typing import List, Dict
from datetime import datetime
import re

class ChatProcessor:
    def __init__(self, 
                 max_user_chars: int = 512,    # Maximum characters for combined user messages
                 max_assistant_chars: int = 1024,  # Maximum characters for combined assistant messages
                 max_turns: int = 6,           # Maximum back-and-forth exchanges in a conversation
                 max_conversation_gap: int = 3600  # Maximum seconds between messages
                ):
        self.max_user_chars = max_user_chars
        self.max_assistant_chars = max_assistant_chars
        self.max_turns = max_turns
        self.max_conversation_gap = max_conversation_gap

        # Add common chat patterns to filter out
        self.noise_patterns = [
            r'^(haha|lol|ok|okay|sure|word|perf|dope|nice|wow|yeah|yep|nah)$',
            r'^[0-9\s\+\-\*\/\=]+$',  # Pure calculations
            r'^\s*[😊😄😃😀😂🤣😅😆👍❤️]+\s*$',  # Just emojis
            r'^[.!?]+$'  # Just punctuation
        ]
        
    def parse_date(self, date_str: str) -> datetime:
        """Parse the date string into a datetime object."""
        try:
            return datetime.strptime(date_str, "%A, %B %d, %Y at %I:%M:%S %p UTC")
        except (ValueError, TypeError):
            return None
    
    def is_valid_message(self, message: Dict) -> bool:
        """Check if a message has all required fields and no attachments."""
        return (
            isinstance(message, dict) and
            "creator" in message and
            isinstance(message["creator"], dict) and
            "name" in message["creator"] and
            "text" in message and
            message["text"] and  # Ensure text is not None or empty
            "attached_files" not in message
        )
    
    def get_message_time(self, message: Dict) -> datetime:
        """Safely get the datetime from a message."""
        if not isinstance(message, dict):
            return None
        date_str = message.get("created_date")
        if not date_str:
            return None
        return self.parse_date(date_str)
    
    def is_meaningful_message(self, text: str) -> bool:
        """Check if a message contains meaningful content."""
        # Remove leading/trailing whitespace
        text = text.strip().lower()
        
        # Check minimum length (adjustable)
        if len(text) < 3:
            return False
            
        # Check against noise patterns
        for pattern in self.noise_patterns:
            if re.match(pattern, text):
                return False
                
        return True

    def should_combine_messages(self, messages: List[Dict], start_idx: int) -> List[Dict]:
        """Enhanced message combination logic with context awareness."""
        if start_idx >= len(messages):
            return []
            
        current_creator = messages[start_idx]["creator"]["name"]
        is_assistant = current_creator != "Chrissie Grover-Roybal"
        consecutive_messages = []
        
        i = start_idx
        context_buffer = []  # Store previous context
        total_chars = 0
        max_chars = self.max_assistant_chars if is_assistant else self.max_user_chars
        
        while i < len(messages):
            if messages[i]["creator"]["name"] != current_creator:
                break
                
            current_msg = messages[i].get("text", "").strip()
            
            # Skip non-meaningful messages
            if not self.is_meaningful_message(current_msg):
                i += 1
                continue
                
            # Check time gap with previous message
            if i > start_idx:
                current_time = self.get_message_time(messages[i])
                prev_time = self.get_message_time(messages[i-1])
                if current_time and prev_time:
                    time_diff = (current_time - prev_time).total_seconds()
                    if time_diff > 300:  # 5 minutes
                        break
            
            msg_length = len(current_msg)
            
            # Check if adding this message would exceed length limit
            if total_chars + msg_length > max_chars:
                # If we've already collected messages, return them
                if consecutive_messages:
                    break
                # If this is the first message and it's too long, truncate it
                current_msg = current_msg[:max_chars]
                msg_length = len(current_msg)
            
            # Add message if it provides new information
            if not context_buffer or not self._is_redundant(current_msg, context_buffer):
                consecutive_messages.append(messages[i])
                context_buffer.append(current_msg)
                total_chars += msg_length
            
            i += 1
        
        return consecutive_messages

    def _is_redundant(self, new_msg: str, context: List[str], similarity_threshold: float = 0.8) -> bool:
        """Check if a message is redundant given the context."""
        new_msg = new_msg.lower()
        
        # Simple word-based similarity check
        new_words = set(new_msg.split())
        
        for ctx_msg in context:
            ctx_words = set(ctx_msg.lower().split())
            
            # Calculate Jaccard similarity
            if len(new_words) == 0 or len(ctx_words) == 0:
                continue
                
            intersection = len(new_words & ctx_words)
            union = len(new_words | ctx_words)
            
            if intersection / union > similarity_threshold:
                return True
        
        return False

    def combine_messages(self, messages: List[Dict]) -> str:
        """Enhanced message combination with improved formatting."""
        if not messages:
            return ""
            
        texts = []
        for msg in messages:
            text = msg.get("text", "").strip()
            if text:
                # Handle common chat abbreviations
                text = re.sub(r'\b(bc|cuz|cause)\b', 'because', text)
                text = re.sub(r'\b(rn)\b', 'right now', text)
                text = re.sub(r'\b(ty)\b', 'thank you', text)
                
                # Improve sentence structure
                if not text[0].isupper():
                    text = text[0].upper() + text[1:]
                
                texts.append(text)
        
        # Combine messages with appropriate punctuation
        combined = ""
        for i, text in enumerate(texts):
            if i > 0:
                prev_text = texts[i-1]
                # Add appropriate connecting punctuation
                if prev_text[-1] not in ".!?":
                    if self._is_related_thought(prev_text, text):
                        combined += ", "
                    else:
                        combined += ". "
                else:
                    combined += " "
            combined += text
        
        # Ensure proper ending punctuation
        if combined and combined[-1] not in ".!?":
            combined += "."
            
        return combined

    def _is_related_thought(self, prev: str, curr: str) -> bool:
        """Determine if two messages are closely related thoughts."""
        # Check for conjunctions at start of current message
        connecting_words = {'and', 'but', 'or', 'so', 'because', 'however'}
        curr_words = curr.lower().split()
        if curr_words and curr_words[0] in connecting_words:
            return True
            
        # Check for sentence fragments that might be continuations
        if not curr[0].isupper():
            return True
            
        return False
    
    def create_conversations(self, messages: List[Dict]) -> List[Dict]:
        """Create multi-turn conversations from messages."""
        # First, filter out invalid messages
        valid_messages = [msg for msg in messages if self.is_valid_message(msg)]
        
        conversations = []
        current_conversation = []
        i = 0
        
        while i < len(valid_messages):
            # If this is the start of a potential conversation
            if not current_conversation:
                if valid_messages[i]["creator"]["name"] == "Chrissie Grover-Roybal":
                    messages_to_combine = self.should_combine_messages(valid_messages, i)
                    if messages_to_combine:
                        combined_text = self.combine_messages(messages_to_combine)
                        current_conversation.append({"role": "user", "content": combined_text})
                        i += len(messages_to_combine)
                    else:
                        i += 1
                else:
                    i += 1
                continue
            
            # Check if we should end the current conversation
            if len(current_conversation) >= self.max_turns * 2:
                conversations.append({"messages": current_conversation})
                current_conversation = []
                continue
            
            # Check time gap if dates are available
            last_msg_time = self.get_message_time(valid_messages[i-1])
            current_msg_time = self.get_message_time(valid_messages[i])
            if last_msg_time and current_msg_time:
                time_diff = (current_msg_time - last_msg_time).total_seconds()
                if time_diff > self.max_conversation_gap:
                    if len(current_conversation) >= 2:  # Only save if we have at least one exchange
                        conversations.append({"messages": current_conversation})
                    current_conversation = []
                    continue
            
            # Add to current conversation
            is_assistant = valid_messages[i]["creator"]["name"] != "Chrissie Grover-Roybal"
            messages_to_combine = self.should_combine_messages(valid_messages, i)
            
            if messages_to_combine:
                combined_text = self.combine_messages(messages_to_combine)
                role = "assistant" if is_assistant else "user"
                
                # Ensure alternating user/assistant messages
                if not current_conversation or current_conversation[-1]["role"] != role:
                    current_conversation.append({"role": role, "content": combined_text})
                
                i += len(messages_to_combine)
            else:
                i += 1
            
        # Add the last conversation if it has at least one exchange
        if len(current_conversation) >= 2:
            conversations.append({"messages": current_conversation})
        
        return conversations
    
    def split_data(self, conversations: List[Dict], train_pct: float = 0.9, 
                   valid_pct: float = 0.05) -> Dict[str, List[Dict]]:
        """Split the data into train, validation, and test sets."""
        random.shuffle(conversations)
        n = len(conversations)
        train_idx = int(n * train_pct)
        valid_idx = int(n * (train_pct + valid_pct))
        
        return {
            "train": conversations[:train_idx],
            "valid": conversations[train_idx:valid_idx],
            "test": conversations[valid_idx:]
        }
    
    def save_jsonl(self, data: List[Dict], filename: str):
        """Save data to a JSONL file."""
        with open(filename, 'w', encoding='utf-8') as f:
            for item in data:
                json_str = json.dumps(item, ensure_ascii=False)
                f.write(json_str + '\n')
    
    def process_chat_data(self, input_data: Dict, output_prefix: str = "chat"):
        """Process the chat data and save train/valid/test files."""
        # Print initial statistics
        total_messages = len(input_data["messages"])
        valid_messages = sum(1 for msg in input_data["messages"] if self.is_valid_message(msg))
        messages_with_attachments = sum(1 for msg in input_data["messages"] if "attached_files" in msg)
        messages_without_text = sum(1 for msg in input_data["messages"] 
                                  if "text" not in msg or not msg["text"])
        
        print(f"\nInitial data statistics:")
        print(f"Total messages: {total_messages}")
        print(f"Valid messages: {valid_messages}")
        print(f"Messages with attachments (excluded): {messages_with_attachments}")
        print(f"Messages without text (excluded): {messages_without_text}")
        
        # Create conversations
        conversations = self.create_conversations(input_data["messages"])
        
        # Analyze conversation statistics
        turn_counts = [len(conv["messages"]) for conv in conversations]
        avg_turns = sum(turn_counts) / len(turn_counts) if turn_counts else 0
        
        print(f"\nProcessed data statistics:")
        print(f"Total conversations: {len(conversations)}")
        print(f"Average turns per conversation: {avg_turns:.1f}")
        print(f"Turn distribution:")
        for turns in range(2, self.max_turns * 2 + 1, 2):
            count = sum(1 for tc in turn_counts if tc == turns)
            print(f"  {turns} turns: {count} conversations")
        
        # Split the data
        splits = self.split_data(conversations)
        
        # Save the files
        for split_name, split_data in splits.items():
            self.save_jsonl(split_data, f"{output_prefix}_{split_name}.jsonl")
            print(f"\nSaved {len(split_data)} conversations to {split_name} set")

# Example usage
if __name__ == "__main__":
    # Load your input data with proper UTF-8 encoding
    with open("messages.json", "r", encoding='utf-8') as f:
        input_data = json.load(f)
    
    # Process the data
    processor = ChatProcessor(
        max_user_chars=512,      # Maximum characters for combined user messages
        max_assistant_chars=1024, # Maximum characters for combined assistant messages
        max_turns=6,             # Maximum back-and-forth exchanges in a conversation
        max_conversation_gap=3600 # Maximum seconds (1 hour) between messages
    )
    processor.process_chat_data(input_data)