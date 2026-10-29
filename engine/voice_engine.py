import os
import requests
import config as cfg

def generate_elevenlabs_voiceover(text_prompt, output_filename="ai_narration.mp3"):
    """
    Connects to the ElevenLabs Text-to-Speech API to generate high-fidelity
    voiceovers for cinematic short-form narrations and video briefs.
    """
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    # Pulls from config or falls back to standard cloned voice ID
    voice_id = getattr(cfg, "ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM") 
    
    if not api_key:
        print(f"\n     {cfg.THEMES['NINJA_ORANGE']['MAIN']}[!] ELEVENLABS_API_KEY environment variable not configured.{cfg.THEMES['NINJA_ORANGE']['RESET']}")
        return None

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    
    # Optimized stability and similarity parameters for short-form video narrations
    payload = {
        "text": text_prompt,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.45,
            "similarity_boost": 0.80,
            "style": 0.20,
            "use_speaker_boost": True
        }
    }
    
    print(f"\n     {cfg.THEMES['NINJA_ORANGE']['ACCENT']}-> Initializing ElevenLabs Voice Synthesis Engine...{cfg.THEMES['NINJA_ORANGE']['RESET']}")
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            os.makedirs(cfg.AUDIO_FOLDER, exist_ok=True)
            out_path = os.path.join(cfg.AUDIO_FOLDER, output_filename)
            with open(out_path, "wb") as f:
                f.write(response.content)
            print(f"     {cfg.THEMES['NINJA_ORANGE']['MAIN']}[+] Voiceover successfully rendered and cached at: {out_path}{cfg.THEMES['NINJA_ORANGE']['RESET']}")
            return out_path
        else:
            print(f"     [!] ElevenLabs API Error ({response.status_code}): {response.text}")
            return None
    except Exception as e:
        print(f"     [!] Connection Error during voice synthesis: {e}")
        return None

if __name__ == "__main__":
    sample_text = "Step into the void. This is the Cinegrade master workflow."
    generate_elevenlabs_voiceover(sample_text, "test_voiceover.mp3")