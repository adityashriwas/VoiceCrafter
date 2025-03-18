{pkgs}: {
  deps = [
    pkgs.libsndfile
    pkgs.xsimd
    pkgs.pkg-config
    pkgs.libxcrypt
    pkgs.ffmpeg
    pkgs.ffmpeg-full
    pkgs.postgresql
    pkgs.openssl
  ];
}
