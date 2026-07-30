mod agent 'agent.just'

@run args:
    uv run azz {{ args }}

@precommit:
    uv run ruff check . --fix
    uv run ty check .

@install:
    uv tool install .

@install-dev:
    uv tool install --editable .

[group("dev")]
@checks:
    just agent::checks

[group("dev")]
@version:
    just agent::version

[group("dev")]
@rumdl:
    rumdl check .

[group("dev")]
@rumdl-fmt:
    rumdl fmt .

[default]
@_list:
    just -l
