{
  projects.backend = {
    id = "backend";
    ports = [ "api" ];
    postInit = ''
      set -euo pipefail

      sed -i "s/^PORT=.*\$/PORT=$BACKEND_API_PORT/" .env
    '';
  };
  projects.frontend = {
    id = "frontend";
    requires = [ "backend" ];
    postInit = ''
      set -euo pipefail

      sed -i "s/^VITE_API_URL=.*\$/VITE_API_URL=http:\/\/localhost:$BACKEND_API_PORT/" .env
    '';
  };
}
