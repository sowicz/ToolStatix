import asyncio
from typing import Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db

from db.models import main_tags, related_tags
from db.models import network_data_source_model
from drivers.OPCUA.opcua_client import OpcUaClient
from drivers.OPCUA.data_handler import DataHandler

from drivers.OPCUA.opcua_new_client import OpcUaConnection
# TESTING
from drivers.OPCUA.opcua_subscription import OpcuaSubscription



router = APIRouter()
ACTIVE_TAGS = {}


@router.post("/opcua/start-subscription/{tag_id}")
async def start_subscription_tag(tag_id: int, db: Session = Depends(get_db)):
        # Request main tag from database
    tag = db.query(main_tags.MainTags).filter(main_tags.MainTags.id == tag_id).first()
    if not tag:
        return {"error": "Invalid tag id"}
    if tag_id in ACTIVE_TAGS:
        return {"status": "already running"}
    
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
    # Launch subscription
    # get data source adress to get singleton client
    server_url = f"opc.tcp://{tag.network_data_sources.server_url}:{tag.network_data_sources.port}"
    connection = OpcUaConnection(server_url)
    client = connection.get_client()
    if not connection.is_connected():
        raise HTTPException(status_code=500, detail="Not connected to OPC UA")
    
    subscription = OpcuaSubscription(id=tag_id, client=client,polls=tag.polls,subscription_handler=data_handler)
    task = asyncio.create_task(subscription.run(tag_addresses))
        # wait few seconds for connection
    for _ in range(50):
        await asyncio.sleep(0.1)
        if subscription.is_running():
            break

    # Check if client is running if not return error
    if not subscription.is_running():
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        raise HTTPException(status_code=504, detail="OPC UA connection timeout")

    ACTIVE_TAGS[tag_id] = {
        "task": task,
        "subscription": subscription
    }
    return {"status": f"tag {tag_id} started"}


@router.post("/opcua/stop-subscription/{tag_id}")
async def stop_subscription_tag(tag_id: int):
    if tag_id not in ACTIVE_TAGS:
        raise HTTPException(status_code=404, detail="No active subscription for this tag")

    task = ACTIVE_TAGS[tag_id].get("task")
    subscription = ACTIVE_TAGS[tag_id].get("subscription") 

    if subscription:
        await subscription.stop()

    if task:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    # Usuń z rejestru
    del ACTIVE_TAGS[tag_id]

    return {"status": f"tag {tag_id} subscription stopped"}


@router.post("/opcua/connect/{data_source_id}")
async def opcua_connect(data_source_id: int ,db: Session = Depends(get_db)):

    data_source = db.query(network_data_source_model.NetworkDataSource).filter(
        network_data_source_model.NetworkDataSource.id == data_source_id).first()
    server_url = f"opc.tcp://{data_source.server_url}:{data_source.port}"
    node_id = 'ns=2;s=Channel1.TEST.sine1'

    opc = OpcUaConnection(server_url)
    await opc.connect()
    if not opc.is_connected():
        raise HTTPException(status_code=500, detail="Can't connect to OPC UA")
    
    client = opc.get_client()
    try:
        node = client.get_node(node_id)
        value = await node.read_value()
        return {
            "node_id": node_id,
            "value": value
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading: {e}")
    

@router.post("/opcua/disconnect/{data_source_id}")
async def disconnect_opcua(data_source_id: int,db: Session = Depends(get_db)):

    data_source = db.query(network_data_source_model.NetworkDataSource).filter(
        network_data_source_model.NetworkDataSource.id == data_source_id).first()
    if not data_source:
        raise HTTPException(status_code=404, detail=f"Can't find data source with id {data_source_id}")
    server_url = f"opc.tcp://{data_source.server_url}:{data_source.port}"

    opc = OpcUaConnection(server_url)

    if not opc.is_connected():
        raise HTTPException(status_code=400, detail="Already disconnected")

    await opc.disconnect()
    return {"status": f"Disconnect with opcua"}


@router.get("/active-tags")
def check_connections():
    return {
        "running_instances": list(ACTIVE_TAGS.keys())
    }


@router.get("/status/{tag_id}")
def status(tag_id: int):
    entry = ACTIVE_TAGS.get(tag_id)
    if not entry:
        return {"status": "not running"}

    subscription = entry["subscription"]
    return {
        "status": "running" if subscription.is_running() else "stopped"
    }



