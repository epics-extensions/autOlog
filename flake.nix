{
  description = "A basic flake using pyproject.toml project metadata";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";
  inputs.pyproject-nix.url = "github:pyproject-nix/pyproject.nix";
  inputs.pyproject-nix.inputs.nixpkgs.follows = "nixpkgs";
  inputs.epnix.url = "github:epics-extensions/EPNix/nixos-25.11";

  outputs = {
    nixpkgs,
    pyproject-nix,
    epnix,
    self,
    ...
  }: let
    project = pyproject-nix.lib.project.loadPyproject {
      projectRoot = ./.;
    };
    pkgs = import nixpkgs {
      system = "x86_64-linux";
      overlays = [epnix.overlays.default];
    };
    python = pkgs.python3;
    autolog = self.packages.x86_64-linux.default;
  in {
    devShells.x86_64-linux.default = let
      arg = project.renderers.withPackages {inherit python;};
      epics-base = pkgs.epnix.epics-base;
      pythonEnv = python.withPackages arg;
    in
      pkgs.mkShell {
        packages = [pythonEnv epics-base autolog];
        env.PYEPICS_LIBCA = "${epics-base}/lib/linux-x86_64/libca.so";
      };

    packages.x86_64-linux.default = let
      attrs = project.renderers.buildPythonPackage {inherit python;};
    in
      python.pkgs.buildPythonPackage (attrs
        // {
          nativeCheckInputs =
            (attrs.nativeCheckInputs or [])
            ++ [
              python.pkgs.pytestCheckHook
            ];

          doCheck = true;
          disabledTests = [
            # Tests using caproto which is not packaged in nix
            "cac"
            "utils"
            "log_content"
          ];
        });

  };
}
