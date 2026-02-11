FROM manimcommunity/manim:v0.19.0

USER root

RUN pip install --no-cache-dir --upgrade "pip" "setuptools<70.0.0" "wheel"

RUN pip install --no-cache-dir --no-build-isolation "openai-whisper==20230314"

RUN pip install --no-cache-dir "manim-voiceover[gtts,transcribe]"

USER manim
WORKDIR /manim
