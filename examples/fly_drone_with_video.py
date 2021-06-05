#!/usr/bin/env python3

from time import time
import asyncio

from tello_asyncio_video import run_tello_video_app


def on_frame_decoded(frame):
    pass
    # print(f'frame {frame.number} DECODED') 

async def fly(drone):
    t0 = time()
    await drone.takeoff()

    for i in range(10):
        r0 = time()
        b = await drone.query_battery()
        t = time() - t0
        print(f'[{i}] at t={t:0.4f}s battery: {b}%')
        dt = time() - r0
        await asyncio.sleep(1-dt)
    # await drone.turn_clockwise(360)
    # await drone.flip_back()
    await drone.land()

run_tello_video_app(fly, on_frame_decoded=on_frame_decoded)