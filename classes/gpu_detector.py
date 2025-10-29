import subprocess

class GPUDetector:
    def __init__(self):
        self.nvidia_gpu_count = 0
        self.amd_gpu_count = 0
        self._detect_gpus()

    def _detect_gpus(self):
        # Detect NVIDIA GPUs
        try:
            # This assumes nvidia-smi is installed and in the system's PATH
            result = subprocess.run(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"], capture_output=True, text=True, check=True)
            output = result.stdout
            # Count lines in the output that likely represent a GPU (adjust as needed based on rocm-smi output format)
            self.nvidia_gpu_count = output.count('NVIDIA') # 'NVIDIA' is often found in NVIDIA GPU IDs
        except FileNotFoundError:
            self.nvidia_gpu_count = 0
        except subprocess.CalledProcessError:
            self.nvidia_gpu_count = 0

        # Detect AMD GPUs (using rocm-smi via subprocess)
        try:
            # This assumes rocm-smi is installed and in the system's PATH
            result = subprocess.run(['rocm-smi', '--showid'], capture_output=True, text=True, check=True)
            output = result.stdout
            # Count lines in the output that likely represent a GPU (adjust as needed based on rocm-smi output format)
            self.amd_gpu_count = output.count('gfx') # 'gfx' is often found in AMD GPU IDs
        except FileNotFoundError:
            self.amd_gpu_count = 0
        except subprocess.CalledProcessError:
            self.amd_gpu_count = 0

    def get_gpu_counts(self):
        return {
            "nvidia_gpus": self.nvidia_gpu_count,
            "amd_gpus": self.amd_gpu_count,
            "total_gpus": self.nvidia_gpu_count + self.amd_gpu_count
        }

# Example usage:
#if __name__ == "__main__":
#    detector = GPUDetector()
#    gpu_info = detector.get_gpu_counts()
