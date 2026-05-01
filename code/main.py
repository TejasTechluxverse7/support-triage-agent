import os
import csv
import argparse
from datetime import datetime
from classifier import classify_ticket
from risk_checker import check_risk
from retriever import DocumentRetriever
from responder import generate_response

def process_tickets(input_file, output_file, log_file):
    print("Loading knowledge corpus...")
    # Corpus is up one directory relative to code/ assuming execution from code/
    # If run from root, we need to handle paths gracefully.
    base_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(base_dir)
    corpus_path = os.path.join(root_dir, "corpus")
    
    retriever = DocumentRetriever(corpus_dir=corpus_path)
    
    if not retriever.is_fitted:
        print("Warning: Corpus is empty or missing. Retrievals will yield low confidence.")

    tickets = []
    if os.path.exists(input_file):
        with open(input_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                tickets.append(row)
    else:
        print(f"Error: {input_file} not found.")
        return

    results = []
    
    # Ensure log directory exists
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    with open(log_file, "w", encoding="utf-8") as log:
        log.write(f"--- Support Triage Agent Run at {datetime.now()} ---\n\n")
        
        for ticket in tickets:
            issue_text = ticket.get("Issue", "")
            subject = ticket.get("Subject", "")
            company = ticket.get("Company", "None")
            
            full_text = f"{subject} {issue_text}".strip()
            
            log.write(f"Issue: {full_text[:100]}...\n")
            log.write(f"Company: {company}\n")
            
            # 1. Classify
            req_type, prod_area = classify_ticket(full_text)
            log.write(f"Classification -> Type: {req_type}, Area: {prod_area}\n")
            
            # 2. Retrieve (Strictly no cross-product)
            retrieved_docs, confidence = retriever.retrieve(full_text, company=company, top_k=1)
            log.write(f"Retrieval -> Confidence Score (0.7 TFIDF + 0.3 Keyword): {confidence:.2f}\n")
            if retrieved_docs:
                log.write(f"Retrieved Document: {retrieved_docs[0]['source']}\n")
                
            # 3. Decision / Risk Check
            if req_type == "invalid":
                status = "replied"
                justification = "Standard response for out-of-scope/invalid inputs."
            else:
                status, justification = check_risk(full_text, req_type, prod_area, confidence)
                
            # If using fallback troubleshooting, discard irrelevant retrieved docs
            if "generic troubleshooting" in justification:
                retrieved_docs = []
            
            # 4. Generate Response
            response = generate_response(retrieved_docs, req_type, status)
            
            log.write(f"Decision -> {status.upper()} ({justification})\n")
            log.write("-" * 40 + "\n")
            
            # Output MUST match format: status,product_area,response,justification,request_type
            results.append({
                "status": status,
                "product_area": prod_area,
                "response": response.strip(),
                "justification": justification,
                "request_type": req_type
            })

    # Save output CSV
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["status", "product_area", "response", "justification", "request_type"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for res in results:
            writer.writerow(res)
            
    print(f"Processed {len(results)} tickets. Saved to '{output_file}' and '{log_file}'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Terminal-based Support Triage Agent")
    # Resolve default paths dynamically relative to script location
    base_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(base_dir)
    default_input = os.path.join(root_dir, "support_tickets", "support_tickets.csv")
    default_output = os.path.join(root_dir, "output.csv")
    default_log = os.path.join(root_dir, "log.txt")
    
    parser.add_argument("--input", default=default_input, help="Input CSV file")
    parser.add_argument("--output", default=default_output, help="Output CSV file")
    parser.add_argument("--log", default=default_log, help="Text file for logging")
    
    args = parser.parse_args()
    process_tickets(args.input, args.output, args.log)
