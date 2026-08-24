mod agent 'agent.just'

[group("user")]
@install:
    uv tool install .

[group("user")]
@run args:
    uv run azz {{ args }}

[group("dev")]
@precommit:
    uv run ruff check . --fix
    uv run ty check .

[group("dev")]
@install-dev:
    uv tool install --editable .

[group("dev")]
@checks:
    just agent::checks

[group("dev")]
@test:
    uv run pytest

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
