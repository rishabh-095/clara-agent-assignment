import whisper

print("Loading Whisper model...")

model = whisper.load_model("base")

print("Transcribing audio...")

result = model.transcribe("audio1975518882.m4a")

with open("onboarding_transcript.txt", "w", encoding="utf-8") as f:
    f.write(result["text"])

print("Transcription completed!")
print(result["text"])