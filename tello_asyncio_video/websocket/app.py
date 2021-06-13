import websockets
from ..video import decoded_frame_to_jpeg_data
from ..app import run_tello_video_app

DEFAULT_SERVER_PORT = 22222

def run_tello_video_app_websocket(fly, 
                                  process_frame=None, 
                                  on_frame_decoded=None, 
                                  drone=None, 
                                  wait_for_wifi=True,
                                  extra_tasks=None,
                                  server_port=DEFAULT_SERVER_PORT):

    clients = set()

    async def handle_websocket(websocket, request_path):
        try:
            clients.add(websocket)

            async for message in websocket:
                await handle_message(websocket, message)
        finally:
            clients.discard(websocket)

    async def handle_message(websocket, message):
        pass

    async def broadcast_frame(frame):
        try:
            # jpeg = decoded_frame_to_jpeg_data(frame)
            
            for c in clients:
                try:
                    await c.send(frame.data)
                except:
                    pass
        except Exception as e:
            print(f'[broadcast frame] ERROR {e}')

    if extra_tasks is None:
        extra_tasks = []

    async def run_server():
        server = await websockets.serve(handle_websocket, port=server_port)
        await server.wait_closed()

    extra_tasks.append(run_server())

    run_tello_video_app(fly, 
                        process_frame=process_frame, 
                        on_frame_decoded=broadcast_frame,
                        drone=drone,
                        wait_for_wifi=wait_for_wifi,
                        extra_tasks=extra_tasks)