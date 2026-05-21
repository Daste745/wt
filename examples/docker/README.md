# Example Project Using Docker

This example uses a docker-compose.yaml stack to run the backend app, postgres and redis. All these services expose a port, which needs to be randomized in each worktree.

We're using the ability to merge compose files automatically from the `docker-compose.override.yaml` file.
We're also using the `!override` tag to remove original values from the `ports` section. This avoids keeping the original set of ports defined in the base `docker-compose.yaml` file.

Also, setting the top-level `name` attribute we get a new docker compose stack, even if the workspace directory has the same name as the original. For example, the main repository's directory is `/home/repos/some_project` and the worktree lives in `/home/trees/foo-bar/some_project/`. By setting `name: "some-project-foo-bar"`, we get a new docker compose stack named `some-project-foo-bar`.

See Docker docs: https://docs.docker.com/compose/how-tos/multiple-compose-files/merge/
