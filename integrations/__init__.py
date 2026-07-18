"""Top-level namespace for DRIFT integrations that live outside the backend.

Packages here sit on the untrusted consumer side of the DRIFT API boundary.
They hold no credentials and add nothing to the backend runtime image or
deployment. Their SDKs are opt-in, optional dependency groups: ``uv.lock``
records them so ``--locked`` CI installs resolve, but ``uv sync --no-dev`` (the
Docker/Railway install) never installs them. See
``docs/adr/011-mcp-thin-client-layer.md``.
"""
