# wt

Worktree manager and localhost proxy for managing git worktrees.

Worktrees are registered in a central database with their generated port numbers, names, paths and dependencies.

## Worktree Configuration

See [Examples](./examples) for example worktree configurations:

- [Simple](./examples/simple) - single-project worktree with generated ports
- [Docker](./examples/docker) - docker-compose setup with generated ports and templated `docker-compose.override.yaml` file
- [Frontend and Backend](./examples/frontend_and_backend) - frontend project dependent on backend's generated API port

## Localhost Proxy

You can use `wt proxy config` to generate a Caddyfile with all registered worktrees as proxy hosts.
This creates hosts with friendly names like `worktree-name.backend.some-project.localhost`, which points to `localhost:<generated port number>`.

```sh
wt proxy config > Caddyfile
# Proxy hosts are bound to port `80`, so we need to run as root
sudo caddyfile run
```

I have a plan on making proxy config generation automatic on any change in the worktree database, but for now it needs to be generated and ran manually.
