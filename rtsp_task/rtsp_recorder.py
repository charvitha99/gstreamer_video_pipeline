import os
from datetime import datetime

import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst


# Initialize GStreamer
Gst.init(None)


# RTSP stream
RTSP_URL = "rtsp://127.0.0.1:8554/test"


# Recording folder
RECORDINGS_DIR = os.path.join(
    os.path.dirname(__file__),
    "recordings"
)

os.makedirs(RECORDINGS_DIR, exist_ok=True)


# Create unique filename
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

OUTPUT_FILE = os.path.join(
    RECORDINGS_DIR,
    f"recording_{timestamp}.mp4"
)


# GStreamer pipeline
pipeline_string = (
    f'rtspsrc location="{RTSP_URL}" protocols=tcp latency=100 '
    "! rtph264depay "
    "! h264parse "
    "! mp4mux "
    f'! filesink location="{OUTPUT_FILE}"'
)


print("Starting RTSP recorder...")
print(f"RTSP URL    : {RTSP_URL}")
print(f"Output file : {OUTPUT_FILE}")


# Create pipeline
pipeline = Gst.parse_launch(pipeline_string)


# Start pipeline
pipeline.set_state(Gst.State.PLAYING)

print("Recording started...")
print("Press Ctrl+C to stop recording.")


# Get GStreamer bus
bus = pipeline.get_bus()


try:
    while True:

        message = bus.timed_pop_filtered(
            Gst.CLOCK_TIME_NONE,
            Gst.MessageType.ERROR | Gst.MessageType.EOS
        )

        if message is None:
            continue

        if message.type == Gst.MessageType.ERROR:

            error, debug = message.parse_error()

            print("GStreamer Error:", error)

            if debug:
                print("Debug:", debug)

            break

        elif message.type == Gst.MessageType.EOS:

            print("End of stream.")
            break


except KeyboardInterrupt:

    print("\nStopping recording...")


# Stop pipeline
pipeline.set_state(Gst.State.NULL)


print("Recording stopped.")
print(f"Recording saved to: {OUTPUT_FILE}")
