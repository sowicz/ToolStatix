import asyncio
from typing import Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db

from db.models import main_tags, related_tags
from db.models import network_data_source_model
from drivers.OPCUA.opcua_client import OpcUaClient
from drivers.OPCUA.data_handler import DataHandler


router = APIRouter()
active_tags = {}

@router.post("/start/{tag_id}")
async def start_worker_route(tag_id: int, db: Session = Depends(get_db)):
    # Request main tag from database
    tag = db.query(main_tags.MainTags).filter(main_tags.MainTags.id == tag_id).first()
    if not tag:
        return {"error": "Invalid tag id"}

    if tag_id in active_tags:
        return {"status": "already running"}

    # Prepare data for connection opcua
    tag_url = f"opc.tcp://{tag.network_data_sources.server_url}:{tag.network_data_sources.port}/"
    main_tag_address = tag.tag_address
    main_tag_name = tag.tag_name

    # Request related tag to main tag
    related_tags_list = db.query(related_tags.RelatedTags).filter(
        related_tags.RelatedTags.main_tag_id == tag.id
    ).all()

    # Mapa nodeid -> tag_name (fallback: nodeid)
    nodeid_to_name = {
        main_tag_address: main_tag_name
    }
    for t in related_tags_list:
        nodeid_to_name[t.tag_address] = t.tag_name or t.tag_address

    # Create tag_adresses list with only addresses
    tag_addresses = list(nodeid_to_name.keys())


    # Create data handler to map in opcUa - and store main tag threshold (power in Amps)
    data_handler = DataHandler(
        tag_id=tag.id,
        main_nodeid=main_tag_address,
        nodeid_to_name=nodeid_to_name,
        threshold=tag.threshold,
        db=db
    )

    # Launch client
    client = OpcUaClient(id=tag_id, url=tag_url, polls=500, subscription_handler=data_handler)
    task = asyncio.create_task(client.run(tag_addresses))

    # wait few seconds for connection
    for _ in range(50):
        await asyncio.sleep(0.1)
        if client.is_running():
            break

    # Check if client is running if not return error
    if not client.is_running():
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        raise HTTPException(status_code=504, detail="OPC UA connection timeout")

    active_tags[tag_id] = {
        "client": client,
        "task": task
    }
    return {"status": f"tag {tag_id} started"}



@router.post("/stop/{tag_id}")
async def stop_worker_route(tag_id: int):
    entry = active_tags.get(tag_id)
    if not entry:
        return {"status": "not running"}

    client: OpcUaClient = entry["client"]
    await client.stop()

    entry["task"].cancel()
    try:
        await entry["task"]
    except asyncio.CancelledError:
        pass

    del active_tags[tag_id]
    return {"status": "stopped"}





@router.get("/active-tags")
def check_connections():
    return {
        "running_instances": list(active_tags.keys())
    }


@router.get("/status/{tag_id}")
def status(tag_id: int):
    entry = active_tags.get(tag_id)
    if not entry:
        return {"status": "not running"}

    client = entry["client"]
    return {
        "status": "running" if client.is_running() else "stopped"
    }



