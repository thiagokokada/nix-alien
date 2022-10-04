pkgs: final: prev:
{
  pylddwrap = prev.pylddwrap.overrideAttrs (oldAttrs: {
    propagatedBuildInputs = (oldAttrs.propagatedBuildInputs or [ ]) ++ [
      pkgs.glibc.bin
    ];
  });
  pyfzf = prev.pyfzf.overrideAttrs (oldAttrs: {
    propagatedBuildInputs = (oldAttrs.propagatedBuildInputs or [ ]) ++ [
      pkgs.fzf
    ];
  });
  mypy = prev.mypy.overrideAttrs (oldAttrs: {
    patches = [ ];
    MYPY_USE_MYPYC = false;
  });
  # Fix conflict between icontract and pylddwrap files
  icontract = prev.icontract.overrideAttrs (oldAttrs: {
    postInstall = (oldAttrs.postInstall or "") + ''
      rm -f $out/*.rst $out/*.txt
    '';
  });
}
