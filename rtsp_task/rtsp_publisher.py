import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst


# Initialize GStreamer
Gst.init(None)


# RTSP destination
RTSP_URL = "rtsp://127.0.0.1:8554/test"


# GStreamer pipeline
pipeline_string = (
    "videotestsrc is-live=true "
    "! videoconvert "
    "! x264enc tune=zerolatency "
    "! h264parse "
    f'! rtspclientsink protocols=tcp location="{RTSP_URL}"'
)


print("Starting RTSP publisher...")
print(f"Publishing to: {RTSP_URL}")


# Create pipeline
pipeline = Gst.parse_launch(pipeline_string)


# Start pipeline
pipeline.set_state(Gst.State.PLAYING)

print("RTSP publisher is running...")


# Get message bus
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

    print("\nStopping RTSP publisher...")


# Stop pipeline
pipeline.set_state(Gst.State.NULL)

print("RTSP publisher stopped.")