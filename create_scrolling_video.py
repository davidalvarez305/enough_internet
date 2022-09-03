import subprocess
from wand.image import Image
from wand.drawing import Drawing
from wand.drawing import Color
from mutagen.mp3 import MP3

# Write text to an image with defined metrics


def create_image(text_path, img_output_path):
    image_width = 1920
    image_height = 1090
    left_margin = 150
    right_margin = image_width - left_margin * 2
    top_margin = 120
    line_padding = 35
    line_offset = 0

    text = ""
    with open(text_path, "r") as f:
        text = f.read()

    with Drawing() as ctx:
        with Image(width=image_width, height=image_height, background=Color("LIGHTCYAN")) as img:
            with Drawing() as draw:
                draw.font = "NotoSans-Bold.ttf"
                draw.font_size = 25
                for i, line in enumerate(text.split("\n")):
                    metrics = draw.get_font_metrics(img, line, multiline=True)
                    last_idx = 1
                    while metrics.text_width > right_margin:
                        last_breakpoint = 0
                        for idx in range(last_idx, len(line)):
                            if line[idx] == ' ':
                                last_breakpoint = idx
                            else:
                                metrics = draw.get_font_metrics(
                                    img, line[:idx], multiline=True)
                                if metrics.text_width >= right_margin:
                                    line = line[:last_breakpoint].strip(
                                    ) + '\n' + line[last_breakpoint:].strip()
                                    last_idx = last_breakpoint
                                    break
                        metrics = draw.get_font_metrics(
                            img, line, multiline=True)
                    draw.text(x=left_margin, y=top_margin +
                              line_offset, body=line)
                    line_offset += int(metrics.text_height) + line_padding
                draw(img)
                img.save(filename=img_output_path)


def create_scrolling_video(image_output_path, video_output_path, silent_video_output_path, audio_input_path, final_video_output_path, text_path):

    try:

        if len(text_path.split("\n")) > 12:
            # Create Silent Video W/ Scrolling
            subprocess.run(f"""
                    ffmpeg -f lavfi -i color=s=1920x1080:color=lightcyan -loop 1 -t 0.02 \
                    -i {image_output_path} -filter_complex \
                    "[1:v]scale=1920:-2,setpts=if(eq(N\,0)\,0\,1+1/0.02/TB),fps=25[fg]; \
                    [0:v][fg]overlay=y=-'t*h*0.005':eof_action=endall,setpts=if(eq(N\,0)\,0\,PTS+2/TB)[v]" -map "[v]" {video_output_path}
                """, shell=True, check=True, text=True)
        else:
            audio_length = MP3(audio_input_path).info.length
            # Create Video Without Scrolling
            subprocess.run(f"""
                    ffmpeg -t {audio_length} -i {image_output_path} {video_output_path}
                """, shell=True, check=True, text=True)

        # Add silent audio to video
        subprocess.run(f"""
                ffmpeg -i {video_output_path} -f lavfi -i anullsrc -c:v copy -c:a aac -shortest {silent_video_output_path}
            """, shell=True, check=True, text=True)

        # Put together video and TTS audio
        subprocess.run(
            f"""ffmpeg -i {silent_video_output_path} -i {audio_input_path} -c:v copy \
            -filter_complex "[0:a]aformat=fltp:44100:stereo,apad[0a];[1]aformat=fltp:44100:stereo,volume=0.75[1a];[0a][1a]amerge[a]" \
            -map 0:v -map "[a]" -ac 2 {final_video_output_path}""", shell=True,
            check=True, text=True)
    except BaseException as err:
        print(err)
