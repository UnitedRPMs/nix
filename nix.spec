%undefine _hardened_build

%global nixbld_user "nix-builder-"
%global nixbld_group "nixbld"

#define _legacy_common_support 1
#global _lto_cflags %{nil}

Name: nix
Version: 2.3.10
Release: 1%{?dist}

Summary: A purely functional package manager

License: LGPLv2+
Group: Applications/System
Url: https://nixos.org/nix
Source: https://nixos.org/releases/nix/nix-%{version}/nix-%{version}.tar.xz

BuildRequires: gcc-c++ 
BuildRequires: autoconf 
BuildRequires: make 
BuildRequires: libtool
BuildRequires: openssl-devel
BuildRequires: bzip2-devel
BuildRequires: sqlite-devel
BuildRequires: libcurl-devel
BuildRequires: xz-devel
BuildRequires: brotli-devel
BuildRequires: libseccomp-devel
BuildRequires: gc-devel
BuildRequires: boost-devel
BuildRequires: libsodium-devel
BuildRequires: flex
BuildRequires: editline-devel >= 1.17.0
Requires: coreutils
Requires: shadow-utils

%description
Nix is a powerful package manager for Linux and other Unix systems that makes
package management reliable and reproducible. It provides atomic upgrades and 
rollbacks, side-by-side installation of multiple versions of a package, 
multi-user package management and easy setup of build environments.

%package        devel
Summary:        Development files for nix
Requires:       %{name} = %{version}-%{release}

%description   devel
The nix-devel package contains libraries and header files for
developing applications that use nix.

%prep
%autosetup -n %{name}-%{version} -p1

%build

%configure --prefix=/usr \
              --sysconfdir=/etc \
              --enable-gc--localstatedir=/nix/var

%make_build AM_DEFAULT_VERBOSITY=0

%install
%make_install

# make the store
mkdir -p %{buildroot}/nix/store
chmod 1775 %{buildroot}/nix/store

# make per-user directories
for d in profiles gcroots;
do
  mkdir -p %{buildroot}/nix/var/nix/$d/per-user
  chmod 1777 %{buildroot}/nix/var/nix/$d/per-user
done

# fix permission of nix profile
# (until this is fixed in the relevant Makefile)
chmod -x %{buildroot}/%{_sysconfdir}/profile.d/nix.sh

# Get rid of Upstart job.
rm -rf %{buildroot}/%{_sysconfdir}/init

%pre
getent group %{nixbld_group} >/dev/null || groupadd -r %{nixbld_group}
for i in $(seq 10);
do
  getent passwd %{nixbld_user}$i >/dev/null || \
    useradd -r -g %{nixbld_group} -G %{nixbld_group} -d /var/empty \
      -s %{_sbindir}/nologin \
      -c "Nix build user $i" %{nixbld_user}$i
done

%post
chgrp %{nixbld_group} /nix/store
# Enable and start Nix worker
systemctl enable nix-daemon.socket nix-daemon.service
systemctl start  nix-daemon.socket

%postun
chgrp %{nixbld_group} /nix/store
# Stop and disable Nix worker}
systemctl stop  nix-daemon.socket
systemctl disable nix-daemon.socket nix-daemon.service

%files
%license COPYING
%{_bindir}/nix
#{_sysconfdir}/init/nix-daemon.conf
%config(noreplace) %{_sysconfdir}/profile.d/nix.sh
%config(noreplace) %{_sysconfdir}/profile.d/nix-daemon.sh
%{_docdir}/nix/manual/
%{_mandir}/man*/
%{_datadir}/nix/
%{_prefix}/lib/systemd/system/nix-daemon.socket
%{_prefix}/lib/systemd/system/nix-daemon.service
%{_libdir}/libnixexpr.so
%{_libdir}/libnixmain.so
%{_libdir}/libnixstore.so
%{_libdir}/libnixutil.so
%{_bindir}/nix-build
%{_bindir}/nix-channel
%{_bindir}/nix-collect-garbage
%{_bindir}/nix-copy-closure
%{_bindir}/nix-daemon
%{_bindir}/nix-env
%{_bindir}/nix-hash
%{_bindir}/nix-instantiate
%{_bindir}/nix-prefetch-url
%{_bindir}/nix-shell
%{_bindir}/nix-store
%{_libexecdir}/nix/build-remote


%files devel
%{_includedir}/nix/
%{_prefix}/lib/pkgconfig/*.pc


%changelog

* Mon Feb 15 2021 David Va <davidva AT tuta DOT io> 2.3.10-1 
- Updated to 2.3.10

* Thu Sep 24 2020 David Va <davidva AT tuta DOT io> 2.3.7-1 
- Updated to 2.3.7

* Mon Jun 08 2020 David Va <davidva AT tuta DOT io> 2.3.6-1 
- Updated to 2.3.6

* Fri May 29 2020 David Va <davidva AT tuta DOT io> 2.3.5-1 
- Updated to 2.3.5

* Fri Apr 24 2020 David Va <davidva AT tuta DOT io> 2.3.4-1 
- Updated to 2.3.4

* Thu Mar 19 2020 David Va <davidva AT tuta DOT io> 2.3.3-1 
- Updated to 2.3.3

* Fri Jan 10 2020 David Va <davidva AT tuta DOT io> 2.3.2-1 
- Updated to 2.3.2

* Mon Oct 14 2019 David Va <davidva AT tuta DOT io> 2.3.1-1 
- Updated to 2.3.1

* Wed Sep 18 2019 David Va <davidva AT tuta DOT io> 2.3-1 
- Updated to 2.3

* Sun Jul 14 2019 David Va <davidva AT tuta DOT io> 2.2.2-1 
- Updated to 2.2.2

* Fri Oct 26 2018 David Va <davidva AT tuta DOT io> 2.1.3-3 
- Initial build
- Upstream

