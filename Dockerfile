FROM pytorch/pytorch:2.4.1-cuda12.1-cudnn9-runtime

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /workspace/humanoid_population_ppo

RUN apt-get update && apt-get install -y --no-install-recommends \
    git build-essential libgl1 libglfw3 libglfw3-dev libglew-dev libosmesa6-dev \
    patchelf ffmpeg tmux && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt pyproject.toml ./
COPY src ./src
COPY configs ./configs
COPY scripts ./scripts
COPY runpod ./runpod
COPY README.md ./README.md
RUN pip install --upgrade pip setuptools wheel && \
    pip install "gymnasium[mujoco]>=1.0.0" numpy PyYAML pandas tensorboard tqdm imageio imageio-ffmpeg && \
    pip install -e . --no-deps

CMD ["bash"]
