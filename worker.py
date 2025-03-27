import requests
import os
import base64

def speech_to_text(audio_binary):
    headers = {
        "Authorization": f"Bearer {os.getenv('HF_API_TOKEN')}",
        "Content-Type": "application/json"
    }

    audio_b64 = base64.b64encode(audio_binary).decode("utf-8")
    data = { "inputs": audio_b64 }

    api_url = "https://api-inference.huggingface.co/models/openai/whisper-small"
    response = requests.post(api_url, headers=headers, json=data)
    result = response.json()

    try:
        text = result["text"]
    except Exception as e:
        print("❌ Whisper STT Error:", result)
        text = "Speech recognition failed."

    print("whisper response:", text)
    return text

def openai_process_message(user_message):
    headers = {
        "Authorization": f"Bearer {os.getenv('HF_API_TOKEN')}",
        "Content-Type": "application/json"
    }

    api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
    prompt = f"[INST] {user_message} [/INST]"
    data = { "inputs": prompt }

    response = requests.post(api_url, headers=headers, json=data)
    result = response.json()

    try:
        text = result[0]["generated_text"].split("[/INST]")[-1].strip()
    except Exception as e:
        print("❌ Mistral Error:", result)
        text = "I'm sorry, something went wrong."

    print("mistral response:", text)
    return text

def text_to_speech(text, voice=""):
    headers = {
        "Authorization": f"Bearer {os.getenv('HF_API_TOKEN')}",
        "Content-Type": "application/json"
    }

    data = { "inputs": text }

    api_url = "https://api-inference.huggingface.co/models/espnet/kan-bayashi_ljspeech_vits"
    response = requests.post(api_url, headers=headers, json=data)

    if response.status_code == 200 and response.headers.get("Content-Type", "").startswith("audio"):
        print("TTS response: success")
        return response.content
    else:
        print("❌ TTS Error:", response.text)
        return b""
