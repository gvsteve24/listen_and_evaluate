from enum import Enum
from pathlib import Path

import ffmpeg
from pydub import AudioSegment


class OutputFormat(Enum):
    PCM = 'pcm_s16le'
    AAC = 'aac'
    AAC_HE = 'aac_he'
    FLAC = 'flac'
    OGG = 'libvorbis'

    def get_ext(self):
        if self == OutputFormat.PCM:
            return 'wav'
        elif self == OutputFormat.AAC:
            return 'aac'
        elif self == OutputFormat.AAC_HE:
            return 'aac'
        elif self == OutputFormat.FLAC:
            return 'flac'
        elif self == OutputFormat.OGG:
            return 'ogg'
        return 'mp4'


class AudioEncoder:
    @staticmethod
    def encode(input_path: str, output_path: str = None, output_codec: OutputFormat = OutputFormat.PCM) -> str:
        if output_path is None:
            input_file = Path(input_path)
            output_path = f'{input_file.parent.absolute()}/{input_file.stem}_encoded.{output_codec.get_ext()}'
        try:
            (
                ffmpeg
                    .input(input_path)
                    .output(output_path, **{
                    'threads': '4',
                    'loglevel': 'panic',
                    'codec:a': output_codec.value,
                    'ac': '1',
                    'ar': '16000',
                })
                    .overwrite_output()
                    .run(capture_stdout=True, capture_stderr=True)
            )
        except ffmpeg.Error as e:
            if e.stdout:
                print('stdout:', e.stdout.decode('utf8'))
            if e.stderr:
                print('stderr:', e.stderr.decode('utf8'))
            raise e
        return output_path

    @staticmethod
    def validate_audio(path: str) -> bool:
        file_name = Path(path).stem
        try:
            audio_file = AudioSegment.from_file(file=path)
            if audio_file.duration_seconds > 60:
                print("File: ", file_name, "is too long. This process allows maximum 60 seconds duration.")
                return False
        except Exception as e:
            print("File: ", file_name, "has error: ", e)
        return True

    @staticmethod
    def cut_in_length(input_path: str, length: int, output_path: str = None, output_codec=OutputFormat.PCM) -> str:
        try:
            if output_path is None:
                input_file = Path(input_path)
                output_path = f'{input_file.parent.absolute()}/{input_file.stem}_trimmed.{output_codec.get_ext()}'
            (
                ffmpeg
                    .input(input_path)
                    .output(output_path, **{
                    'threads': '4',
                    'loglevel': 'panic',
                    'ss': '0',
                    'to': str(length),
                })
                    .overwrite_output()
                    .run(capture_stdout=True, capture_stderr=True)
            )
        except ffmpeg.Error as e:
            if e.stdout:
                print('stdout:', e.stdout.decode('utf8'))
            if e.stderr:
                print('stderr:', e.stderr.decode('utf8'))
            raise e
        return output_path


if __name__ == '__main__':
    # test filepath: /home/junghyun/Downloads/engineer_interview_questions.mp4
    if not AudioEncoder.validate_audio('/home/junghyun/Downloads/engineer_interview_questions.mp4'):
        temp_path = AudioEncoder.encode('/home/junghyun/Downloads/engineer_interview_questions.mp4')
        output_path = AudioEncoder.cut_in_length(temp_path, 60)
        print(output_path)
