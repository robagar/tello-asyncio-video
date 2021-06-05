import asyncio
import tornado.web
from io import BytesIO
from PIL import Image
from time import time

from tello_asyncio import Tello

from .video import H264DecoderAsync


DEFAULT_SERVER_PORT=22222


class RootHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('''<!doctype html>
<html lang=en>
  <head>
    <meta charset=utf-8>
    <title>Tello Async Video</title>
    <h1>Tello Async Video</h1>
    <img src="mjpegstream" />
  </head>
  <body>
    
  </body>
</html>
''')

def run_tello_video_app(fly, drone=None, on_frame_decoded=None, wait_for_wifi=True, server_port=DEFAULT_SERVER_PORT):
    if not drone:
        drone = Tello()


    async def main():
        if wait_for_wifi:
            await drone.wifi_wait_for_network()
    
        await drone.connect()

        # begin video stream
        await drone.start_video()
        t0 = time()

        decoder = H264DecoderAsync()

        async def watch_video():
            ''' 
            Receive and decode all frames from the drone. Decoding each frame
            often relies on previous frame data, so all frames must be decoded.
            '''
            print('[watch video] START')
            await decoder.decode_frames(drone.video_stream, on_frame_decoded)
            print('[watch video] END')

        class MJPEGStreamHandler(tornado.web.RequestHandler):
            BOUNDARY = '--jpgboundary'

            async def get(self):
                self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, pre-check=0, post-check=0, max-age=0')
                self.set_header('Pragma', 'no-cache')
                self.set_header('Content-Type', 'multipart/x-mixed-replace;boundary=' + self.BOUNDARY)
                self.set_header('Connection', 'close')

                while True:
                    frame = await decoder.decoded_frame
                    print(f'[mjpegstream] got frame {frame.number}...') 

                    frame_t0 = time()
                    content = self.frame_to_jpeg_data(frame)
                    content_length = len(content)

                    self.write(self.BOUNDARY)
                    self.write('Content-type: image/jpeg\r\n')
                    self.write(f'Content-length: {content_length}\r\n\r\n')
                    self.write(content)
                    await self.flush()
                    t = time()
                    frame_time = t - t0
                    dt = t - frame_t0
                    fps = 1.0/dt
                    print(f'[mjpegstream] FRAME {frame.number} at t={frame_time:0.4f} took {dt:0.4f}s ({fps:0.1f} fps)')
 

            def frame_to_jpeg_data(self, frame):
                image = Image.frombytes('RGB', (frame.width, frame.height), frame.data)
                buf = BytesIO()
                image.save(buf, 'jpeg')
                return buf.getvalue()                    

        # start http server
        handlers = [
            ('/', RootHandler), 
            ('/mjpegstream', MJPEGStreamHandler)
        ]
        tornado_app = tornado.web.Application(handlers)
        tornado_app.listen(server_port)

        try:
            # run all together until `fly` is complete
            finished, unfinished = await asyncio.wait(
                [fly(drone), watch_video()], 
                return_when=asyncio.FIRST_COMPLETED)

            # clean up
            for task in unfinished:
                task.cancel()
            await asyncio.wait(unfinished)
        except Exception as e:
            print(f'Exception caught: {e}')
        finally:
            await drone.stop_video()
            await drone.disconnect()

    # run asyncio event loop
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
