# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	userspace	# don't build userspace module
%bcond_with	verbose		# verbose build (V=1)

%if %{without kernel}
%undefine	with_dist_kernel
%endif
%if "%{_alt_kernel}" != "%{nil}"
%undefine	with_userspace
%endif
%if %{without userspace}
# nothing to be placed to debuginfo package
%define		_enable_debug_packages	0
%endif

%define		rel 10
%define		iptables_ver	1.3.3
%define		pname	p2p
Summary:	P2P - a netfilter extension to identify P2P filesharing traffic
Summary(pl.UTF-8):	P2P - rozszerzenie filtra pakietów identyfikujące ruch P2P
Name:		%{pname}%{_alt_kernel}
Version:	0.3.0a
Release:	%{rel}
License:	GPL
Group:		Base/Kernel
Source0:	http://dl.sourceforge.net/iptables-p2p/iptables-p2p-%{version}.tar.gz
# Source0-md5:	79832eb411003fb35f0c6a0985649c14
Patch0:		kernel-net-p2p-Makefile.patch
Patch1:		kernel-net-p2p-iptables.patch
URL:		http://sourceforge.net/projects/iptables-p2p/
%{?with_userspace:BuildRequires:	iptables-devel}
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build}
BuildRequires:	rpmbuild(macros) >= 1.330
%endif
Buildroot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
iptables-p2p is a P2P match module for iptables. It supports the
detection of the following protocols: FastTrack (KaZaa, Grokster,
...), eDonkey (eDonkey, eMule, ...), Direct Connect, Gnutella (regular
clients and Shareaza's gnutella 2), BitTorrent, OpenFT (giFT).

This package contains Linux kernel module.

%description -l pl.UTF-8
iptables-p2p to moduł dopasowywania P2P dla iptables. Obsługuje
wykrywanie następujących protokołów: FastTrack (KaZaa, Grokster...),
eDonkey (eDonkey, eMule...), Direct Connect, Gnutella (zwykli klienci
oraz gnutella 2 Shareazy), BitTorrent, OpenFT (giFT).

Ten pakiet zawiera moduł jądra Linuksa.

%package -n kernel%{_alt_kernel}-net-p2p
Summary:	P2P - a netfilter extension to identify P2P filesharing traffic
Summary(pl.UTF-8):	P2P - rozszerzenie filtra pakietów identyfikujące ruch P2P
Release:	%{rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_up}
Requires(post,postun):	/sbin/depmod

%description -n kernel%{_alt_kernel}-net-p2p
iptables-p2p is a P2P match module for iptables. It supports the
detection of the following protocols: FastTrack (KaZaa, Grokster,
...), eDonkey (eDonkey, eMule, ...), Direct Connect, Gnutella (regular
clients and Shareaza's gnutella 2), BitTorrent, OpenFT (giFT).

This package contains Linux kernel module.

%description -n kernel%{_alt_kernel}-net-p2p -l pl.UTF-8
iptables-p2p to moduł dopasowywania P2P dla iptables. Obsługuje
wykrywanie następujących protokołów: FastTrack (KaZaa, Grokster...),
eDonkey (eDonkey, eMule...), Direct Connect, Gnutella (zwykli klienci
oraz gnutella 2 Shareazy), BitTorrent, OpenFT (giFT).

Ten pakiet zawiera moduł jądra Linuksa.

%package -n iptables-p2p
Summary:	P2P - a netfilter extension to identify P2P filesharing traffic
Summary(pl.UTF-8):	P2P - rozszerzenie filtra pakietów identyfikujące ruch P2P
Release:	%{rel}
Group:		Base/Kernel
Requires:	iptables

%description -n iptables-p2p
iptables-p2p is a P2P match module for iptables. It supports the
detection of the following protocols: FastTrack (KaZaa, Grokster,
...), eDonkey (eDonkey, eMule, ...), Direct Connect, Gnutella (regular
clients and Shareaza's gnutella 2), BitTorrent, OpenFT (giFT).

%description -n iptables-p2p -l pl.UTF-8
iptables-p2p to moduł dopasowywania P2P dla iptables. Obsługuje
wykrywanie następujących protokołów: FastTrack (KaZaa, Grokster...),
eDonkey (eDonkey, eMule...), Direct Connect, Gnutella (zwykli klienci
oraz gnutella 2 Shareazy), BitTorrent, OpenFT (giFT).

%prep
%setup -q -n iptables-p2p-%{version}
%patch0 -p1
%patch1 -p1

%build
%if %{with userspace}
# iptables module
# IPTABLES_VERSION=`rpm -q --queryformat '%{V}' iptables`
IPTABLES_VERSION="%{iptables_ver}"
cat << 'EOF' > iptables/Makefile
CC		= %{__cc}
CFLAGS		= %{rpmcflags} -fPIC -DIPTABLES_VERSION=\"%{iptables_ver}\"
#"-vim
INCPATH		= -I../common
LD		= %{__ld}
.SUFFIXES:	.c .o .so
.c.o:
		$(CC) $(CFLAGS) $(INCPATH) -c -o $@ $<
.o.so:
		$(LD) -shared -o $@ $<
all:		libipt_p2p.so
EOF
%{__make} -C iptables
%endif

%if %{with kernel}
# kernel module(s)
cp common/ipt_p2p.h kernel
%build_kernel_modules -C kernel -m ipt_p2p
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
install -d $RPM_BUILD_ROOT%{_libdir}/iptables
install iptables/libipt_p2p.so $RPM_BUILD_ROOT%{_libdir}/iptables
%endif

%if %{with kernel}
%install_kernel_modules -m kernel/ipt_p2p -d kernel/net/ipv4/netfilter
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post -n kernel%{_alt_kernel}-net-p2p
%depmod %{_kernel_ver}

%postun -n kernel%{_alt_kernel}-net-p2p
%depmod %{_kernel_ver}

%if %{with kernel}
%files -n kernel%{_alt_kernel}-net-p2p
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/kernel/net/ipv4/netfilter/*
%endif

%if %{with userspace}
%files -n iptables-p2p
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/iptables/*.so
%endif
