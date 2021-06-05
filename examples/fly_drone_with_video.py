#!/usr/bin/env python3

import asyncio
from tello_asyncio_video import run_tello_video_app

async def fly(drone):
    await drone.takeoff()
    await asyncio.sleep(30)
    # await drone.turn_clockwise(360)
    # await drone.flip_back()
    await drone.land()

run_tello_video_app(fly)