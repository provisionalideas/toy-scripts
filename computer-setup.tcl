#!/bin/sh
# the next line restarts using tclsh \
exec tclsh "$0" "$@"

package require Expect

#Colour assignment
set blue "\033\[34m"
set clear "\033\[0m"
set bold "\033\[1m"
set green "\033\[32m"
set bkrd "\033\[1;36;40m"
set undr "\033\[4m"

stty -echo
spawn pwd
expect "(.*)\n";
set path1 [string trim $expect_out(buffer)]
stty echo

#Expect EOFs are here to force sequential behaviour and prevent a race condition.

#Clear screen before start
exec tput clear >@ stdout
puts "$bkrd\n\nNEW COMPUTER SETUP$clear"
puts "$blue\nThis program will install all necessary software to your computer."
puts "When prompted, please first install Xcode, then the Developer Tools.$clear"

#Request user's github username
send_user "$bold\nPlease enter your github username:  $clear"
expect_user -re "(.*)\n"
send_user "\n"
set username $expect_out(1,string)

send_user "$bold\nPlease enter your email address:  $clear"
expect_user -re "(.*)\n"
send_user "\n"
set email $expect_out(1,string)

#Request user password
stty -echo
send_user "$bold\nPlease enter your $undr*computer*$clear$bold password.$clear"
expect_user -re "(.*)\n"
send_user "\n"
stty echo
set password $expect_out(1,string)
exec tput clear >@ stdout

send_user "
What is your preferred text editor? (select number)
1. VSCode
2. Sublime Text
3. Emacs
4. Vim
5. Zed\n"
expect_user -re "(.*)\n"
set selection $expect_out(1,string)

if { $selection == 1 } {
  puts "VSCode will be installed."
}
if { $selection == 2} {
  puts "Sublime Text will be installed."
}
if { $selection == 3 } {
  puts "Emacs will be installed."
}
if { $selection == 4 } {
  puts "Vim will be installed."
}
if { $selection == 5 } {
  puts "Zed will be installed."
}

#run once to let user install Xcode
puts "$bold$blue\nClick Get Xcode!\n$clear"
spawn xcode-select --install
set timeout -1
puts "$bold$blue\nHit <enter> when installation is complete!\n$clear"
expect_user "\n"

#run once to let user install Xcode command line tools
puts "$bold$blue\nClick Install!\n$clear"
spawn xcode-select --install
set timeout -1
puts "$bold$blue\nHit <enter> when installation is complete!\n$clear"
expect_user "\n"

set timeout 5
spawn sudo xcodebuild -license
expect "assword:" { send "$password\r" }
expect {
  "Hit the Enter key to view the license agreements"
  {
    send "\r"
    exp_continue;
  }
  "By typing 'agree' you are agreeing" { send "agree\r\n" }
  "Software License Agreements Press 'space' for more, or 'q' to quit" {
    send " ";
    exp_continue;
  }
  timeout {
    send_user "\nTimeout\n"
    exit 1
  }
}

set timeout -1
puts "$bold$blue\nHit <enter> to proceed.$clear"
expect_user "\n"

#Install Homebrew
spawn bash
exp_send "/usr/bin/ruby -e \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)\"\n"
expect {
  "Press RETURN to continue or any other key to abort"
  {
    send "\r"
    exp_continue;
  }
  "assword:" { send "$password\r" }
}
expect {
  "bash"
  {
    close;
  }
}
#set up brew libraries
spawn brew install git ruby-build python gmp \
redis imagemagick mysql rbenv rbenv-bundler curl gnupg2 homebrew/versions/v8-315 p7zip
expect eof;
spawn brew link -force homebrew/versions/v8-315
expect eof;

#Fix socket problem
spawn brew unlink mysql
expect eof;
spawn brew install percona-server
expect eof;
spawn brew services start percona-server
expect eof;
spawn brew services start redis
expect eof;

#set up brew casks/apps
spawn brew cask install zoomus slack anaconda 1password iterm2 virtualbox google-chrome firefox \
viscosity Caskroom/cask/wkhtmltopdf
expect {
  "assword:" {
    send "$password\r"
    exp_continue;
  }
}
#expect eof;

if { $selection == 1 } {
  spawn brew install --cask visual-studio-code
}
if { $selection == 2} {
  spawn brew cask install sublime-text
}
if { $selection == 3 } {
  spawn brew install --with-cocoa --srgb emacs
  expect eof;
  spawn brew linkapps emacs;
}
if { $selection == 4 } {
  spawn brew install --cask macvim
  expect eof;
  spawn git clone https://github.com/VundleVim/Vundle.vim.git $path1/.vim/bundle/Vundle.vim
  expect eof;
  set fileID [open .vimrc w+]
  set str1 "set nocompatible              \" be iMproved, required
filetype off                  \" required

\" set the runtime path to include Vundle and initialize
set rtp+=~/.vim/bundle/Vundle.vim
call vundle#begin()
\" alternatively, pass a path where Vundle should install plugins
\"call vundle#begin('~/some/path/here')

\" let Vundle manage Vundle, required
Plugin 'VundleVim/Vundle.vim'
Plugin 'vim-syntastic/syntastic'

\" All of your Plugins must be added before the following line
call vundle#end()            \" required
filetype plugin indent on    \" required
\" To ignore plugin indent changes, instead use:
\"filetype plugin on
\"
\" Brief help
\" :PluginList       - lists configured plugins
\" :PluginInstall    - installs plugins; append `!` to update or just :PluginUpdate
\" :PluginSearch foo - searches for foo; append `!` to refresh local cache
\" :PluginClean      - confirms removal of unused plugins; append `!` to auto-approve removal
\"
\" see :h vundle for more details or wiki for FAQ
\" Put your non-Plugin stuff after this line"
puts $fileID $str1
close $fileID
spawn vim +PluginInstall +qall
}
if { $selection == 5 } {
  spawn brew install --cask zed
}
#set up rbenv
set path2 "/.rbenv"
set path $path1$path2
spawn git clone https://github.com/rbenv/rbenv.git $path
expect eof;
spawn cd $path && src/configure && make -C src
expect eof;

#Set .bash-profile
set fileID [open .bash_profile w+]
set str1 "PATH=\"$path1/.rbenv/shims:$path1/.rbenv/bin:\
/opt/local/bin:/opt/local/sbin:/usr/local/bin:/usr/local/sbin:/usr/bin:/bin:/usr/sbin:/sbin\"\n\
eval \"\$(rbenv init -)\""
puts $fileID $str1
close $fileID

#Set .zshrc path in case .zsh user
set fileID [open .zshrc w+]
set str1 "PATH=\"$path1/.rbenv/shims:$path1/.rbenv/bin:\
/opt/local/bin:/opt/local/sbin:/usr/local/bin:/usr/local/sbin:/usr/bin:/bin:/usr/sbin:/sbin\"\n\
eval \"\$(rbenv init -)\""
puts $fileID $str1
close $fileID

spawn type rbenv
expect "rbenv is a shell function";

spawn rbenv install 2.2.3
expect {
  "(y/N)"
  {
    send "y\r";
  }
}
expect eof;
spawn rbenv global 2.2.3
spawn sudo gem update --system
expect "assword:" { send "$password\r" }
expect eof;
spawn sudo gem install bundler foreman pg rails thin --no-rdoc --no-ri
expect "assword:" { send "$password\r" }
expect eof;
spawn rbenv rehash
expect eof;

#Install command line github integration
spawn sudo gem install ghi
expect "assword:" { send "$password\r" }

#Download Microsoft VMs
set path2 "/Documents/VMs/IE11.Win7.For.Windows.VirtualBox.zip"
set path $path1$path2
spawn curl https://az412801.vo.msecnd.net/vhd/VMBuild_20141027/VirtualBox/IE11/Windows/IE11.Win7.For.Windows.VirtualBox.zip --create-dirs -0 -o $path
set path2 "/Documents/VMs/MSEdge.Win10_RS1.VirtualBox.zip"
set path $path1$path2
spawn curl https://az792536.vo.msecnd.net/vms/VMBuild_20160802/VirtualBox/MSEdge/MSEdge.Win10_RS1.VirtualBox.zip -0 -o $path
expect eof;

#unpack VMs
spawn 7z x $path1/Documents/VMs/*.zip

#configure git
spawn git config --global user.name $username
expect eof;
spawn git config --global user.email $email

puts "$bold$blue\nInstallation complete!$clear"
