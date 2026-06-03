# VoxPilot Demo Assets

This folder holds manual demo assets for VoxPilot.

Do not generate or commit synthetic demo media from the repository. Add real assets manually when they are ready.

Expected assets:

- `demo/audio/sample_generation.wav`: manually added sample output from a normal TTS generation.
- `demo/video/demo_walkthrough.mp4`: manually added short walkthrough video.
- `demo/screenshots/`: manually added screenshots of the Streamlit UI, run metadata, feedback flow, history, and metrics.

Suggested walkthrough:

1. Start the API and UI.
2. Generate speech from text.
3. Show run ID, engine, latency, cache status, and audio duration.
4. Repeat the same text to show cache behavior.
5. Submit generation feedback.
6. Show history and metrics.
