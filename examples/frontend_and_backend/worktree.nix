{
  id = "frontend-and-backend-example";
  projects.backend = {
    id = "backend";
    ports = [ "api" ];
    mainPort = "api";
    postInit = ''
      sed -i "s/^PORT=.*\$/PORT=$BACKEND_API_PORT/" .env
    '';
  };
  projects.frontend = {
    id = "frontend";
    requires = [ "backend" ];
    ports = [ "vite" ];
    mainPort = "vite";
    postInit = ''
      sed -i "s/^VITE_API_URL=.*\$/VITE_API_URL=http:\/\/localhost:$BACKEND_API_PORT/" .env
      echo "VITE_PORT=$FRONTEND_VITE_PORT" >> .env
    '';
  };
}
