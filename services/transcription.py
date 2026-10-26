import os
import whisper

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")

_model = None

def load_model():
    global _model

    if _model is None:
        print(f"Loading Model...")
        _model = whisper.load_model(WHISPER_MODEL)
        print(f"whisper model loaded sucessfully ")

    return _model

load_model()

def transcribe_chunk(chunk_path: str,translate: bool = False) -> str:

    model = load_model()  
    task = "translate" if translate else "transcribe"
    result = model.transcribe(chunk_path, task=task,fp16=False)  
    return result["text"]



def transcribe_all(chunks:list ,translate :bool = False)->str:
    full_transcript= ""
    for i , chunk in  enumerate(chunks):
        print(f"transcribing chunk {i+1} ")
        text = transcribe_chunk(chunk , translate=translate)
        full_transcript += text + " "

    print("transcription completed")
    return full_transcript

