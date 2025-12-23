# Complete Tutorial: Compiling ngspice on Linux

## Table of Contents
1. [Introduction](#introduction)
2. [System Requirements](#system-requirements)
3. [Installing Dependencies](#installing-dependencies)
4. [Downloading ngspice Source](#downloading-ngspice-source)
5. [Configuration Options](#configuration-options)
6. [Compilation Process](#compilation-process)
7. [Installation](#installation)
8. [Post-Installation Setup](#post-installation-setup)
9. [Verification](#verification)
10. [Troubleshooting](#troubleshooting)
11. [Advanced Configuration](#advanced-configuration)

---

## Introduction

This tutorial guides you through compiling ngspice from source on Linux systems. Compiling from source gives you:

- **Latest features**: Access to newest capabilities
- **OSDI support**: Required for Verilog-A models
- **Optimization**: Tune for your specific system
- **Custom features**: Enable only what you need

**Time required:** 30-60 minutes
**Difficulty:** Intermediate
**Tested on:** Ubuntu 20.04, 22.04, 24.04, Debian 11/12

---

## System Requirements

### Minimum Requirements
- **OS**: Linux (Ubuntu, Debian, Fedora, etc.)
- **RAM**: 2 GB
- **Disk**: 500 MB free space
- **CPU**: Any modern processor

### Recommended
- **RAM**: 4 GB or more
- **Disk**: 1 GB free space
- **Multiple CPU cores** (faster compilation)

---

## Installing Dependencies

### Ubuntu/Debian Systems

#### Essential Build Tools

```bash
# Update package lists
sudo apt update

# Install basic build tools
sudo apt install -y build-essential
sudo apt install -y gcc g++ make
sudo apt install -y autoconf automake libtool
sudo apt install -y bison flex
sudo apt install -y git
```

#### Core Libraries

```bash
# Readline (command-line editing)
sudo apt install -y libreadline-dev

# X11 (graphical plotting)
sudo apt install -y libx11-dev
sudo apt install -y libxaw7-dev
sudo apt install -y libxmu-dev
sudo apt install -y libxext-dev
sudo apt install -y libxft-dev
sudo apt install -y libfontconfig1-dev
sudo apt install -y libxrender-dev

# Math libraries
sudo apt install -y libfftw3-dev

# NCurses (terminal interface)
sudo apt install -y libncurses-dev
```

#### Optional but Recommended

```bash
# For better documentation
sudo apt install -y texinfo

# For PDF documentation generation
sudo apt install -y texlive
sudo apt install -y texlive-latex-extra
sudo apt install -y texlive-fonts-recommended

# For advanced features
sudo apt install -y libedit-dev
```

#### OSDI Support Dependencies

```bash
# OSDI requires no special libraries!
# It uses dlopen from glibc (already installed)
# Just ensure you have a C compiler
```

### All-in-One Command for Ubuntu/Debian

```bash
sudo apt update && sudo apt install -y \
    build-essential \
    gcc g++ make \
    autoconf automake libtool \
    bison flex \
    git \
    libreadline-dev \
    libx11-dev libxaw7-dev libxmu-dev libxext-dev \
    libxft-dev libfontconfig1-dev libxrender-dev \
    libfftw3-dev \
    libncurses-dev \
    texinfo
```

### Fedora/RHEL/CentOS Systems

```bash
# Development tools
sudo dnf groupinstall "Development Tools"
sudo dnf install gcc gcc-c++ make autoconf automake libtool bison flex git

# Libraries
sudo dnf install readline-devel
sudo dnf install libX11-devel libXaw-devel libXmu-devel libXext-devel
sudo dnf install libXft-devel fontconfig-devel libXrender-devel
sudo dnf install fftw-devel
sudo dnf install ncurses-devel
sudo dnf install texinfo
```

### Arch Linux

```bash
sudo pacman -S base-devel
sudo pacman -S gcc make autoconf automake libtool bison flex git
sudo pacman -S readline libx11 libxaw libxmu libxext libxft fontconfig libxrender
sudo pacman -S fftw
sudo pacman -S ncurses
sudo pacman -S texinfo
```

---

## Downloading ngspice Source

### Method 1: Git Clone (Recommended for Latest)

```bash
# Create a work directory
mkdir -p ~/work
cd ~/work

# Clone the official ngspice repository
git clone https://git.code.sf.net/p/ngspice/ngspice ngspice

# Enter the source directory
cd ngspice

# Optional: Checkout a specific version
# git checkout ngspice-42
# git checkout ngspice-43

# Check current version
git describe --tags
```

### Method 2: Download Release Tarball

```bash
# Download specific version (example: version 43)
cd ~/work
wget https://sourceforge.net/projects/ngspice/files/ng-spice-rework/43/ngspice-43.tar.gz

# Extract
tar -xzf ngspice-43.tar.gz
cd ngspice-43
```

### Verify Download

```bash
# Check directory contents
ls -la

# Should see:
# - configure.ac or autogen.sh
# - src/ directory
# - examples/ directory
# - COPYING (license file)
```

---

## Configuration Options

### Understanding Configure

The `./configure` script prepares ngspice for compilation on your system. It:
- Detects installed libraries
- Sets compilation flags
- Enables/disables features

### Recommended Configuration

For most users including OSDI support:

```bash
./autogen.sh  # Generate configure script (if using git)

./configure \
    --with-x \
    --enable-xspice \
    --enable-cider \
    --enable-osdi \
    --enable-predictor \
    --with-readline=yes \
    --enable-openmp \
    --disable-debug
```

### Configuration Options Explained

#### Graphics and Interface

```bash
--with-x                  # Enable X11 graphics (plots)
--with-readline=yes       # Command-line editing (recommended)
--without-x              # Text-only version (smaller, faster)
```

#### Simulation Features

```bash
--enable-xspice          # Enable XSPICE extensions (code models)
--enable-cider           # Enable CIDER (semiconductor device sim)
--enable-osdi            # Enable OSDI (Verilog-A models) ★ IMPORTANT
--enable-predictor       # Better convergence for transient analysis
```

#### Performance

```bash
--enable-openmp          # Parallel processing (multi-core)
--disable-debug          # Optimize for speed (no debug symbols)
--enable-relpath         # Use relative paths (portable)
```

#### Installation Location

```bash
--prefix=/usr/local      # Default installation directory
--prefix=$HOME/ngspice   # Install to home directory (no sudo needed)
```

#### Advanced Options

```bash
--with-fftw3=yes         # Use FFTW3 for FFT (faster)
--enable-adms            # ADMS support (alternative Verilog-A)
--enable-klu             # KLU sparse matrix solver (better for large circuits)
--enable-ndev            # Enable ndev interface
```

### Example Configurations

#### Minimal Configuration (Small, Fast)

```bash
./configure \
    --without-x \
    --disable-xspice \
    --disable-cider \
    --with-readline=yes
```

#### Full-Featured Configuration

```bash
./configure \
    --with-x \
    --enable-xspice \
    --enable-cider \
    --enable-osdi \
    --enable-predictor \
    --with-readline=yes \
    --enable-openmp \
    --disable-debug \
    --with-fftw3=yes \
    --enable-klu
```

#### OSDI-Focused Configuration (What We Used)

```bash
./configure \
    --with-x \
    --enable-osdi \
    --enable-predictor \
    --with-readline=yes \
    --enable-openmp \
    --disable-debug
```

---

## Compilation Process

### Step-by-Step Compilation

#### 1. Generate Configure Script (Git Only)

If you cloned from git:

```bash
cd ~/work/ngspice
./autogen.sh
```

**Expected output:**
```
Running autoconf...
Running automake...
Configure script created successfully
```

#### 2. Run Configure

```bash
./configure \
    --with-x \
    --enable-osdi \
    --enable-predictor \
    --with-readline=yes \
    --enable-openmp \
    --disable-debug 2>&1 | tee configure.log
```

**What to check:**
- "checking for X... yes" (X11 found)
- "OSDI: yes" (OSDI enabled)
- "OpenMP: yes" (parallel support)
- No error messages

**Expected at end:**
```
config.status: creating config.h
config.status: executing depfiles commands
config.status: executing libtool commands

ngspice build configuration:

    Configured on host: ...

    Prefix:          /usr/local
    Debug:           no
    OpenMP:          yes
    OSDI:            yes
    ...
```

#### 3. Compile

Use multiple cores for faster compilation:

```bash
# Use all CPU cores
make -j$(nproc)

# Or specify number of cores (e.g., 4)
make -j4
```

**Time:** 5-15 minutes depending on CPU

**Expected output:**
```
Making all in src
...
make[2]: Entering directory '.../ngspice/src'
...
CC       file1.c
CC       file2.c
...
CCLD     ngspice
...
```

**Watch for:**
- Warnings are usually OK
- Errors will stop compilation
- "CCLD ngspice" at the end means success

#### 4. Verify Compilation

```bash
# Check if binary was created
ls -lh src/ngspice

# Expected:
# -rwxr-xr-x ... src/ngspice
```

#### 5. Optional: Run Tests

```bash
make check
```

This runs built-in tests to verify compilation quality.

---

## Installation

### Standard Installation (to /usr/local)

```bash
# Install (requires sudo)
sudo make install

# This installs:
# - /usr/local/bin/ngspice (executable)
# - /usr/local/lib/libngspice.so (shared library)
# - /usr/local/share/ngspice/ (scripts and data)
# - /usr/local/share/man/man1/ngspice.1 (manual page)
```

### User Installation (no sudo required)

```bash
# Configure with custom prefix
./configure --prefix=$HOME/ngspice --enable-osdi ...

# Compile
make -j$(nproc)

# Install to home directory
make install

# Add to PATH in ~/.bashrc
echo 'export PATH=$HOME/ngspice/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

### Verify Installation

```bash
# Check installation
which ngspice
# Expected: /usr/local/bin/ngspice

# Check version
ngspice --version
# Expected: ngspice compiled from ngspice revision ...

# Check library
ldd /usr/local/bin/ngspice | grep osdi
# Not expected to show libosdi (it's statically linked)

# Better check - verify OSDI in binary
strings /usr/local/bin/ngspice | grep -i osdi
# Should show OSDI-related strings
```

---

## Post-Installation Setup

### 1. Enable OSDI Support

Check if OSDI is disabled by default:

```bash
# Check spinit file
cat /usr/local/share/ngspice/scripts/spinit | grep osdi
```

If you see `unset osdi_enabled`, you need to enable it:

```bash
# Edit spinit file
sudo nano /usr/local/share/ngspice/scripts/spinit

# Find line with: unset osdi_enabled
# Comment it out: *unset osdi_enabled
```

**Or create user config:**

```bash
# Create user ngspice config
cat > ~/.spiceinit << 'EOF'
* User ngspice configuration
* Enable OSDI support
set osdi_enabled
EOF
```

### 2. Set Up Environment

Add to `~/.bashrc`:

```bash
# Add to ~/.bashrc
cat >> ~/.bashrc << 'EOF'

# ngspice configuration
export NGSPICE_HOME=/usr/local/share/ngspice

# Optional: Set default SPICE compatibility mode
# export SPICE_COMPAT_MODE=hspice
EOF

# Reload
source ~/.bashrc
```

### 3. Install Documentation (Optional)

```bash
# Build and install manual pages
cd ~/work/ngspice
sudo make install-man

# View manual
man ngspice
```

---

## Verification

### Test Basic Functionality

#### 1. Command-Line Test

```bash
# Start ngspice interactively
ngspice

# You should see:
# ******
# ** ngspice-XX ...
# ** Creation Date: ...
# ******
# ngspice 1 ->

# Try a command:
ngspice 1 -> version
ngspice 1 -> quit
```

#### 2. Test OSDI Support

Create test file: `test_osdi.cir`

```spice
* Quick OSDI test

.control
    echo "Testing OSDI support..."

    * Try loading a non-existent OSDI (should give proper error)
    pre_osdi test.osdi

    quit
.endc

.end
```

Run it:

```bash
ngspice -b test_osdi.cir
```

**Good output:**
```
Error on line X: model name is not found
```

**Bad output:**
```
Unknown command: pre_osdi
```

If you see "Unknown command", OSDI is not enabled!

#### 3. Test X11 Graphics

Create: `test_plot.cir`

```spice
* Test plotting

Vsrc n1 0 dc 0

.control
    dc Vsrc 0 10 0.1
    plot v(n1)
.endc

.end
```

Run interactively:

```bash
ngspice test_plot.cir
```

A plot window should appear!

#### 4. Test FFT (FFTW3)

```spice
* Test FFT

Vsrc n1 0 sin(0 1 1k)

.tran 0.01m 10m

.control
    run
    fft v(n1)
    quit
.endc

.end
```

```bash
ngspice -b test_fft.cir
```

Should complete without errors.

#### 5. Complete OSDI Test

If you have a working `.osdi` file:

```bash
# Use one of our working examples
cd ~/work/learning_ngspice/circuits/17_eletricidade_vlsi
ngspice -b test_res_final.cir
```

**Expected:**
```
v(p) = 1.000000e+00
i(v1) = -1.00000e-03
```

**Success!** ✓

---

## Troubleshooting

### Configuration Issues

#### Error: "X11 not found"

```
checking for X... no
configure: error: X11 not found
```

**Solution:**
```bash
sudo apt install libx11-dev libxaw7-dev libxmu-dev libxext-dev
./configure --with-x ...
```

**Or:** Build without X11:
```bash
./configure --without-x ...
```

#### Error: "readline not found"

```
checking for readline... no
```

**Solution:**
```bash
sudo apt install libreadline-dev
./configure --with-readline=yes ...
```

#### Warning: "FFTW3 not found"

**Solution:**
```bash
sudo apt install libfftw3-dev
./configure --with-fftw3=yes ...
```

**Or:** Ignore (ngspice has built-in FFT)

### Compilation Issues

#### Error: "make: command not found"

**Solution:**
```bash
sudo apt install build-essential
```

#### Error: Multiple definition of symbols

**Example:**
```
multiple definition of `something'
```

**Solution:** Clean and rebuild:
```bash
make clean
./configure [your options]
make -j$(nproc)
```

#### Error: Out of memory during compilation

**Solution:** Use fewer cores:
```bash
make -j2  # Instead of -j$(nproc)
```

### Runtime Issues

#### OSDI Commands Not Recognized

**Error:**
```
Unknown command: pre_osdi
```

**Solutions:**

1. Check if OSDI was enabled during configuration:
   ```bash
   grep OSDI ~/work/ngspice/config.log
   # Should show: enable_osdi=yes
   ```

2. Check spinit file:
   ```bash
   grep osdi /usr/local/share/ngspice/scripts/spinit
   ```

3. Recompile with `--enable-osdi`

#### OSDI Models Not Loading

**Error:**
```
model name is not found
```

**Solutions:**

1. Check OSDI is enabled:
   ```bash
   cat ~/.spiceinit
   # Should have: set osdi_enabled
   ```

2. Verify .osdi file exists:
   ```bash
   ls -lh *.osdi
   ```

3. Check circuit syntax (see Verilog-A tutorial)

#### Graphics Not Working

**Error:**
```
Warning: No graphics interface
```

**Solutions:**

1. Install X11 libraries and recompile with `--with-x`

2. Or use text output only:
   ```spice
   .control
       run
       print v(node)  # Instead of plot
   .endc
   ```

3. Export data and use external plotter:
   ```spice
   wrdata output.txt v(node)
   ```
   Then plot with gnuplot/Python

---

## Advanced Configuration

### Building with Debug Symbols

For development or debugging:

```bash
./configure \
    --enable-debug \
    --enable-osdi \
    --with-x \
    CFLAGS="-g -O0"

make -j$(nproc)
```

### Building Shared Library

To use ngspice as a library in your programs:

```bash
./configure \
    --with-ngshared \
    --enable-osdi \
    --prefix=/usr/local

make -j$(nproc)
sudo make install
```

Creates: `/usr/local/lib/libngspice.so`

### Cross-Compilation

For different architecture:

```bash
./configure \
    --host=arm-linux-gnueabihf \
    --enable-osdi \
    CC=arm-linux-gnueabihf-gcc

make -j$(nproc)
```

### Static Linking

For portable binary:

```bash
./configure \
    --enable-osdi \
    --without-x \
    LDFLAGS="-static"

make -j$(nproc)
```

Creates standalone executable (larger but no library dependencies).

### Optimization Flags

For maximum performance:

```bash
./configure \
    --enable-osdi \
    --enable-openmp \
    --disable-debug \
    CFLAGS="-O3 -march=native -mtune=native"

make -j$(nproc)
```

**Warning:** Binary won't work on different CPUs!

---

## Multiple Versions

### Installing Side-by-Side

Install different versions without conflicts:

```bash
# Version 1: Stable release
cd ~/work/ngspice-43
./configure --prefix=/opt/ngspice-43 --enable-osdi
make -j$(nproc)
sudo make install

# Version 2: Development version
cd ~/work/ngspice-git
./configure --prefix=/opt/ngspice-dev --enable-osdi
make -j$(nproc)
sudo make install

# Use specific version:
/opt/ngspice-43/bin/ngspice
/opt/ngspice-dev/bin/ngspice
```

### Switching Versions

```bash
# Add to ~/.bashrc
alias ngspice-stable='/opt/ngspice-43/bin/ngspice'
alias ngspice-dev='/opt/ngspice-dev/bin/ngspice'
alias ngspice='ngspice-stable'  # Default
```

---

## Uninstalling

### Remove Compiled ngspice

```bash
cd ~/work/ngspice
sudo make uninstall
```

### Clean Build Files

```bash
cd ~/work/ngspice
make clean           # Remove compiled objects
make distclean       # Remove everything including configure results
```

### Complete Removal

```bash
# Remove installation
sudo rm -rf /usr/local/bin/ngspice
sudo rm -rf /usr/local/lib/libngspice*
sudo rm -rf /usr/local/share/ngspice
sudo rm -rf /usr/local/share/man/man1/ngspice.1

# Remove source
rm -rf ~/work/ngspice
```

---

## Performance Tips

### 1. Use OpenMP

Enable parallel processing:

```bash
./configure --enable-openmp ...

# Set number of threads at runtime:
export OMP_NUM_THREADS=4
ngspice circuit.cir
```

### 2. Use KLU Solver

For large circuits:

```bash
./configure --enable-klu ...
```

Then in circuit:
```spice
.options klu
```

### 3. Optimize for Your CPU

```bash
CFLAGS="-O3 -march=native" ./configure ...
```

### 4. Use Shared Memory

For very large circuits:
```bash
./configure --with-x --enable-xspice --enable-shared-memory
```

---

## Summary: Quick Start Guide

### Complete Installation (Copy-Paste)

```bash
# 1. Install dependencies
sudo apt update && sudo apt install -y \
    build-essential gcc g++ make \
    autoconf automake libtool bison flex git \
    libreadline-dev libx11-dev libxaw7-dev libxmu-dev \
    libxext-dev libxft-dev libfontconfig1-dev libfftw3-dev \
    libncurses-dev texinfo

# 2. Download source
mkdir -p ~/work && cd ~/work
git clone https://git.code.sf.net/p/ngspice/ngspice ngspice
cd ngspice

# 3. Configure
./autogen.sh
./configure \
    --with-x \
    --enable-osdi \
    --enable-predictor \
    --with-readline=yes \
    --enable-openmp \
    --disable-debug

# 4. Compile
make -j$(nproc)

# 5. Install
sudo make install

# 6. Enable OSDI
echo "set osdi_enabled" > ~/.spiceinit

# 7. Verify
ngspice --version
echo ".control\n  echo 'OSDI test'\n  quit\n.endc\n.end" | ngspice -b
```

**Expected result:** ngspice runs without errors ✓

---

## Configuration Summary Table

| Feature | Configure Flag | Dependency | Recommended |
|---------|---------------|------------|-------------|
| X11 Graphics | `--with-x` | libx11-dev | Yes |
| OSDI | `--enable-osdi` | None | Yes (for Verilog-A) |
| Readline | `--with-readline=yes` | libreadline-dev | Yes |
| OpenMP | `--enable-openmp` | gcc with OpenMP | Yes |
| XSPICE | `--enable-xspice` | None | Optional |
| CIDER | `--enable-cider` | None | Optional |
| FFTW3 | `--with-fftw3=yes` | libfftw3-dev | Yes |
| Predictor | `--enable-predictor` | None | Yes |
| Debug | `--enable-debug` | None | No (slower) |

---

## Next Steps

After successful installation:

1. **Read the Verilog-A tutorial** (TUTORIAL_VERILOG_A.md)
2. **Try the examples** in `examples/` directory
3. **Create your first OSDI model**
4. **Read ngspice manual**: `man ngspice`
5. **Join the community**: ngspice mailing list

---

## Additional Resources

- **ngspice Homepage**: http://ngspice.sourceforge.net/
- **Source Repository**: https://sourceforge.net/p/ngspice/ngspice/
- **Manual**: http://ngspice.sourceforge.net/docs.html
- **Mailing List**: https://sourceforge.net/p/ngspice/mailman/
- **OpenVAF**: https://openvaf.semimod.de/

---

## Conclusion

You now have a complete guide to compiling ngspice with full OSDI support! The key points:

1. Install all dependencies first
2. Use `--enable-osdi` in configure
3. Enable OSDI in spinit or ~/.spiceinit
4. Verify installation with test circuits

Happy simulating!
