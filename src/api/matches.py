from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import boto3
import botocore
import json
import base64
import io
from PIL import Image
from datetime import datetime
import re
from supabase import create_client, Client

router = APIRouter(
    prefix="/matches",
    tags=["matches"],
)

bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')
import os
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

class EntrantInfo(BaseModel):
    name: str
    weapon: str

class FightImageRequest(BaseModel):
    entrant1: EntrantInfo
    entrant2: EntrantInfo

@router.post("/generate_fight_image")
async def generate_fight_image(request: FightImageRequest):
    try:
        prompt = f"An epic battle scene between {request.entrant1.name} wielding a {request.entrant1.weapon} and {request.entrant2.name} wielding a {request.entrant2.weapon}, digital art style"
        
        print("Generating fight image with prompt:", prompt)
        response = bedrock.invoke_model(
            modelId='stability.stable-image-ultra-v1:0',
            body=json.dumps({'prompt': prompt})
        )
        
        print("Response:", response)
        output_body = json.loads(response["body"].read().decode("utf-8"))
        base64_output_image = output_body["images"][0]
        image_data = base64.b64decode(base64_output_image)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name1 = re.sub(r'[^a-zA-Z0-9]', '', request.entrant1.name)
        name2 = re.sub(r'[^a-zA-Z0-9]', '', request.entrant2.name)
        filename = f"fight_{name1}_vs_{name2}_{timestamp}.png"
        
        # Save locally
        with open(filename, 'wb') as f:
            f.write(image_data)
            print(f"Saved image to {filename}")
        
        print("Uploading image to Supabase storage...")
        # Upload to Supabase storage
        with open(filename, 'rb') as f:
            response = supabase.storage.from_('images').upload(
                path=filename,
                file=f,
                file_options={"content-type": "image/png"}
            )
            print("Upload response:", response)
            
        image_url = supabase.storage.from_('images').get_public_url(filename)
        
        return {"image_url": image_url, "local_file": filename}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate fight image: {str(e)}"
        )


class FightStoryRequest(BaseModel):
    entrant1: EntrantInfo
    entrant2: EntrantInfo
    winner: str
    
MODEL_ID = "anthropic.claude-3-5-sonnet-20241022-v2:0"
REGION = 'us-west-2'

@router.post("/generate_fight_story")
async def generate_fight_story(request: FightStoryRequest):
    """Generates a story describing the fight between two entrants using Claude via AWS Bedrock"""
    prompt = f"""Write an exciting short story (2-3 paragraphs) about an epic battle between two fighters:

Fighter 1: {request.entrant1.name} wielding a {request.entrant1.weapon}
Fighter 2: {request.entrant2.name} wielding a {request.entrant2.weapon}

The winner must be: {request.winner}

Make it dramatic and entertaining, incorporating both weapons in creative ways."""

    inference_config = {
        "temperature": 0.7,
        "maxTokens": 4096,
        "topP": 0.95,
    }

    messages = [
        {
            "role": "user",
            "content": [{"text": prompt}]
        }
    ]

    try:
        response = bedrock.converse(
            modelId=MODEL_ID,
            messages=messages,
            inferenceConfig=inference_config,
        )
        story = response['output']['message']['content'][0]['text']
        return {"story": story}
    except botocore.exceptions.ClientError as error:
        if error.response['Error']['Code'] == 'AccessDeniedException':
            raise HTTPException(
                status_code=403,
                detail="AWS Bedrock access denied. Please check your credentials and permissions."
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=str(error)
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate fight story: {str(e)}"
        )