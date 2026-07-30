# Python

As explained, we use:

- Astral/uv for python package management and virtual environments
  - always check the `pyproject.toml` for dependencies and scripts
  - never try to `pip install` or manage the environment manually.
  - as shown in the justfile, `uv run` is the recommended way to run python
    commands locally.
- Linting/Typecheck is done with Ruff/Ty
  - always `just checks` before committing — it runs `rumdl` and
    `precommit` in one command with a real exit code.
  - never invoke `ruff` or `ty` directly.

c.f. [`just -l`](../justfile) for more details on available commands.

## Code Practices

- We use type annotations everywhere, please make sure to add them to your code.
- Don't be lazy, never use single letter names, prefer descriptive names.
  - Also don't shorten names with abbreviations, for example `specification` is
    better than `spec`.
- We are in python 3.14
  - It means we can use all the latest features.
  - E.g. when possible in classmethods (not Enum), use `-> Self`
    instead of the class name in quotes.
  - prefer `tuple[TypeA, ...]` over `list[TypeA]`
    - They convey the immutability of the data.
    - `tuple[TypeA, TypeB, TypeC]` in function returns is often a poor way to
      concatenate multiple values, it makes signatures really hard to read.
      It is not a contradiction: tuple for immutable sequences good, tuple to
      concatenate values, often not good. Replace it with a dataclass, or at
      minimum a type alias plus a docstring.
  - when possible functions should accept immutable types (e.g. `Sequence`
    instead of `list`) and return immutable types (e.g. `tuple` instead of
    `list`)
- Avoid `Callable`, use a `Protocol` instead — it is more explicit and
  readable, and it names the contract.
- Please professional code, i.e.
  - short functions
    - I insist on this one. A function should be short, we should not have to
      scroll to read the whole function and understand it.
      The signature of the function should be
      enough to understand what the function does.
      You can use type annotations and aliases to make the signature more clear
      if needed.
  - short files
    - Try when possible to avoid multiple classes
      in the same file. Don't hesitate to create a
      module if you have multiple related classes
      to implement (see `plan/models/`, one class per file).
    - Be careful with the size of the files, if a file is too big,
      it's often a sign that it should be split into multiple files.
    - A file being too big is never an excuse for a new file to be too big.
  - single concern per function/file/class
    - the main thing I want you to adapt is the separation of concerns.
      You do not use OOP enough. Often I see you create a file with 900
      functions. Instead choose well defined abstractions to encapsulate
      algorithms. Force yourself to have clean contracts.
      Writing code is not supposed to be linear — it is coming up with
      abstractions that solve sub-problems in other files.
  - self explanatory code
    - comments only when strictly necessary.
      - and don't hardcode information in them: humans don't have the time to
        update comments, so keep them simple in the extremely rare case they
        are needed.
    - e.g. use variable names, function names and types to convey the meaning
      of comments that would otherwise need to be updated
    - Comments on top of files are **extremely** often a code smell.
      Comments belong on unclear functions, rarely on classes.
      Most of the time a file-header comment is a sign that there should be a
      class responsible for encapsulating the problem being solved.
    - Please don't write enormous comments on classes. You are not supposed to
      explain in what context a class is used. Think of code as isolated
      bricks — let the reader focus.
- Classes reminder
  - pydantic `BaseModel` for anything public facing
    - e.g. serialization/deserialization, and anything crossing a boundary
      (frontmatter, cached `az` payloads)
    - Don't use comments to explain the fields, use concise pydantic `Field`
      descriptions instead.
  - `dataclass` for internal use
    - or `pydantic.dataclasses.dataclass` when validation is needed
    - or when a dataclass becomes public facing
  - `StrEnum`/`IntEnum`/`Enum` for enums
  - Try to do OOP when possible to ensure good
    encapsulation and separation of concerns.
    We use a lot of `@classmethod` and `@property` to
    ensure good encapsulation.
    If you need a factory for a `tuple[TypeA, ...]`
    you can also use a `@classmethod` to return it, instead of
    a standalone function.

## When a docstring *is* required

The rules above push towards no comments. That is not the same as no
documentation.

Ask yourself: **can a random engineer understand the purpose of this function
from its signature alone?** For business logic the answer is often no — and
then a short docstring stating the input and the output is required.

Self-explanatory code is the goal; a signature that is impossible to decode is
not self-explanatory just because it has no comment.

## Remarks

Behaviors to avoid, with real examples.

### The self-explanatory code for Einstein

```python
def _resolve_state(
    fields: Mapping[str, Any],
) -> tuple[str, tuple[str, ...]] | None: ...
```

It is impossible to understand what this does from the signature, and barely
possible after reading the implementation. What is the `str`? What are the
other strings? What does `None` mean — not found, or no change?

This is a typical candidate for a docstring describing the typical
(input, output) pair, and sometimes a type alias is the real fix.

- `tuple[TypeA, ...]` is good for a sequence.
- `tuple[TypeA, TypeB, TypeC]` is often a code smell and should be replaced by
  a dataclass, or at least a type alias and a docstring.

### Weird function signature

```python
def _parse_tasks(
    directory: bytes,
) -> list[tuple[list[str], dict[str, Any], bool]]: ...
```

This is wrong on many levels. Either introduce more functions, or dataclasses,
or a named tuple. Nothing justifies this kind of signature — it is not
self-explanatory, not readable, not maintainable.

And what kind of function returns a `list` instead of a `tuple`? Even `bytes`
deserves a type alias when it means something specific.

### Cognitive Overload

Ultimately, the goal of the code is to be read by humans. These strict rules
are my attempt to give you a framework for writing code that is readable and
maintainable by **HUMANS**.

The most senior thing you can do is reduce the amount of required comments,
explanations, bloat, and code.

I insist on this one: be **concise**, don't be verbose, be surgical.
