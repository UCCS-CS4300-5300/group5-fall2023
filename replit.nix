{ pkgs }: {
  deps = [
    pkgs.python39Packages.pylint
    pkgs.python39Packages.coverage
    pkgs.python38Full
  ];
  env = {
    PYTHONBIN = "${pkgs.python38Full}/bin/python3.8";
    LANG = "en_US.UTF-8";
  };
}