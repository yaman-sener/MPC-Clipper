# MPC Clipper

A fast and precise multi-clip extraction & concatenation tool for MPC-HC/MPC-BE using FFmpeg.

## Features & Fixes
- **Frame-Accurate Re-Encoding Engine**: Eliminates audio desync ("ses kayması") and video freezing ("donma / kayma") caused by keyframe (GOP) misalignment.
- **Audio Synchronization**: Standardizes audio to AAC 48kHz stereo with timestamp resynchronization (`aresample=async=1`).
- **Multi-Source Support**: Seamlessly combines clips taken from different video files with automatic aspect ratio scaling and padding.
- **Fast Copy Option**: Option to use direct stream copy (`-c copy`) for quick cutting when keyframe alignment is sufficient.
- **Speed Presets & Resolution Settings**: Support for `ultrafast`, `veryfast`, `medium` encoding speeds and custom/auto output resolutions (Auto, 1080p, 720p, 4K).
