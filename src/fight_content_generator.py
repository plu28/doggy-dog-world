from fastapi import HTTPException
from pydantic import BaseModel
import boto3
import botocore
import json
import base64
from datetime import datetime
import re
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')
bedrock_client = boto3.client('bedrock', region_name='us-west-2')

supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_KEY"]
)

class EntrantInfo(BaseModel):
    name: str
    weapon: str

class FightImageRequest(BaseModel):
    entrant1: EntrantInfo
    entrant2: EntrantInfo
    
class FightStoryRequest(BaseModel):
    entrant1: EntrantInfo
    entrant2: EntrantInfo
    winner: str

FIGHT_STORY_MODEL_ID = "meta.llama3-70b-instruct-v1:0"

async def generate_fight_image(request: FightImageRequest):
    try: 
        prompt = f"An epic battle scene between {request.entrant1.name} wielding a {request.entrant1.weapon} and {request.entrant2.name} wielding a {request.entrant2.weapon}, digital art style"
        
        response = bedrock.invoke_model(
            modelId='stability.stable-image-ultra-v1:0',
            body=json.dumps({'prompt': prompt})
        )
        
        output_body = json.loads(response["body"].read().decode("utf-8"))
        base64_output_image = output_body["images"][0]
        image_data = base64.b64decode(base64_output_image)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name1 = re.sub(r'[^a-zA-Z0-9]', '', request.entrant1.name)
        name2 = re.sub(r'[^a-zA-Z0-9]', '', request.entrant2.name)
        filename = f"fight_{name1}_vs_{name2}_{timestamp}.png"
        
        with open(filename, 'wb') as f:
            f.write(image_data)
        
        with open(filename, 'rb') as f:
            response = supabase.storage.from_('images').upload(
                path=filename,
                file=f,
                file_options={"content-type": "image/png"}
            )
            
        image_url = supabase.storage.from_('images').get_public_url(filename)
        
        return {"image_url": image_url, "local_file": filename}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate fight image: {str(e)}"
        )


async def generate_entrant_image(entrant: EntrantInfo):
    try:
        prompt = f"An epic character portrait of {entrant.name} wielding a {entrant.weapon}, digital art style"

        response = bedrock.invoke_model(
            modelId='stability.stable-image-ultra-v1:0',
            body=json.dumps({'prompt': prompt})
        )

        output_body = json.loads(response["body"].read().decode("utf-8"))
        base64_output_image = output_body["images"][0]
        image_data = base64.b64decode(base64_output_image)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = re.sub(r'[^a-zA-Z0-9]', '', entrant.name)
        weapon = re.sub(r'[^a-zA-Z0-9]', '', entrant.weapon)
        filename = f"fight_{name}_w_{weapon}_{timestamp}.png"

        with open(filename, 'wb') as f:
            f.write(image_data)

        with open(filename, 'rb') as f:
            response = supabase.storage.from_('images').upload(
                path=filename,
                file=f,
                file_options={"content-type": "image/png"}
            )

        image_url = supabase.storage.from_('images').get_public_url(filename)

        return {"image_url": image_url, "local_file": filename}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate entrant image: {str(e)}"
        )

async def generate_fight_story(request: FightStoryRequest):
    try:
        if request.winner not in [request.entrant1.name, request.entrant2.name]:
            raise HTTPException(
                status_code=400,
                detail="Winner must be one of the entrants"
            )

        prompt = f"""Create an epic battle chronicle in Star Wars opening crawl style:

        A LEGENDARY DUEL
        BETWEEN TWO WARRIORS

        {request.entrant1.name.upper()} 
        Armed with: {request.entrant1.weapon}

        VERSUS

        {request.entrant2.name.upper()}
        Armed with: {request.entrant2.weapon}

        Write an epic 5-7 sentence story that unfolds like a legend, using present tense and cinematic language. The story should:

        1. Start with an atmospheric scene-setting sentence
        2. Introduce both warriors with their weapons, building tension
        3. Describe 2-3 dramatic exchanges of combat, showcasing both fighters' skills
        4. Build to a climactic moment where the tide turns
        5. End with {request.winner}'s decisive victory

        Keep sentences powerful but not too long, perfect for scrolling text. Focus on visual imagery and dramatic action that brings the battle to life. Your response must start with the words THE BATTLE BEGINS"""

        inference_config = {
            "temperature": 0.7,
            "maxTokens": 2048,
            "topP": 0.95,
        }

        messages = [
            {
                "role": "user",
                "content": [{"text": prompt}]
            }
        ]

        response = bedrock.converse(
            modelId=FIGHT_STORY_MODEL_ID,
            messages=messages,
            inferenceConfig=inference_config,
        )
        story = response['output']['message']['content'][0]['text']
        return story
    except HTTPException:
        raise
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