# Azz - Azure Devops CLI helper

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-green.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.14+](https://img.shields.io/badge/Python-3.14%2B-yellow.svg)](https://www.python.org/)
[![UV](https://img.shields.io/badge/uv-available-brightgreen.svg)](https://astral.sh/uv)
[![Justfile](https://img.shields.io/badge/just-available-brightgreen.svg)](https://just.systems/man/en/)
[![Docker](https://img.shields.io/badge/Docker-available-blue.svg)](https://www.docker.com/)

A simple CLI tool to help with Azure DevOps work item management,
built on top of the Azure CLI.

I only built this tool for myself,
but I thought it could be useful for others as well,
so I decided to make it public.
Feel free to clone it to adapt it to your needs.

## Installation

Requirements:

- [azure cli](https://learn.microsoft.com/en-us/cli/azure/get-started-with-azure-cli?view=azure-cli-latest)
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- An Azure DevOps organization and project
  - the tool is based on the Epic-Feature-Task work item hierarchy

Recommended:

- unix-like environment
  The tool was only tested on Linux
- [direnv](https://github.com/direnv/direnv)
  For loading environment variables from .envrc files.
  It permits you to have different configurations for different projects.

Installation:

```bash
# From pypi
uvx add azz # Not published yet, but will be available soon

# From source 
git clone
cd Azz

uv tool install . # classic install
just install # classic install using justfile
uv tool install --editable . # dev install
just install-dev # dev install using justfile
```

Then to verify the installation

```bash
azz --version
```

## Usage

In your project repository,
configure a `.envrc` file like `.envrc.example`.
