def format_as_steps(text):
    """
    Converts raw text into short, actionable, step-based answers.
    It attempts to find sequential actions and bullet points.
    """
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if not lines:
        return text
        
    formatted_lines = []
    step_counter = 1
    
    for line in lines:
        # If line is already a numbered list or bullet, preserve it
        if line[0].isdigit() and len(line) > 1 and line[1] in [".", ")"]:
            formatted_lines.append(f"{line}")
        elif line.startswith("-") or line.startswith("*"):
            formatted_lines.append(f"{line}")
        else:
            # Check if line looks like an instruction
            action_verbs = ("Go to", "Click", "Select", "Enter", "Log in", "Navigate", "Scroll", "Call", "Follow", "Review")
            if any(line.startswith(verb) for verb in action_verbs):
                formatted_lines.append(f"{step_counter}. {line}")
                step_counter += 1
            else:
                # Add as regular text
                formatted_lines.append(line)
                
    return "\n".join(formatted_lines)

def generate_response(retrieved_docs, request_type, status):
    """
    Generates an actionable response. 
    Adds fallback safe responses for bugs.
    """
    if request_type == "invalid":
        return "I am sorry, this is out of scope from my capabilities."
        
    if status == "escalated":
        return "Your ticket has been escalated to a human agent for further review."
        
    # Fallback safe responses for bugs when retrieval is low/absent (checked in risk_checker)
    if not retrieved_docs and request_type == "bug":
        return "Please try clearing your browser cache, restarting the application, or checking your internet connection. If the issue persists, a human agent will assist you shortly."
        
    if not retrieved_docs:
        return "We could not find an automated resolution for your issue. Escalating to human support."
        
    best_doc = retrieved_docs[0]
    
    # Do NOT dump raw text, convert into steps
    formatted_text = format_as_steps(best_doc['text'])
    
    return formatted_text
