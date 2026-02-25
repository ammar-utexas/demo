# Building PyTorch with CUDA on NVIDIA Jetson Thor (JetPack 7.0)

## System Information

| Property | Value |
|----------|-------|
| **Device** | NVIDIA Jetson AGX Thor |
| **JetPack** | 7.0-b128 |
| **L4T** | R38 (release), Revision 2.2 |
| **CUDA** | 13.0, V13.0.48 |
| **Python** | 3.12.3 |
| **GPU Architecture** | Blackwell (sm_100 / compute_100) |
| **Platform** | SBSA (Server Base System Architecture) aarch64 |

## Context

This guide documents the process of setting up the [finetuning_isic](https://github.com/sarupurisailalith/finetuning_isic) repository on a Jetson Thor for training an EfficientNet-B4 model on ISIC dermoscopic images. The Jetson Thor with JetPack 7.0 and CUDA 13.0 is bleeding-edge hardware — no pre-built PyTorch wheels exist for this configuration as of February 2025.

---

## Part 1: Repository Setup

### Step 1: Clone and activate virtual environment

```bash
cd ~/Projects/utexas
git clone git@github.com:sarupurisailalith/finetuning_isic.git
cd finetuning_isic
source .venv/bin/activate
```

### Step 2: Download ISIC data

**❌ Failed: `python download_data.py --limit 25000`**
- **Error:** `No module named isic` — the `isic-cli` package was not installed
- **Root cause:** Missing from `requirements.txt` in the repo

**❌ Failed: `pip install -r requirements.txt`**
- **Error:** `externally-managed-environment` — the venv was broken and using system Python
- **Root cause:** venv not created properly, missing `python3-venv` package

**✅ Fix: Recreate the venv**

```bash
sudo apt install python3-full python3-venv
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install isic-cli
```

**❌ Failed: `python download_data.py --limit 25000` (again)**
- **Error:** `No module named isic` — the script uses `subprocess` to call `.venv/bin/python3 -m isic` but `isic-cli` doesn't register as a `-m` runnable module
- **Root cause:** Bug in `download_data.py` — it shells out with `-m isic` instead of calling the `isic` CLI directly

**✅ Fix: Use the `isic` CLI directly**

```bash
mkdir -p data
isic image download --collections 65 --limit 25000 data
```

This successfully downloaded 25,000 images + metadata.

---

## Part 2: Installing PyTorch — The Journey

### Attempt 1: Pre-built wheels from NVIDIA index URLs

**❌ All failed — no wheels exist for JetPack 7.0 / CUDA 13.0:**

```bash
pip install torch torchvision --index-url https://developer.download.nvidia.com/compute/redist/jp/v70
pip install torch torchvision --index-url https://developer.download.nvidia.com/compute/redist/jp7/cu130
pip install torch torchvision --index-url https://developer.download.nvidia.com/compute/redist/jp6/cu126
pip install torch torchvision --index-url https://pypi.jetson-ai-lab.io/jp7/cu130
pip install torch torchvision --index-url https://pypi.jetson-ai-lab.io/jp6/cu126
```

- **Error:** `No matching distribution found for torch` on all indexes
- **Root cause:** JetPack 7.0 with CUDA 13.0 is too new — NVIDIA hasn't published wheels yet

### Attempt 2: System-level PyTorch check

```bash
deactivate
python3 -c "import torch; print(torch.__version__)"
```

- **Result:** `ModuleNotFoundError: No module named 'torch'`
- PyTorch is **not** pre-installed with JetPack 7.0

### Attempt 3: NVIDIA Docker container

```bash
sudo docker run -it --runtime nvidia --network host \
  -v ~/Projects/utexas/finetuning_isic:/workspace/finetuning_isic \
  nvcr.io/nvidia/pytorch:24.12-py3-igpu bash
```

- **Error:** `WARNING: Detected NVIDIA Thor GPU, which is not yet supported in this version of the container`
- **Error:** `No supported GPU(s) detected to run this container`
- **Root cause:** Container doesn't support Thor/Blackwell GPU yet

### Attempt 4: CPU-only PyTorch from PyPI

```bash
pip install torch --break-system-packages
```

- **Result:** Successfully installed `torch-2.10.0+cpu` (146 MB wheel for cp312 aarch64)

**❌ NumPy conflict:**
- **Error:** `RuntimeError: The current Numpy installation fails to pass simple sanity checks`
- **Root cause:** System NumPy (apt) conflicting with pip-installed torch

**✅ Fix:**

```bash
pip install --force-reinstall numpy --break-system-packages
```

**Verification:**

```bash
python3 -c "import torch; print(torch.__version__); print('CUDA:', torch.cuda.is_available())"
# Output: 2.10.0+cpu
# Output: CUDA: False
```

- **Conclusion:** Works but CPU-only. Training would take ~30+ min per epoch. Need to build from source for CUDA support.

---

## Part 3: Building PyTorch from Source (CUDA 13.0)

### Attempt 1: PyTorch v2.6.0

```bash
cd ~
sudo apt-get install -y cmake libopenblas-dev libopenmpi-dev libomp-dev
git clone --recursive --branch v2.6.0 https://github.com/pytorch/pytorch
cd pytorch
```

**Set environment variables:**

```bash
export USE_CUDA=1
export TORCH_CUDA_ARCH_LIST="10.0"
export USE_NCCL=0
export USE_DISTRIBUTED=0
export USE_QNNPACK=0
export USE_PYTORCH_QNNPACK=0
export MAX_JOBS=8
```

```bash
pip install -r requirements.txt --break-system-packages
python3 setup.py bdist_wheel
```

**❌ Failed: CMake protobuf compatibility**
- **Error:** `Compatibility with CMake < 3.5 has been removed from CMake`
- **Root cause:** System CMake is too new (4.2.1) for the bundled protobuf's `cmake_minimum_required`

**✅ Fix:**

```bash
export CMAKE_POLICY_VERSION_MINIMUM=3.5
```

**❌ Failed: CUB not found**
- **Error:** `Could NOT find CUB (missing: CUB_INCLUDE_DIR)`
- **Root cause:** CUB headers are at a non-standard path on Jetson Thor SBSA platform

**Investigation:**

```bash
find /usr -name "cub.cuh" 2>/dev/null
# Result: /usr/local/cuda-13.0/targets/sbsa-linux/include/cccl/cub/cub.cuh
```

**✅ Fix: Symlink CUB to expected location**

```bash
sudo ln -s /usr/local/cuda-13.0/targets/sbsa-linux/include/cccl/cub /usr/local/cuda/include/cub
```

**❌ Failed: XNNPACK compilation error**
- **Error:** `ninja: build stopped: subcommand failed` during XNNPACK Float16 compilation
- **Root cause:** XNNPACK has aarch64 compilation issues with the system GCC

**✅ Fix:**

```bash
export USE_XNNPACK=0
python3 setup.py clean
python3 setup.py bdist_wheel
```

**❌ Failed at [1535/2666]: cuFFT API incompatibility**
- **Error:** `'CUFFT_INCOMPLETE_PARAMETER_LIST' was not declared in this scope`
- **Error:** `'CUFFT_PARSE_ERROR' was not declared in this scope`
- **Error:** `'CUFFT_LICENSE_ERROR' was not declared in this scope`
- **Root cause:** CUDA 13.0 removed deprecated cuFFT error constants. PyTorch v2.6.0 does not support CUDA 13.0.

### Attempt 2: PyTorch `main` branch (has CUDA 13 fixes)

```bash
cd ~/pytorch
git fetch origin
git checkout main
git submodule sync
git submodule update --init --recursive
```

**❌ Failed: `python3 setup.py clean`**
- **Error:** `ModuleNotFoundError: No module named 'setuptools.command.bdist_wheel'`
- **Root cause:** `main` branch uses newer build tooling

**✅ Fix:**

```bash
pip install setuptools wheel --break-system-packages
pip install -r requirements.txt --break-system-packages
```

**❌ Failed: Stale build cache**
- **Error:** `ninja: error: rebuilding 'build.ninja'... missing and no known rule to make it`
- **Root cause:** Build artifacts from v2.6.0 conflicting with `main` branch

**✅ Fix:**

```bash
rm -rf build
python3 setup.py bdist_wheel
```

**Build started successfully — compiling [136/3200]...**

---

## Part 4: Complete Working Steps (Start to Finish)

If you need to restart the entire process from scratch, follow these steps:

### Prerequisites

```bash
sudo apt-get install -y python3-full python3-venv cmake libopenblas-dev libopenmpi-dev libomp-dev
```

### Step 1: Build PyTorch from source

```bash
cd ~
git clone --recursive https://github.com/pytorch/pytorch
cd pytorch

# Symlink CUB headers for CUDA 13 on SBSA
sudo ln -s /usr/local/cuda-13.0/targets/sbsa-linux/include/cccl/cub /usr/local/cuda/include/cub

# Set all required environment variables
export USE_CUDA=1
export TORCH_CUDA_ARCH_LIST="10.0"
export USE_NCCL=0
export USE_DISTRIBUTED=0
export USE_QNNPACK=0
export USE_PYTORCH_QNNPACK=0
export USE_XNNPACK=0
export MAX_JOBS=4
export CMAKE_POLICY_VERSION_MINIMUM=3.5

# Install build dependencies
pip install setuptools wheel --break-system-packages
pip install -r requirements.txt --break-system-packages

# Build (takes 2-3+ hours)
python3 setup.py bdist_wheel

# Install the built wheel
pip install dist/torch-*.whl --break-system-packages --force-reinstall
```

### Step 2: Verify PyTorch CUDA support

```bash
python3 -c "import torch; print(torch.__version__); print('CUDA:', torch.cuda.is_available())"
# Expected: CUDA: True
```

### Step 3: Build torchvision from source

```bash
cd ~
git clone --branch v0.21.0 https://github.com/pytorch/vision
cd vision
python3 setup.py bdist_wheel
pip install dist/torchvision-*.whl --break-system-packages
```

> **Note:** Match torchvision version to PyTorch version. If using PyTorch `main`, use torchvision `main` as well.

### Step 4: Set up the finetuning project

```bash
cd ~/Projects/utexas/finetuning_isic

# Recreate venv with system site packages (to use the built PyTorch)
rm -rf .venv
python3 -m venv --system-site-packages .venv
source .venv/bin/activate

# Install project dependencies
pip install -r requirements.txt
pip install isic-cli
```

### Step 5: Download ISIC data

```bash
# Use isic CLI directly (download_data.py has a bug with -m isic)
isic image download --collections 65 --limit 25000 data
```

### Step 6: Train

```bash
python3 train.py --epochs 15 --batch-size 64
```

---

## Fallback: CPU-Only Training

If the CUDA build is not ready and you need results immediately:

```bash
pip install torch torchvision --break-system-packages
pip install --force-reinstall numpy --break-system-packages

cd ~/Projects/utexas/finetuning_isic
python3 train.py --epochs 15 --batch-size 8
```

This will work but is significantly slower (~30+ min per epoch vs ~2 min with CUDA).

---

## Key Lessons Learned

1. **JetPack 7.0 + CUDA 13.0 is bleeding edge** — no pre-built PyTorch wheels from any source (NVIDIA, PyPI, Jetson AI Lab)
2. **NVIDIA Docker containers don't support Thor yet** — the `pytorch:24.12-py3-igpu` container explicitly rejects the Thor GPU
3. **PyTorch v2.6.0 does not support CUDA 13.0** — cuFFT API constants were removed in CUDA 13; only the `main` branch has fixes
4. **CUB headers on SBSA are at a non-standard path** — `/usr/local/cuda-13.0/targets/sbsa-linux/include/cccl/` instead of `/usr/local/cuda/include/`
5. **XNNPACK fails to compile on this platform** — must be disabled with `USE_XNNPACK=0`
6. **CMake 4.x breaks protobuf** — requires `CMAKE_POLICY_VERSION_MINIMUM=3.5`
7. **Always clean build artifacts when switching branches** — `rm -rf build` before rebuilding

---

## Part 5: Post-Build Steps

### Step 1: Install the PyTorch wheel

Once the `python3 setup.py bdist_wheel` completes successfully, the wheel will be in the `dist/` directory.

```bash
cd ~/pytorch
pip install dist/torch-*.whl --break-system-packages --force-reinstall
```

### Step 2: Verify PyTorch with CUDA

```bash
python3 -c "
import torch
print('PyTorch version:', torch.__version__)
print('CUDA available:', torch.cuda.is_available())
print('CUDA version:', torch.version.cuda)
print('cuDNN version:', torch.backends.cudnn.version())
a = torch.cuda.FloatTensor(2).zero_()
print('Tensor a =', a)
b = torch.randn(2).cuda()
print('Tensor b =', b)
c = a + b
print('Tensor c =', c)
"
```

**Expected output:**
- `CUDA available: True`
- Tensors should print with `device='cuda:0'`

If `CUDA available: False`, the build did not pick up CUDA correctly — re-check that `USE_CUDA=1` was set and that `/usr/local/cuda/bin/nvcc` exists.

### Step 3: Fix NumPy (if needed)

If you get NumPy sanity check errors when importing torch:

```bash
pip install --force-reinstall numpy --break-system-packages
```

### Step 4: Build and install torchvision from source

torchvision must be built from source to match the custom PyTorch build. Standard pip wheels won't be compatible.

```bash
cd ~
sudo apt-get install -y libjpeg-dev zlib1g-dev libpython3-dev libavcodec-dev libavformat-dev libswscale-dev

# Use main branch to match PyTorch main
git clone https://github.com/pytorch/vision torchvision
cd torchvision

# Build (takes ~15-20 minutes)
python3 setup.py bdist_wheel

# Install
pip install dist/torchvision-*.whl --break-system-packages
```

**Verify:**

```bash
python3 -c "import torchvision; print('torchvision version:', torchvision.__version__)"
```

### Step 5: Install additional training dependencies

The `train.py` script also requires `onnx` for model export and `pillow` for image processing:

```bash
pip install onnx pillow pandas scikit-learn --break-system-packages
```

### Step 6: Set up the finetuning project environment

```bash
cd ~/Projects/utexas/finetuning_isic

# Recreate venv with system site packages to inherit the built PyTorch/torchvision
rm -rf .venv
python3 -m venv --system-site-packages .venv
source .venv/bin/activate

# Install project-specific dependencies (isic-cli etc.)
pip install -r requirements.txt
pip install isic-cli
```

### Step 7: Download ISIC data (if not already done)

```bash
# Check if data already exists
ls data/ | wc -l

# If not downloaded yet, use isic CLI directly
isic image download --collections 65 --limit 25000 data
```

**Expected:** 25,000 images downloaded to `data/` directory (~8.5 GB).

### Step 8: Run training

```bash
# Jetson Thor with Blackwell GPU — use batch-size 64
python3 train.py --epochs 15 --batch-size 64
```

**Expected output files in `./output/`:**
- `efficientnet_b4_isic.onnx` — ONNX model for deployment
- `efficientnet_b4_isic.pth` — PyTorch checkpoint
- `training_log.csv` — per-epoch metrics

**Estimated training time:** ~2 min per epoch with 10k images at batch-size 64 (based on A100/4090 tier performance).

If you encounter GPU out-of-memory errors:

```bash
python3 train.py --epochs 15 --batch-size 32
```

### Step 9: Deploy to DermaCheck (optional)

After training, copy the ONNX model into the PMS project:

```bash
cp output/efficientnet_b4_isic.onnx <pms-ai>/models/efficientnet_b4_isic.onnx
cd <pms-ai>
docker compose restart pms-derm-cds
docker compose exec pms-derm-cds python scripts/populate_cache.py
```

---

## SSH Key Setup for GitHub (Reference)

These steps were completed during the session to push/pull from GitHub:

```bash
# Generate key
ssh-keygen -t ed25519 -C "ammar.darkazanli@austin.utexas.edu"

# Start agent and add key
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519_utexas

# Copy public key
cat ~/.ssh/id_ed25519_utexas.pub
```

Then add the public key at: **GitHub → Settings → SSH and GPG keys → New SSH key**

Verify with:

```bash
ssh -T git@github.com
```

---

## Quick Reference: All Environment Variables for PyTorch Build

```bash
# Copy-paste this block before starting the build
export USE_CUDA=1
export TORCH_CUDA_ARCH_LIST="10.0"
export USE_NCCL=0
export USE_DISTRIBUTED=0
export USE_QNNPACK=0
export USE_PYTORCH_QNNPACK=0
export USE_XNNPACK=0
export MAX_JOBS=4
export CMAKE_POLICY_VERSION_MINIMUM=3.5
export CUB_INCLUDE_DIR=/usr/local/cuda-13.0/targets/sbsa-linux/include/cccl
```

**Note:** If the CUB symlink was created (`sudo ln -s ... /usr/local/cuda/include/cub`), the `CUB_INCLUDE_DIR` export may not be needed, but it doesn't hurt to have both.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `No module named isic` | Use `isic` CLI directly instead of `python -m isic` |
| `externally-managed-environment` | Use `--break-system-packages` flag or recreate venv |
| `No matching distribution found for torch` | No pre-built wheels exist for JP 7.0; must build from source |
| NumPy sanity check failure | `pip install --force-reinstall numpy --break-system-packages` |
| `CMake < 3.5 compatibility removed` | `export CMAKE_POLICY_VERSION_MINIMUM=3.5` |
| `Cannot find CUB` | Symlink: `sudo ln -s /usr/local/cuda-13.0/targets/sbsa-linux/include/cccl/cub /usr/local/cuda/include/cub` |
| XNNPACK compilation failure | `export USE_XNNPACK=0` |
| cuFFT constants not declared | Use PyTorch `main` branch (not v2.6.0) |
| `ninja: build stopped` | Scroll up for actual error; reduce `MAX_JOBS` if OOM |
| `setuptools.command.bdist_wheel` missing | `pip install setuptools wheel --break-system-packages` |
| Stale build artifacts | `rm -rf build` before rebuilding |
| Docker container rejects Thor GPU | Container doesn't support Thor yet; build from source instead |

---

## Appendix A: Glossary

### Build Tools & Packaging

| Term | Definition |
|------|-----------|
| **bdist_wheel** | A Python setuptools command that builds a "wheel" (`.whl`) — a pre-compiled binary distribution package. Wheels are the standard format for distributing Python packages and are faster to install than source distributions because they skip the compilation step. |
| **CMake** | A cross-platform build system generator. It doesn't compile code directly but generates build files (like Makefiles or Ninja files) that other tools use to compile. PyTorch uses CMake to configure its C++/CUDA build. |
| **Ninja** | A small, fast build system designed for speed. It takes build instructions (generated by CMake) and executes compilation commands in parallel. The `[1535/2666]` progress indicators in the build output come from Ninja. |
| **pip** | Python's package installer. Used to install packages from PyPI (Python Package Index) or from local `.whl` files. The `--break-system-packages` flag overrides PEP 668 protections on externally managed Python environments. |
| **setuptools** | A Python library for building and distributing Python packages. `python3 setup.py bdist_wheel` uses setuptools to orchestrate the entire build process. |
| **wheel (.whl)** | A built Python package format (ZIP archive with a `.whl` extension). Contains compiled code ready to install, named like `torch-2.12.0-cp312-cp312-linux_aarch64.whl` (package-version-python-platform). |
| **venv** | Python's built-in virtual environment module. Creates isolated Python environments so project dependencies don't conflict with system packages. `--system-site-packages` allows the venv to access system-wide installed packages. |

### NVIDIA CUDA Ecosystem

| Term | Definition |
|------|-----------|
| **CUDA** | Compute Unified Device Architecture — NVIDIA's parallel computing platform and API. Allows software to use NVIDIA GPUs for general-purpose computation (not just graphics). CUDA 13.0 is the version on JetPack 7.0. |
| **nvcc** | The NVIDIA CUDA Compiler. Compiles `.cu` (CUDA) source files into GPU-executable code. Part of the CUDA Toolkit. |
| **cuDNN** | CUDA Deep Neural Network library — NVIDIA's GPU-accelerated library of primitives for deep neural networks. Provides optimized implementations of convolutions, pooling, normalization, and activation layers. |
| **cuFFT** | CUDA Fast Fourier Transform library — provides GPU-accelerated FFT implementations. PyTorch uses it for spectral operations. CUDA 13.0 removed some legacy error constants (`CUFFT_PARSE_ERROR`, `CUFFT_LICENSE_ERROR`, `CUFFT_INCOMPLETE_PARAMETER_LIST`), breaking older PyTorch versions. |
| **CUB** | CUDA UnBound — a library of cooperative threadblock primitives and utilities for CUDA kernel development. Provides reusable building blocks like parallel sort, scan, and reduction. On Jetson Thor SBSA, it's located at a non-standard path under CCCL. |
| **CCCL** | CUDA C++ Core Libraries — NVIDIA's umbrella project that includes CUB, Thrust, and libcu++. On Jetson Thor, CCCL headers are at `/usr/local/cuda-13.0/targets/sbsa-linux/include/cccl/`. |
| **cuSPARSELt** | A library for sparse matrix operations on NVIDIA GPUs. Required by some PyTorch builds for optimized sparse tensor operations. |
| **NCCL** | NVIDIA Collective Communications Library — provides multi-GPU and multi-node communication primitives (all-reduce, broadcast, etc.). Disabled in our build (`USE_NCCL=0`) since we're training on a single GPU. |
| **TensorRT** | NVIDIA's deep learning inference optimizer and runtime. Converts trained models into optimized engines for deployment. Separate from PyTorch but can be used to accelerate PyTorch model inference. |

### GPU Architecture

| Term | Definition |
|------|-----------|
| **Blackwell** | NVIDIA's GPU architecture used in the Jetson Thor. Identified by compute capability `sm_100` / `compute_100`. Successor to Ada Lovelace (sm_89) and Hopper (sm_90). |
| **sm_100 / compute_100** | The CUDA compute capability identifier for Blackwell GPUs. `sm` = Streaming Multiprocessor. Set via `TORCH_CUDA_ARCH_LIST="10.0"` when building PyTorch. |
| **SBSA** | Server Base System Architecture — an ARM specification for server-class systems. Jetson Thor uses SBSA (unlike older Jetsons which used Tegra/L4T paths), which is why CUDA headers are at `/targets/sbsa-linux/` instead of the usual locations. |
| **aarch64** | The 64-bit ARM processor architecture. All Jetson devices use ARM CPUs (as opposed to x86_64 used in desktop PCs). This is why standard PyTorch wheels from PyPI don't include CUDA support — they're built for x86_64 CUDA. |
| **VRAM** | Video RAM — the GPU's dedicated memory. Determines the maximum batch size for training. More VRAM allows larger batch sizes and faster training. |

### Jetson Platform

| Term | Definition |
|------|-----------|
| **JetPack** | NVIDIA's SDK for Jetson devices. Bundles the Linux OS (L4T), CUDA, cuDNN, TensorRT, and other libraries. JetPack 7.0 is the version for Jetson Thor. |
| **L4T** | Linux for Tegra — NVIDIA's custom Linux distribution for Jetson platforms. Version R38.2.2 on our system. Provides kernel, drivers, and board support packages. |
| **MAXN** | The highest power mode on Jetson devices. Enables all CPU and GPU cores at maximum clock speeds for peak performance. Visible in the top bar of the Jetson desktop. |
| **jetson_clocks** | A command-line utility that locks all CPU, GPU, and EMC (memory) clocks to their maximum frequencies. Used with MAXN mode for maximum training performance. |

### Neural Network Libraries & Tools

| Term | Definition |
|------|-----------|
| **XNNPACK** | A library of optimized floating-point neural network operators for ARM, x86, and WebAssembly. Used by PyTorch for CPU inference acceleration. Disabled in our build (`USE_XNNPACK=0`) due to compilation failures on this platform. |
| **QNNPACK** | Quantized Neural Network PACKage — a library for quantized (low-precision) neural network inference. Optimized for mobile ARM processors. Disabled in our build (`USE_QNNPACK=0`). |
| **FBGEMM** | Facebook GEneral Matrix Multiplication — a low-precision, high-performance matrix-matrix multiplication library. Used for quantized inference on x86. Not applicable to ARM/aarch64 builds. |
| **OpenMP** | Open Multi-Processing — an API for shared-memory parallel programming in C/C++. PyTorch uses it for CPU-side parallelism. The `-fopenmp` flags in the build enable this. |
| **protobuf** | Protocol Buffers — Google's language-neutral data serialization format. Used by PyTorch's Caffe2 backend for model serialization. The bundled version caused CMake compatibility issues. |
| **pybind11** | A C++ library that creates Python bindings for C++ code. PyTorch uses it to expose C++ functions to Python. |
| **Eigen** | A C++ template library for linear algebra (matrices, vectors). Used by PyTorch for CPU-side math operations. |

### ONNX & Model Export

| Term | Definition |
|------|-----------|
| **ONNX** | Open Neural Network Exchange — an open format for representing machine learning models. The finetuning_isic project exports trained models to ONNX format for deployment in the DermaCheck service. |
| **EfficientNet-B4** | A convolutional neural network architecture from Google. Part of the EfficientNet family, B4 is a medium-sized variant with 380x380 input resolution. Used in this project for skin lesion classification. |

### ISIC & Medical Imaging

| Term | Definition |
|------|-----------|
| **ISIC** | International Skin Imaging Collaboration — an organization that maintains a large public archive of dermoscopic images for skin cancer research. The ISIC Archive is the data source for this project. |
| **isic-cli** | A command-line tool for interacting with the ISIC Archive API. Used to download images and metadata. Installed via `pip install isic-cli`. |
| **dermoscopic** | Relating to dermoscopy — a technique for examining skin lesions using a specialized magnifying instrument (dermatoscope). Dermoscopic images show structures not visible to the naked eye. |

### Docker & Containers

| Term | Definition |
|------|-----------|
| **Docker** | A platform for running applications in isolated containers. NVIDIA provides pre-built Docker containers with PyTorch and CUDA for Jetson devices, though Thor support is not yet available. |
| **NGC** | NVIDIA GPU Cloud — NVIDIA's registry of GPU-optimized containers, models, and tools. Container images are pulled from `nvcr.io/nvidia/`. |
| **--runtime nvidia** | A Docker flag that enables GPU access inside the container using the NVIDIA Container Toolkit. Required for CUDA-accelerated workloads in Docker. |

### Git & Version Control

| Term | Definition |
|------|-----------|
| **submodule** | A Git feature for embedding one repository inside another. PyTorch has many submodules (protobuf, pybind11, XNNPACK, etc.) that must be cloned with `--recursive` or initialized with `git submodule update --init --recursive`. |
| **SSH key (ed25519)** | An authentication key pair using the Ed25519 elliptic curve algorithm. Used for secure passwordless authentication with GitHub. More secure and faster than RSA keys. |

### Python & System

| Term | Definition |
|------|-----------|
| **cp312** | CPython 3.12 — identifies the Python version in wheel filenames. Our system runs Python 3.12.3, so we need `cp312` wheels. |
| **manylinux** | A tag in Python wheel filenames indicating the wheel is compatible with many Linux distributions. `manylinux_2_28_aarch64` means it works on Linux systems with glibc 2.28+ on ARM64. |
| **PEP 668** | A Python Enhancement Proposal that marks system Python installations as "externally managed" to prevent pip from accidentally breaking OS packages. The `--break-system-packages` flag overrides this protection. |
| **MAX_JOBS** | An environment variable controlling how many parallel compilation processes run during the PyTorch build. Higher values (8) are faster but use more RAM. Lower values (4) are safer if running low on memory. |

---

*Document created: February 24, 2026*
*Session duration: ~3 hours of troubleshooting*
