import os
import time
from datetime import datetime

import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst


# ============================================================
# INITIALIZE GSTREAMER
# ============================================================

Gst.init(None)


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

RECORDINGS_DIR = os.path.join(
    BASE_DIR,
    "recordings"
)

os.makedirs(RECORDINGS_DIR, exist_ok=True)

RTSP_URL = "rtsp://127.0.0.1:8554/webcam"


# ============================================================
# RECORDING FILE
# ============================================================

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

OUTPUT_FILE = os.path.join(
    RECORDINGS_DIR,
    f"webcam_{timestamp}.mp4"
).replace("\\", "/")


# ============================================================
# DISPLAY INFORMATION
# ============================================================

print("========================================")
print("       GStreamer RTSP Webcam System")
print("========================================")
print(f"RTSP URL  : {RTSP_URL}")
print(f"Recording : {OUTPUT_FILE}")
print("========================================")


# ============================================================
# PUBLISHER
# ============================================================

publisher_pipeline = (
    "mfvideosrc "
    "! videoconvert "
    "! x264enc tune=zerolatency speed-preset=ultrafast "
    "! h264parse "
    f'! rtspclientsink protocols=tcp location="{RTSP_URL}"'
)

print("\nStarting webcam RTSP publisher...")

publisher = Gst.parse_launch(
    publisher_pipeline
)

publisher.set_state(
    Gst.State.PLAYING
)

print("Webcam publisher started.")

# Give MediaMTX time to make the stream available
time.sleep(2)


# ============================================================
# RECEIVER
# ============================================================

receiver_pipeline = (
    f'rtspsrc location="{RTSP_URL}" protocols=tcp latency=100 '
    "! rtph264depay "
    "! h264parse "
    "! tee name=t "

    # Webcam display
    "t. ! queue "
    "! avdec_h264 "
    "! videoconvert "
    "! autovideosink sync=false "

    # Recording
    "t. ! queue "
    "! mp4mux "
    f'! filesink location="{OUTPUT_FILE}"'
)

print("Starting RTSP receiver...")

receiver = Gst.parse_launch(
    receiver_pipeline
)

receiver.set_state(
    Gst.State.PLAYING
)

print("Receiver started.")
print("Webcam window should open.")
print("Recording started.")
print("\nPress Ctrl+C to stop.")


# ============================================================
# BUSES
# ============================================================

publisher_bus = publisher.get_bus()
receiver_bus = receiver.get_bus()


# ============================================================
# FINISH RECORDING
# ============================================================

def finish_recording():

    print("\nFinalizing recording...")

    # Send EOS to receiver so mp4mux
    # can properly finalize the MP4 file.
    receiver.send_event(
        Gst.Event.new_eos()
    )

    while True:

        message = receiver_bus.timed_pop_filtered(
            5 * Gst.SECOND,
            Gst.MessageType.EOS |
            Gst.MessageType.ERROR
        )

        if message is None:

            print(
                "Waiting for recording to finalize..."
            )

            continue

        if message.type == Gst.MessageType.EOS:

            print(
                "Recording finalized successfully."
            )

            break

        if message.type == Gst.MessageType.ERROR:

            error, debug = message.parse_error()

            print(
                "Receiver error while finalizing:"
            )

            print(error)

            if debug:
                print("Debug:")
                print(debug)

            break


# ============================================================
# MAIN LOOP
# ============================================================

try:

    while True:

        # Check publisher messages
        message = publisher_bus.timed_pop_filtered(
            100 * Gst.MSECOND,
            Gst.MessageType.ERROR
        )

        if message:

            if message.type == Gst.MessageType.ERROR:

                error, debug = message.parse_error()

                print("\nPublisher error:")
                print(error)

                if debug:
                    print("Debug:")
                    print(debug)

                break


        # Check receiver messages
        message = receiver_bus.timed_pop_filtered(
            100 * Gst.MSECOND,
            Gst.MessageType.ERROR
        )

        if message:

            if message.type == Gst.MessageType.ERROR:

                error, debug = message.parse_error()

                print("\nReceiver error:")
                print(error)

                if debug:
                    print("Debug:")
                    print(debug)

                break


except KeyboardInterrupt:

    print("\nStopping webcam RTSP system...")

    finish_recording()


# ============================================================
# STOP RECEIVER
# ============================================================

print("Stopping receiver...")

receiver.set_state(
    Gst.State.NULL
)


# ============================================================
# STOP PUBLISHER
# ============================================================

print("Stopping publisher...")

publisher.set_state(
    Gst.State.NULL
)


# ============================================================
# FINAL RESULT
# ============================================================

print("\n========================================")
print("RTSP webcam processing completed.")
print("Recording saved to:")
print(OUTPUT_FILE)
print("========================================")