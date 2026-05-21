{
  projects = {
    backend = {
      id = "backend";
      ports = [ "api" ];
      postInit = ''
        sed -i "s/^PORT=.*\$/PORT=$BACKEND_API_PORT/" .env
      '';
    };
    frontend = {
      id = "frontend";
      requires = [ "backend" ];
      postInit = ''
        sed -i "s/^VITE_API_URL=.*\$/VITE_API_URL=http:\/\/localhost:$BACKEND_API_PORT/" .env
      '';
    };
  };
}
