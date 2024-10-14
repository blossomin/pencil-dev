# Use the PyTorch base image with CUDA support
FROM nvidia/cuda:11.7.1-cudnn8-devel-ubuntu22.04

# Install git and other dependencies
RUN apt-get update && apt-get install -y \
    build-essential git vim python3 python3-dev python3-pip python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip \
    && pip3 install cmake numpy torch torchvision torchtext transformers
# Set the working directory
WORKDIR /home/dchen/projects/pencil-dev

# Copy the project files into the container
COPY . /home/dchen/projects/pencil-dev

# Change ownership of the directory
RUN chown -R $(id -u):$(id -g) /home/dchen/projects/pencil-dev

# Run the build_dependencies.sh script
# RUN bash scripts/build_dependencies.sh
RUN ln -s /usr/bin/python3 /usr/bin/python
# Set the entrypoint to bash
ENTRYPOINT ["bash"]

# --storage-opt size=20G
# docker run -it --rm --gpus all -v /home/dchen/projects/pencil-dev/:/home/dchen/projects/pencil-dev -w /home/dchen/projects/pencil-dev pencilcuda:v1