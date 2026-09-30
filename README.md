# GStreamer RTSP Video Streaming and Recording

## Overview

This project implements a video streaming and recording pipeline using **GStreamer** and **RTSP**.

The project supports:

- Streaming a video file through RTSP
- Streaming live webcam video through RTSP
- H.264 video encoding and decoding
- Receiving RTSP streams
- Displaying the received video
- Automatically recording the received RTSP stream into MP4
- Using MediaMTX as the RTSP server
- Python-based automation of the complete pipeline

---

## Technologies Used

- Python
- GStreamer 1.28.7
- RTSP
- MediaMTX
- H.264
- x264
- Docker
- Windows Media Foundation

---

## Project Architecture

### Video File Pipeline

```text
Video File
    |
    v
GStreamer
    |
    v
H.264 Processing
    |
    v
RTSP Publisher
    |
    v
MediaMTX
    |
    v
RTSP Receiver
    |
    +-------------> Video Display
    |
    +-------------> MP4 Recording
