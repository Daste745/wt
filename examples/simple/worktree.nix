{
  projects.server = {
    id = "server";
    requires = [ ];
    ports = [
      "api"
      "foo"
      "bar"
    ];
    postInit = ''
      set -euo pipefail

      sed -i "s/^PORT=.*\$/PORT=$SERVER_API_PORT/" .env
      sed -i "s/^FOO=.*\$/FOO=$SERVER_FOO_PORT/" .env
      sed -i "s/^BAR=.*\$/BAR=$SERVER_BAR_PORT/" .env
    '';
  };
}
