import re

def classify_request_type(text):
    text_lower = text.lower()
    
    # 1. invalid: greetings, empty, irrelevant
    invalid_keywords = ["thank you", "thanks", "hello", "hi", "hey", "good morning", "good evening", "name of the actor"]
    if not text.strip() or text_lower.strip() in invalid_keywords or "name of the actor" in text_lower:
        return "invalid"
    
    # 2. feature_request: "would like", "it would be helpful", "can you add"
    feature_keywords = ["would like to request", "would be helpful", "can you add", "feature request", "please implement", "idea for", "would like to"]
    if any(kw in text_lower for kw in feature_keywords):
        return "feature_request"

    # 3. bug: errors, crash, failing, not working
    bug_keywords = ["bug", "down", "not working", "crash", "error", "failing", "blocker", "vulnerability", "issue with", "stopped working"]
    if any(kw in text_lower for kw in bug_keywords):
        return "bug"
        
    # 4. Default
    return "product_issue"

def classify_product_area(text):
    text_lower = text.lower()
    
    # Richer keyword mapping
    area_mapping = {
        "authentication": ["login", "password", "access", "account", "locked", "sign up", "sign in", "reset", "cannot login"],
        "payments": ["payment", "charge", "refund", "card", "money", "billing", "subscription", "invoice", "pricing", "cost", "spend", "cheque", "minimum spend"],
        "assessments": ["test", "assessment", "score", "submissions", "interviewer", "candidate", "variant", "challenge", "hackerrank test", "time limit", "compile", "practice"],
        "permissions": ["permission", "role", "admin", "remove", "seat", "workspace", "invite", "add user", "privilege"],
        "security_and_privacy": ["privacy", "data", "crawl", "stolen", "vulnerability", "security", "gdpr", "delete account", "identity"]
    }
    
    for area, keywords in area_mapping.items():
        if any(kw in text_lower for kw in keywords):
            return area
            
    return "general_support"

def classify_ticket(ticket_text):
    """
    Classifies the ticket to identify the request_type and product_area.
    """
    req_type = classify_request_type(ticket_text)
    prod_area = classify_product_area(ticket_text)
    return req_type, prod_area
