{
  id = "docker-example";
  projects.backend = {
    id = "backend";
    ports = [
      "app"
      "postgres"
      "redis"
    ];
    mainPort = "app";
    postInit = ''
      sed "
        s/%STACK_NAME%/$WORKTREE_NAME/;
        s/%APP_PORT%/$BACKEND_APP_PORT/;
        s/%POSTGRES_PORT%/$BACKEND_POSTGRES_PORT/;
        s/%REDIS_PORT%/$BACKEND_REDIS_PORT/;
      " docker-compose.override.template.yaml > docker-compose.override.yaml
    '';
  };
}
