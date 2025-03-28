import json
import os
from typing import Dict, List
from datetime import datetime
from pathlib import Path
from src.generators.llm_generator import LLMGenerator

def get_company_info() -> Dict[str, str]:
    """Get basic company information from user input."""
    print("\n=== Company Configuration Generator ===\n")
    
    # Basic company information
    company_name = input("Enter company name: ").strip()
    print("\nEnter company description:")
    company_description = input().strip()
    industry = input("\nEnter company industry: ").strip()
    
    return {
        "name": company_name,
        "description": company_description,
        "industry": industry
    }

def generate_company_structure(llm: LLMGenerator, company_info: Dict[str, str]) -> Dict[str, any]:
    """Generate company structure using LLM."""
    # Extract location information from description if possible
    location = "United States"  # Default to US
    description = company_info['description'].lower()
    if "india" in description or "indian" in description:
        location = "India"
    elif "uk" in description or "britain" in description or "united kingdom" in description:
        location = "United Kingdom"
    elif "europe" in description or "eu" in description:
        location = "Europe"
    elif "asia" in description and "india" not in description:
        location = "Asia"
    
    prompt = f"""Based on the following company information, generate a detailed company configuration with products and initiatives.

Company Name: {company_info['name']}
Description: {company_info['description']}
Industry: {company_info['industry']}
Location: {location}

Generate a JSON structure that MUST follow this exact format:
{{
    "products": [
        {{
            "name": "string",
            "description": "string",
            "initiatives": [
                {{
                    "name": "string",
                    "description": "string"
                }}
            ]
        }}
    ]
}}

Requirements:
1. Products (1-2):
   - Include detailed product features and purpose
   - Each product should have 2-3 initiatives

2. Initiatives:
   - Each initiative should have clear goals and expected outcomes
   - Initiatives should be realistic and aligned with the company's industry

The structure should be realistic and aligned with the company's industry and description.
IMPORTANT: Return ONLY the JSON object, no additional text or explanation."""

    # Get the generated structure from LLM
    response = llm.client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a business analyst expert at generating realistic company structures. You must return ONLY valid JSON that matches the exact structure provided, with no additional text."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=3000
    )
    
    # Get the response content and clean it
    content = response.choices[0].message.content.strip()
    
    # Try to find JSON content if there's any additional text
    try:
        # First try parsing the entire content
        structure = json.loads(content)
    except json.JSONDecodeError:
        try:
            # Try to find JSON between curly braces
            start = content.find('{')
            end = content.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = content[start:end]
                structure = json.loads(json_str)
            else:
                raise ValueError("No valid JSON found in response")
        except Exception as e:
            print(f"Error parsing LLM response: {str(e)}")
            print("Raw response:", content)
            raise
    
    # Validate the structure has required fields
    required_fields = ['products']
    missing_fields = [field for field in required_fields if field not in structure]
    if missing_fields:
        raise ValueError(f"Generated structure missing required fields: {missing_fields}")
    
    return structure

def save_config(config: Dict[str, any], output_dir: str = "config") -> str:
    """Save the configuration to a JSON file."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename based on company name
    company_name = config["company"]["name"].lower().replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{company_name}_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    # Save configuration
    with open(filepath, "w") as f:
        json.dump(config, f, indent=2)
    
    return filepath

def main():
    # Initialize LLM generator
    llm = LLMGenerator()
    
    # Get basic company information
    company_info = get_company_info()
    
    print("\nGenerating company structure using AI...")
    
    try:
        # Generate company structure using LLM
        structure = generate_company_structure(llm, company_info)
        
        # Create final configuration
        config = {
            "company": {
                **company_info,
                "created_at": datetime.now().isoformat()
            },
            **structure
        }
        
        # Save configuration
        filepath = save_config(config)
        
        print(f"\nCompany configuration saved to: {filepath}")
        print("\nYou can now use this configuration file to generate tickets and other data.")
        
    except Exception as e:
        print(f"\nError generating company structure: {str(e)}")
        print("Please try again or check your input.")

if __name__ == "__main__":
    main() 