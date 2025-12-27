import asyncio
from typing import Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db

from db.models import main_tags, related_tags
from db.models import network_data_source_model

from drivers.OPCUA.data_handler import DataHandler
from drivers.OPCUA.opcua_manager import OpcUaConnectionManager
# TESTING
# from drivers.OPCUA.opcua_subscription import OpcuaSubscription



router = APIRouter()
ACTIVE_TAGS = {}


@router.post("/opcua/start-subscription/{tag_id}")
async def start_subscription_tag(
    tag_id: int,
    db: Session = Depends(get_db)
):
    # 1️⃣ Pobranie main tag
    tag = (
        db.query(main_tags.MainTags)
        .filter(main_tags.MainTags.id == tag_id)
        .first()
    )

    if not tag:
        raise HTTPException(status_code=404, detail="Invalid tag id")

    if tag_id in ACTIVE_TAGS:
        return {"status": "already running"}

    main_tag_address = tag.tag_address
    main_tag_name = tag.tag_name

    # 2️⃣ Pobranie related tags
    related_tags_list = (
        db.query(related_tags.RelatedTags)
        .filter(related_tags.RelatedTags.main_tag_id == tag.id)
        .all()
    )

    # 3️⃣ Mapa nodeid → tag_name
    nodeid_to_name = {
        main_tag_address: main_tag_name
    }

    for t in related_tags_list:
        nodeid_to_name[t.tag_address] = t.tag_name or t.tag_address

    tag_addresses = list(nodeid_to_name.keys())

    # 4️⃣ DataHandler
    data_handler = DataHandler(
        tag_id=tag.id,
        main_nodeid=main_tag_address,
        nodeid_to_name=nodeid_to_name,
        threshold=tag.threshold,
        db=db
    )

    # 5️⃣ OPC UA connection (PRZEZ MANAGERA)
    server_url = (
        f"opc.tcp://"
        f"{tag.network_data_sources.server_url}:"
        f"{tag.network_data_sources.port}"
    )

    try:
        connection = await OpcUaConnectionManager.get_connection(server_url)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to connect to OPC UA: {e}"
        )

    if not connection.is_connected():
        raise HTTPException(
            status_code=500,
            detail="Not connected to OPC UA"
        )

    client = connection.get_client()

    # 6️⃣ Subskrypcja
    subscription = OpcuaSubscription(
        id=tag_id,
        client=client,
        polls=tag.polls,
        subscription_handler=data_handler
    )

    task = asyncio.create_task(subscription.run(tag_addresses))

    # 7️⃣ Czekamy aż subskrypcja faktycznie ruszy
    for _ in range(50):
        await asyncio.sleep(0.1)
        if subscription.is_running():
            break

    if not subscription.is_running():
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

        raise HTTPException(
            status_code=504,
            detail="OPC UA subscription timeout"
        )

    # 8️⃣ Rejestracja aktywnej subskrypcji
    ACTIVE_TAGS[tag_id] = {
        "task": task,
        "subscription": subscription,
        "server_url": server_url
    }

    return {
        "status": "started",
        "tag_id": tag_id,
        "server_url": server_url
    }


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
async def opcua_connect(
    data_source_id: int,
    db: Session = Depends(get_db)
):
    data_source = db.query(
        network_data_source_model.NetworkDataSource
    ).filter(
        network_data_source_model.NetworkDataSource.id == data_source_id
    ).first()

    if not data_source:
        raise HTTPException(404, "Data source not found")

    server_url = f"opc.tcp://{data_source.server_url}:{data_source.port}"
    node_id = "ns=2;s=Channel1.TEST.sine1"

    # OPCUA connectionManager
    opc = await OpcUaConnectionManager.get_connection(server_url)

    # TODO
    # Connection manager not working properly
    if not opc.is_connected():
        raise HTTPException(500, "Can't connect to OPC UA")

    try:
        client = opc.get_client()
        node = client.get_node(node_id)
        value = await node.read_value()

        return {
            "server_url": server_url,
            "connected": True,
            "node_id": node_id,
            "value": value
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading node value: {e}"
        )
    

@router.post("/opcua/disconnect/{data_source_id}")
async def disconnect_opcua(
    data_source_id: int,
    db: Session = Depends(get_db)
):
    data_source = db.query(
        network_data_source_model.NetworkDataSource
    ).filter(
        network_data_source_model.NetworkDataSource.id == data_source_id
    ).first()

    if not data_source:
        raise HTTPException(
            status_code=404,
            detail=f"Can't find data source with id {data_source_id}"
        )

    server_url = f"opc.tcp://{data_source.server_url}:{data_source.port}"

    # OPCUA connectionManager
    conn = OpcUaConnectionManager._connections.get(server_url)

    if not conn or not conn.is_connected():
        raise HTTPException(status_code=400, detail="Already disconnected")

    await conn.disconnect()

    return {
        "server_url": server_url,
        "connected": False
    }


@router.get("/active-tags")
def check_connections():
    return {
        "running_instances": list(ACTIVE_TAGS.keys())
    }


@router.get("/status/tag/{tag_id}")
def status(tag_id: int):
    entry = ACTIVE_TAGS.get(tag_id)

    if not entry:
        return {"status": "not running"}

    subscription = entry["subscription"]

    return {
        "status": "running" if subscription.is_running() else "stopped"
    }


@router.get("/opcua/status/data-source/{data_source_id}")
async def opcua_status(
    data_source_id: int,
    db: Session = Depends(get_db)
):
    data_source = (
        db.query(network_data_source_model.NetworkDataSource)
        .join(network_data_source_model.NetworkDataSource.machines)
        .filter(
            network_data_source_model.NetworkDataSource.id == data_source_id
        )
        .first()
    )

    if not data_source:
        raise HTTPException(404, "Data source not found")

    server_url = f"opc.tcp://{data_source.server_url}:{data_source.port}"

    return {
        "data_source_id": data_source.id,
        "machine_id": data_source.machine_id,
        "machine_name": data_source.machines.name,
        "server_url": server_url,
        "connected": OpcUaConnectionManager.is_connected(server_url)
    }



@router.get("/opcua/status/data-sources-all")
async def opcua_data_sources_status(
    db: Session = Depends(get_db)
):
    data_sources = (
        db.query(network_data_source_model.NetworkDataSource)
        .join(network_data_source_model.NetworkDataSource.machines)
        .all()
    )

    result = []

    for ds in data_sources:
        server_url = f"opc.tcp://{ds.server_url}:{ds.port}"

        result.append({
            "data_source_id": ds.id,
            "machine_id": ds.machine_id,
            "machine_name": ds.machines.name,
            "protocol": ds.protocol,
            "server_url": server_url,
            "connected": OpcUaConnectionManager.is_connected(server_url)
        })

    return result