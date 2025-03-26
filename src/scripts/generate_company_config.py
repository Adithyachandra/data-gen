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
    company_description = input("Enter company description: ").strip()
    industry = input("Enter company industry: ").strip()
    
    return {
        "name": company_name,
        "description": company_description,
        "industry": industry
    }

def generate_company_structure(llm: LLMGenerator, company_info: Dict[str, str]) -> Dict[str, any]:
    """Generate company structure using LLM."""
    prompt = f"""Based on the following company information, generate a realistic company structure with business units, teams, products, and initiatives.

Company Name: {company_info['name']}
Description: {company_info['description']}
Industry: {company_info['industry']}

Generate a JSON structure with:
1. 2-4 business units with appropriate names and descriptions
2. 2-3 teams per business unit with realistic team sizes (5-15 members)
3. 1-2 products with 2-3 initiatives each

The structure should be realistic and aligned with the company's industry and description.
Return only the JSON structure, no additional text."""

    # Get the generated structure from LLM
    response = llm.client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a business analyst expert at generating realistic company structures."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1000
    )
    
    # Parse the response into a dictionary
    try:
        structure = json.loads(response.choices[0].message.content)
        return structure
    except json.JSONDecodeError:
        print("Error: Could not parse LLM response as JSON")
        raise

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