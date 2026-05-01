import re

def classify_product_area(text):
    text_lower = text.lower()
    
    # 1. Payments / Financial
    payments_keywords = ["money", "payment", "refund", "charge", "card", "invoice", "billing", "subscription", "pricing", "cost", "spend", "cheque", "minimum spend"]
    if any(kw in text_lower for kw in payments_keywords):
        return "payments"
        
    # 2. Authentication
    auth_keywords = ["login", "password", "access", "account", "locked", "sign up", "sign in", "reset", "cannot login"]
    if any(kw in text_lower for kw in auth_keywords):
        return "authentication"
        
    # 3. Assessments
    assessment_keywords = ["mock interview", "test", "submission", "compiler", "assessment", "score", "interviewer", "candidate", "variant", "challenge", "hackerrank test", "time limit", "practice"]
    if any(kw in text_lower for kw in assessment_keywords):
        return "assessments"
        
    # 4. Permissions
    permission_keywords = ["permission", "role", "admin", "remove", "seat", "workspace", "invite", "add user", "privilege"]
    if any(kw in text_lower for kw in permission_keywords):
        return "permissions"
        
    # 5. Security & Privacy
    security_keywords = ["privacy", "data", "crawl", "stolen", "vulnerability", "security", "gdpr", "delete account", "identity"]
    if any(kw in text_lower for kw in security_keywords):
        return "security_and_privacy"
        
    return "general_support"

def classify_request_type(text, product_area):
    text_lower = text.lower()
    
    # 1. Invalid
    invalid_keywords = ["thank you", "thanks", "hello", "hi", "hey", "good morning", "good evening", "name of the actor"]
    if not text.strip() or text_lower.strip() in invalid_keywords or "name of the actor" in text_lower:
        return "invalid"
        
    # 2. Feature Request
    feature_keywords = ["would like to request", "would be helpful", "can you add", "feature request", "please implement", "idea for", "would like to"]
    if any(kw in text_lower for kw in feature_keywords):
        return "feature_request"

    # 3. Product Issue override (CRITICAL: Payments are NEVER bugs)
    if product_area == "payments":
        return "product_issue"

    # 4. Bug
    bug_keywords = ["bug", "down", "not working", "crash", "error", "failing", "blocker", "vulnerability", "issue with", "stopped working"]
    if any(kw in text_lower for kw in bug_keywords):
        return "bug"
        
    # Default
    return "product_issue"

def classify_ticket(ticket_text):
    prod_area = classify_product_area(ticket_text)
    req_type = classify_request_type(ticket_text, prod_area)
    return req_type, prod_area
