{
  lib,
  callPackage,
  python,
  uv2nix,
  pyproject-nix,
  pyproject-build-systems,
}:
let
  inherit (callPackage pyproject-nix.build.util { }) mkApplication;

  workspace = uv2nix.lib.workspace.loadWorkspace {
    workspaceRoot = ./.;
  };

  pyprojectOverlay = workspace.mkPyprojectOverlay {
    sourcePreference = "wheel";
  };

  baseSet = callPackage pyproject-nix.build.packages {
    inherit python;
  };
  overlays = [
    pyproject-build-systems.overlays.default
    pyprojectOverlay
  ];
  pythonSet = baseSet.overrideScope (lib.composeManyExtensions overlays);
in
mkApplication {
  venv = pythonSet.mkVirtualEnv "wt-env" workspace.deps.default;
  package = pythonSet.wt;
}
