# Security Model

This project executes model-generated code. Execution isolation is therefore part of the research method.

## Docker mode

The Docker sandbox requests:

- network disabled
- read-only root filesystem
- read-only code mount
- 512 MB default memory limit
- 64-process PID limit
- dropped Linux capabilities
- no-new-privileges
- bounded execution time
- writable /tmp only as a limited tmpfs

These controls reduce exposure but are not a proof of complete container security.

## Subprocess mode

Subprocess execution is explicitly a fallback with weaker isolation.

It uses:

- temporary working directory
- separate Python process
- timeout handling
- best-effort CPU and address-space resource limits on POSIX systems
- cleanup of temporary files

Subprocess mode does not disable network access and is not equivalent to Docker isolation.

## Research requirements

Every result records the execution mode so that experiments mixing Docker and subprocess execution are visible.

For security-sensitive benchmarks, prefer Docker mode and validate host/container policy independently.

## Secrets

API keys must be supplied through environment variables. No tracked configuration file should contain a real credential.
