from fastapi import HTTPException
from pydantic import BaseModel
import boto3
from dotenv import load_dotenv
import os
from colorama import Fore, Style
load_dotenv()

GUARDRAIL_ID = os.getenv("GUARDRAIL_ID")
GUARDRAIL_VERSION = os.getenv("GUARDRAIL_VERSION")

bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')

class Entrant(BaseModel):
    name: str
    weapon: str

async def validate_entrant(entrant: Entrant):
    try:
        print(f"{Fore.GREEN}Validating entrant with Guardrails...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Name: {entrant.name}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Weapon: {entrant.weapon}{Style.RESET_ALL}")
        # Check name
        name_response = bedrock.apply_guardrail(
            guardrailIdentifier=GUARDRAIL_ID,
            guardrailVersion=GUARDRAIL_VERSION,
            source='INPUT',
            content=[{"text": {"text": entrant.name}}]
        )

        # Check weapon
        weapon_response = bedrock.apply_guardrail(
            guardrailIdentifier=GUARDRAIL_ID,
            guardrailVersion=GUARDRAIL_VERSION,
            source='INPUT',
            content=[{"text": {"text": entrant.weapon}}]
        )
        
        if name_response['action'] != 'NONE':
            print(f"{Fore.RED}Name validation failed: {name_response['action']}{Style.RESET_ALL}")
        if weapon_response['action'] != 'NONE':
            print(f"{Fore.RED}Weapon validation failed: {weapon_response['action']}{Style.RESET_ALL}")
            
        # Return True only if both checks pass
        return (name_response['action'] == 'NONE' and 
                weapon_response['action'] == 'NONE')
                
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Guardrail validation failed: {str(e)}"
        )