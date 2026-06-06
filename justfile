@run args:
    uv run azz {{ args }}

@precommit:
    uv run ruff check . --fix
    uv run ty check .

@install:
    uv tool install .

@install-dev:
    uv tool install --editable .

[default]
@_list:
    just -l
