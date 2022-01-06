### Install dependency\(ies\)
- Create install destination
  ```bash
  mkdir -p "$HOME/.local"
  ```
- Download latest ncurses:
  ```bash
  wget "https://ftp.gnu.org/pub/gnu/ncurses/ncurses-6.1.tar.gz"
  ```
- Extract archive and enter folder
  ```bash
  tar zvxf ncurses-6.1.tar.gz
  cd ncurses-6.1
  ```
- Install:
  ```bash
  ./configure --prefix="$HOME/.local"
  make
  make install
  ```
### Install screen
- Set compilation flags:
  ```bash
  export LDFLAGS="-L$HOME/.local/lib"
  export CPPFLAGS="-I$HOME/.local/include"
  ```
- screen download and install:
  ```bash
  wget "https://ftp.gnu.org/gnu/screen/screen-4.8.0.tar.gz"
  tar xzvf screen-4.8.0.tar.gz
  mkdir $HOME/local/etc # for install below
  cd screen-4.8.0
  ./configure --prefix=$HOME/local
  # Note: if you got tgetent error use real path instead of $HOME
  make install
  install -m 644 ./etc/etcscreenrc "$HOME/.local/etc/screenrc"
  ```
- Point the shell to the right direction
  ```bash
  # Either by using alias
  alias sc="$HOME/.local/bin/screen"
  # Or add ~/.local/bin to PATH variable, not really preferred since it might cause undesireable discrepancies in scripts and such
  export PATH="$HOME/.local/bin:$PATH"
  ```

Related to: https://unix.stackexchange.com/questions/348184/can-not-find-screen-and-how-to-install-it-without-network-and-administration
Source: http://www.linuxfromscratch.org/blfs/view/svn/general/screen.html
