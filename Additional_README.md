# Installation

```
mamba create -n nf-core-custom python=3.10 pip git=2
# move into cloned repo and activate new environment
conda acitvate nf-core-custom
pip install ./
```

# Using nf-core modules

## Using new repo for the first time

```
# Use full URL when accessing a new repo for the first time
nf-core modules -g https://github.com/CSI-Dx/nextflow-resources -s csi list remote
```

## Using previously configured repo
```
# Only repo's name is needed
nf-core modules -g CSI-Dx/nextflow-resources -s csi list remote
```

## Addtional options
```
--git-remote    -g  TEXT  Remote git repo to fetch files from.
--branch        -b  TEXT  Branch of git repository hosting modules.
--subdirectory  -s  TEXT  Subdirectory within "modules/" directory that "nf-core modules" should use.
```
