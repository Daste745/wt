{
  python,
  pyproject-nix,
}:
let
  project = pyproject-nix.lib.project.loadPyproject {
    projectRoot = ./.;
  };
  pkgAttrs = project.renderers.buildPythonPackage { inherit python; };
in
python.pkgs.buildPythonApplication pkgAttrs
