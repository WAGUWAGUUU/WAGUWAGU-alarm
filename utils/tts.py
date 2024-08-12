import os
import uuid
from gtts import gTTS

def generate_tts(text: str) -> str:
    # 음성 파일을 저장할 경로 설정
    directory = "audio_files"
    if not os.path.exists(directory):
        os.makedirs(directory)  # 디렉토리가 없으면 생성

    # 고유한 파일 이름 생성
    file_name = f"{uuid.uuid4()}.mp3"
    file_path = os.path.join(directory, file_name)

    try:
        # TTS 생성 및 저장
        tts = gTTS(text=text, lang='ko')
        tts.save(file_path)
        if not os.path.exists(file_path):
            raise RuntimeError(f"Failed to save TTS file at {file_path}")
        print(f"TTS file created at {file_path}")
        return file_path
    except Exception as e:
        # 예외 처리: TTS 생성 또는 파일 저장 중 에러가 발생할 경우
        print(f"Error generating TTS: {e}")
        return None