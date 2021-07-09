#!/usr/bin/env python3

import asyncio
from tello_asyncio_video.websocket import run_tello_video_app_websocket

async def fly(drone):
    await asyncio.sleep(30)
    # await drone.takeoff()
    # await drone.turn_clockwise(360)
    # await drone.land()

run_tello_video_app_websocket(fly)