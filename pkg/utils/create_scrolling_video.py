import subprocess
from mutagen.mp3 import MP3
from wand.image import Image

def get_image_height(image_path):
    with Image(filename=image_path) as i:
        return i.height

def create_scrolling_video(image_output_path, video_output_path, silent_video_output_path, audio_input_path, final_video_output_path):
    audio_length = MP3(audio_input_path).info.length
    image_height = get_image_height(image_output_path) * 15
    scroll_rate = audio_length / image_height

    try:
        # Create Silent Video W/ Scrolling
        subprocess.run(f"""
                ffmpeg -y -f lavfi -i color=s=1920x1080:color=white -loop 1 -t {audio_length} \
                -i {image_output_path} -filter_complex \
                "[1:v]scale=1920:-2,setpts=if(eq(N\,0)\,0\,1+{audio_length}/TB),fps=25[fg]; \
                [0:v][fg]overlay=y=-'t*h*{scroll_rate}':eof_action=endall[v]" -map "[v]" {video_output_path}
            """, shell=True, check=True, text=True)

        # Add audio to silent video
        subprocess.run(f"""
                ffmpeg -y -i {video_output_path} -f lavfi -i anullsrc -c:v copy -c:a aac -shortest {silent_video_output_path}
            """, shell=True, check=True, text=True)

         # Put together video and TTS audio
        subprocess.run(f"""
            ffmpeg -i {silent_video_output_path} -i {audio_input_path} -c:v copy \
            -filter_complex "[0:a]aformat=fltp:44100:stereo,apad[0a];[1]aformat=fltp:44100:stereo,volume=0.75[1a];[0a][1a]amerge[a]" \
            -map 0:v -map "[a]" -ac 2 {final_video_output_path}
        """, shell=True, check=True, text=True)

    except BaseException as err:
        raise Exception(err)
