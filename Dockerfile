# Use the PyTorch base image with CUDA support
FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-devel

# Install git and other dependencies
RUN apt-get update && apt-get install -y \
    git vim \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /home/Pencil

# Copy the project files into the container
COPY . /home/Pencil

# Change ownership of the directory
RUN chown -R $(id -u):$(id -g) /home/Pencil

# Run the build_dependencies.sh script
# RUN bash scripts/build_dependencies.sh

# Set the entrypoint to bash
ENTRYPOINT ["bash"]

# docker run -it --rm --gpus all -v /home/dchen/projects/Pencil/:/home/Pencil -w /home/Pencil pencil:cudav117