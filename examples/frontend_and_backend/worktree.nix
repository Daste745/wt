{
  projects.backend = {
    id = "backend";
    ports = [ "api" ];
    postInit = ''
      # TODO)) Generate random server ports for `ports`
      # TODO)) Update server port from `ports`->`api`
    '';
  };
  projects.frontend = {
    id = "frontend";
    requires = [ "backend" ];
    postInit = ''
      # TODO)) Pass port generated for backend (maybe `BACKEND_API_PORT`?)
      # TODO)) Set VITE_API_URL in .env to the backend URL
    '';
  };
}
