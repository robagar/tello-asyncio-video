import tornado.web
import tornado.ioloop
from io import BytesIO
from PIL import Image
from time import time


def run_server(frame_queue, port):

    t0 = time()

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

    class MJPEGStreamHandler(tornado.web.RequestHandler):
        BOUNDARY = '--jpgboundary'
        JPEG_QUALITY = 75

        def get(self):
            self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, pre-check=0, post-check=0, max-age=0')
            self.set_header('Pragma', 'no-cache')
            self.set_header('Content-Type', 'multipart/x-mixed-replace;boundary=' + self.BOUNDARY)
            self.set_header('Connection', 'close')

            while True:
                print(f'[mjpegstream] waiting for frame...')
                frame = frame_queue.get()
                print(f'[mjpegstream] got frame {frame.number}') 

                frame_t0 = time()
                content = self.frame_to_jpeg_data(frame)
                content_length = len(content)

                dt = time() - frame_t0
                print(f'[mjpegstream] frame {frame.number}: encoded jpeg after {dt:0.4f}s') 

                self.write('X-Timestamp: {0}\n'.format(time()))
                self.write('Content-type: image/jpeg\r\n')
                self.write(f'Content-length: {content_length}\r\n\r\n')
                self.write(content)
                self.write(self.BOUNDARY)
                self.write('\n')

                dt = time() - frame_t0
                print(f'[mjpegstream] frame {frame.number}: wrote output after {dt:0.4f}s') 
                
                self.flush()

                dt = time() - frame_t0
                print(f'[mjpegstream] frame {frame.number}: flushed after {dt:0.4f}s') 
                
                t = time()
                frame_time = t - t0
                dt = t - frame_t0
                fps = 1.0/dt
                print(f'[mjpegstream] FRAME {frame.number} at t={frame_time:0.4f} took {dt:0.4f}s ({fps:0.1f} fps)')


        def frame_to_jpeg_data(self, frame):
            image = Image.frombytes('RGB', (frame.width, frame.height), frame.data)
            buf = BytesIO()
            image.save(buf, 'jpeg', quality=self.JPEG_QUALITY)
            return buf.getvalue()                    

    # start http server
    handlers = [
        ('/', RootHandler), 
        ('/mjpegstream', MJPEGStreamHandler)
    ]
    tornado_app = tornado.web.Application(handlers)
    tornado_app.listen(port)
    ioloop = tornado.ioloop.IOLoop.current()
    ioloop.start()


