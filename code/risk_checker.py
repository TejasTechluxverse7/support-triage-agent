def check_risk(ticket_text, request_type, product_area, retrieval_confidence):
    """
    Evaluates the risk of a ticket.
    Escalate ONLY for: fraud / billing / account compromise, OR no relevant docs AND unsafe.
    """
    text_lower = ticket_text.lower()
    
    # 1. Strict high-risk keywords for fraud/billing/compromise
    high_risk_keywords = ["fraud", "unauthorized", "stolen", "compromised", "hacked", "scam", "identity theft", "urgent need for cash"]
    if any(kw in text_lower for kw in high_risk_keywords):
        return "escalated", "High-risk financial or security keywords detected."
        
    # Escalation by product area mapping
    if product_area == "payments" and any(w in text_lower for w in ["charge", "refund", "dispute"]):
        return "escalated", "Sensitive billing or payment issue detected."

    # 2. Confidence handling
    CONFIDENCE_VERY_LOW = 0.25
    CONFIDENCE_SLIGHTLY_LOW = 0.40
    
    if retrieval_confidence < CONFIDENCE_VERY_LOW:
        if request_type == "bug":
            # If very low confidence but it's a bug, we can offer safe generic troubleshooting
            return "replied", "Low confidence but provided safe generic troubleshooting for bug."
        else:
            return "escalated", "Low confidence and no safe automated resolution."
            
    if retrieval_confidence < CONFIDENCE_SLIGHTLY_LOW:
        # If slightly low, we reply if it's a safe category (e.g. feature request, general product issue)
        if request_type in ["feature_request", "invalid"]:
            return "replied", "Slightly low confidence but safe category."
        if product_area not in ["authentication", "security_and_privacy"]:
            return "replied", "Slightly low confidence but safe product area."
        else:
            return "escalated", "Slightly low confidence for a sensitive product area."

    return "replied", "Strong match found in corpus and no high-risk factors."
