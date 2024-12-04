from fastapi import HTTPException
from pydantic import BaseModel
import boto3
import botocore
import json
import base64
from io import BytesIO
from datetime import datetime
import re
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import src.database as db
import sqlalchemy
from colorama import Fore, Style

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
IMAGE_MODEL_ID = "stability.stable-image-ultra-v1:0"


async def generate_fight_image(request: FightImageRequest, match_id: int):
    print(f"{Fore.GREEN}Generating fight image: {request}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Match ID: {match_id}{Style.RESET_ALL}")
    try: 
        prompt = f"An epic battle scene between {request.entrant1.name} wielding a {request.entrant1.weapon} and {request.entrant2.name} wielding a {request.entrant2.weapon}, digital art style"[:70]
        
        response = bedrock.invoke_model(
            modelId=IMAGE_MODEL_ID,
            body=json.dumps({'prompt': prompt})
        )
        
        output_body = json.loads(response["body"].read().decode("utf-8"))
        base64_output_image = output_body["images"][0]
        image_data = base64.b64decode(base64_output_image)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name1 = re.sub(r'[^a-zA-Z0-9]', '', request.entrant1.name)
        name2 = re.sub(r'[^a-zA-Z0-9]', '', request.entrant2.name)
        filename = f"fight_{name1}_vs_{name2}_{timestamp}.png"

        image_file = BytesIO(image_data)
        response = supabase.storage.from_('images').upload(
            path=filename,
            file=image_file.getvalue(),
            file_options={"content-type": "image/png"}
        )
            
        image_url = supabase.storage.from_('images').get_public_url(filename)

        upload_match_image(image_url, match_id)
        
        print(f"{Fore.GREEN}Fight image generated successfully!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Image URL: {image_url}{Style.RESET_ALL}")
        return {"image_url": image_url, "local_file": filename}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate fight image: {str(e)}"
        )


async def generate_entrant_image(entrant: EntrantInfo, entrant_id: int):
    print(f"{Fore.GREEN}Generating entrant image: {entrant}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Entrant ID: {entrant_id}{Style.RESET_ALL}")
    try:
        prompt = f"An epic character portrait of {entrant.name} wielding a {entrant.weapon}, digital art style"[:70]

        response = bedrock.invoke_model(
            modelId=IMAGE_MODEL_ID,
            body=json.dumps({'prompt': prompt})
        )

        output_body = json.loads(response["body"].read().decode("utf-8"))
        base64_output_image = output_body["images"][0]
        image_data = base64.b64decode(base64_output_image)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = re.sub(r'[^a-zA-Z0-9]', '', entrant.name)
        weapon = re.sub(r'[^a-zA-Z0-9]', '', entrant.weapon)
        filename = f"entrant_{name}_w_{weapon}_{timestamp}.png"

        image_file = BytesIO(image_data)
        response = supabase.storage.from_('images').upload(
            path=filename,
            file=image_file.getvalue(),
            file_options={"content-type": "image/png"}
        )

        image_url = supabase.storage.from_('images').get_public_url(filename)

        upload_entrant_image(image_url, entrant_id)
        
        print(f"{Fore.GREEN}Entrant image generated successfully!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Image URL: {image_url}{Style.RESET_ALL}")
        return {"image_url": image_url, "local_file": filename}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate entrant image: {str(e)}"
        )

async def generate_fight_story(request: FightStoryRequest, match_id: int):
    print(f"{Fore.GREEN}Generating fight story: {request}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Match ID: {match_id}{Style.RESET_ALL}")
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

        upload_match_story(story, match_id)
        
        print(f"{Fore.GREEN}Fight story generated successfully!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Story: {story[:100]}...{Style.RESET_ALL}")
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


def upload_match_image(img_url: str, match_id: int):
    print(f"{Fore.GREEN}Uploading match image to Supabase...{Style.RESET_ALL}")
    upload_query = sqlalchemy.text("""
        UPDATE matches
        SET img_url = :img_url
        WHERE id = :match_id
    """)

    try:
        with db.engine.begin() as con:
            con.execute(upload_query, {
                'img_url': img_url, 'match_id': match_id
            })
        print(f"{Fore.GREEN}Match image uploaded successfully!{Style.RESET_ALL}")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to update match img_url in Supabase. Error: " + str(e)
        )


def upload_match_story(story: str, match_id: int):
    print(f"{Fore.GREEN}Uploading match story to Supabase...{Style.RESET_ALL}")
    upload_query = sqlalchemy.text("""
        UPDATE matches
        SET story = :story
        WHERE id = :match_id
    """)

    try:
        with db.engine.begin() as con:
            con.execute(upload_query, {
                'story': story, 'match_id': match_id
            })
        print(f"{Fore.GREEN}Match story uploaded successfully!{Style.RESET_ALL}")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to update match story in Supabase. Error: " + str(e)
        )


def upload_entrant_image(img_url: str, entrant_id: int):
    print(f"{Fore.GREEN}Uploading entrant image to Supabase...{Style.RESET_ALL}")
    upload_query = sqlalchemy.text("""
        UPDATE entrants
        SET img_url = :img_url
        WHERE id = :entrant_id
    """)

    try:
        with db.engine.begin() as con:
            con.execute(upload_query, {
                'img_url': img_url, 'entrant_id': entrant_id
            })
        print(f"{Fore.GREEN}Entrant image uploaded successfully!{Style.RESET_ALL}")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to update entrant img_url in Supabase. Error: " + str(e)
        )
