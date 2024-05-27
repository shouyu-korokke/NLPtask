import torch

# Check if CUDA (GPU support) is available
if torch.cuda.is_available():
    # Get the name of the GPU
    gpu_name = torch.cuda.get_device_name(0)  # Assuming you have one GPU
    print("CUDA is available. Using GPU:", gpu_name)
else:
    print("CUDA is not available. Using CPU.")
