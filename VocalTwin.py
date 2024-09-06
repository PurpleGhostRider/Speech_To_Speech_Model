import os
import wave
import torch
import whisper
import pyaudio
import threading
import tkinter as tk
from TTS.api import TTS
from tkinter import filedialog
from colorama import init, Fore, Style

def browse_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    return file_path

def is_audio_file(file_path):
    valid_extensions = ['.wav', '.mp3', '.ogg']
    _, ext = os.path.splitext(file_path)
    return ext.lower() in valid_extensions

def record_audio(output_file):
    chunk = 1024
    sample_format = pyaudio.paInt16
    channels = 1
    fs = 44100

    p = pyaudio.PyAudio()

    print("\n*Recording... Press Enter to stop.")

    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True)

    frames = []
    recording = True

    def stop_recording():
        nonlocal recording
        input()
        recording = False

    stop_thread = threading.Thread(target=stop_recording)
    stop_thread.start()

    while recording:
        data = stream.read(chunk)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(output_file, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()

def Transcribe_audio(audio_file):
    print("Transcribing in progress, please wait...")
    hasGpu = "cuda" if torch.cuda.is_available() else "cpu"
    model = whisper.load_model("medium").to(hasGpu)
    try:
        result = model.transcribe(audio_file)
        return result["text"]
    except Exception as e:
        print(f"{Fore.RED}Error running Whisper: {e}")

def clone_audio(To_be_cloned_audio_path, text_to_say, language):
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=True)
    tts.tts_to_file(text=text_to_say,
                    file_path="Clone.wav",
                    speaker_wav=[To_be_cloned_audio_path],
                    language=language,
                    split_sentences=True
                    )
    
def main():
    init(autoreset=True)
    
    # Step 1: get audio to clone
    while True:
        print("\n--> This audio is the voice you want to clone:")
        choice = input("*R to record or U to upload (R / U)? ").lower()
         
        # Record audio
        if choice == 'r':
            input("*Hit Enter to start recording: ").lower()
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            To_be_cloned_audio_path = os.path.join(desktop_path, "To_be_transcribed.wav")
            record_audio(To_be_cloned_audio_path)
            print(f"{Fore.GREEN}--- Recording temporarily saved as \"{To_be_cloned_audio_path}\" ---")
            break
        
        # Upload file
        elif choice == 'u':
            To_be_cloned_audio_path = browse_file()
            # Check if the provided path is a valid audio file
            while not is_audio_file(To_be_cloned_audio_path):
                print(f"*{Fore.RED}{Style.BRIGHT}The file is not an audio file.")
                To_be_cloned_audio_path = browse_file()
            print(f"{Fore.GREEN}---File Uploaded successfully---")
            break
        
        else:
            print("**Invalid choice.")


    # Step 2: Get audio to transcribe
    while True:
        print("\n--> This is the text you want the cloned voice to say:")
        choice = input("*W to write your own text or T to transcribe from audio file (T / W)? ").lower()
        
        # Write text
        if choice == 'w':
            print("\n--> This text is what you want the cloned voice to say:")
            text = input("Type here -> ")
            while not text:
                print(f"*{Fore.RED}{Style.BRIGHT}Empty string not allowed")
                text = input("Type here -> ")
            break
        
        # get audio file
        elif choice == 't':
            while True:
                print("\n--> This audio is the voice you want to transcribe:")
                choice = input("*R to record or U to upload (R / U)? ").lower()

                # Record audio
                if choice == 'r':
                    input("*Hit Enter to start recording: ").lower()
                    cloner_path = os.path.join(os.path.expanduser("~"), "Desktop")
                    To_be_Transc_audio_path = os.path.join(cloner_path, "To_be_transcribed.wav")
                    record_audio(To_be_Transc_audio_path)
                    print(f"{Fore.GREEN}--- Recording temporarily saved as \"{To_be_Transc_audio_path}\" ---")
                    break
                
                # Upload file
                elif choice == 'u':
                    To_be_Transc_audio_path = browse_file()
                    # Check if the provided path is a valid audio file
                    while not is_audio_file(To_be_Transc_audio_path):
                        print(f"*{Fore.RED}{Style.BRIGHT}The file is not an audio file.")
                        To_be_Transc_audio_path = browse_file()
                    print(f"{Fore.GREEN}---File uploaded successfully---")
                    break
                
                else:
                    print("**Invalid choice.")
            text = Transcribe_audio(To_be_Transc_audio_path)
            print(f"{Fore.GREEN}--- Audio has been transcribed successfully ---")
            break
        else:
            print("**Invalid choice.")
    
    # Enter the language in the refernce audio
    valid_codes = ['ar', 'en', 'fr', 'de', 'es', 'it',  'ru', 'pt', 'pl', 'tr', 'nl', 'cs', 'zh', 'ja']
    while True:
        print("Supported languages are 'ar', 'en', 'fr', 'de', 'es', 'it',  'ru', 'pt', 'pl', 'tr', 'nl', 'cs', 'zh', 'ja'")
        code = input("Enter a language code (e.g., en, fr, es): ").strip().lower()
        if code in valid_codes:
            print(f"{Fore.GREEN}--- Language set successfully ---")
            break
        else:
            print(f"{Fore.RED}{Style.BRIGHT}--- Language Not Supported ---")

    # clones the voice and outputs the file named Clone.wav
    clone_audio(To_be_cloned_audio_path, text, code)
    print(f"{Fore.GREEN}--- Audio has been cloned successfully ---")
    print(f"{Fore.GREEN}--- Note that the cloned voice will be saved in the directory you are working in ---\n")

if __name__ == "__main__":
    main()


# pyinstaller to make executable version
# let xtts allow more input chars
# increment file name if same file name exists(To avoid overriding old files)