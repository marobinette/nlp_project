#!bin/bash

CC_ROOT=$(pwd)

# check if conda is installed
if ! command -v conda &> /dev/null
then
    echo "Conda could not be found"
    exit
fi

# check if cc environment exists
if [ -d "$HOME/miniforge3/envs/cc" ]
then
    echo "cc environment already exists"
    echo "Please remove the existing environment before running this script"
    echo "conda remove -n cc --all"
    exit
fi

# create a new conda environment
echo "Creating a new conda environment: cc"
conda create -n cc python=3.12 -y

echo "Activating the environment"

conda init
source ~/.bashrc
conda activate cc

if [ "$CONDA_DEFAULT_ENV" != "cc" ]
then
    echo "cc environment could not be activated"
    exit
fi

# post install setup
if [ ! -d "$CONDA_PREFIX/etc/conda/activate.d" ]; then
    mkdir -p "$CONDA_PREFIX/etc/conda/activate.d"
fi

if [ ! -d "$CONDA_PREFIX/etc/conda/deactivate.d" ]; then
    mkdir -p "$CONDA_PREFIX/etc/conda/deactivate.d"
fi

cat <<EOF > "$CONDA_PREFIX/etc/conda/activate.d/env_vars.sh"
export CC_ROOT=$CC_ROOT
EOF

cat <<EOF > "$CONDA_PREFIX/etc/conda/deactivate.d/env_vars.sh"
unset CC_ROOT
EOF

echo "Setup complete..."

pip install -e ./
conda install -c conda-forge nodejs -y


