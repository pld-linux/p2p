#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	smp		# don't build SMP module
%bcond_without	userspace	# don't build userspace module
%bcond_with	verbose		# verbose build (V=1)
#
%define		_orig_name	p2p
%define		_rel 1
%define		no_install_post_compress_modules	1
#
Summary:	P2P - a netfilter extension to identify P2P filesharing traffic
Summary(pl):	P2P - rozszerzenie filtra pakietów identyfikuj±ce ruch P2P
Name:		kernel-net-p2p
Version:	0.3.0a
Release:	%{_rel}@%{_kernel_ver_str}
License:	GPL
Group:		Base/Kernel
Source0:	http://mega.ist.utl.pt/~filipe/iptables-p2p/iptables-p2p-%{version}.tar.gz
# Source0-md5:	79832eb411003fb35f0c6a0985649c14
Patch0:		%{name}-Makefile.patch
URL:		http://mega.ist.utl.pt/~filipe/iptables-p2p/
%{?with_userspace:BuildRequires:	iptables-devel}
%if %{with kernel} && %{with dist_kernel}
BuildRequires:	kernel-module-build
%endif
%{?with_dist_kernel:%requires_releq_kernel_up}
Requires(post,postun):	/sbin/depmod
Buildroot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
iptables-p2p is a P2P match module for iptables. It supports the
detection of the following protocols: FastTrack (KaZaa, Grokster,
...), eDonkey (eDonkey, eMule, ...), Direct Connect, Gnutella
(regular clients and Shareaza's gnutella 2), BitTorrent, OpenFT
(giFT).

This package contains Linux kernel module.

%description -l pl
iptables-p2p to modu³ dopasowywania P2P dla iptables. Obs³uguje
wykrywanie nastêpuj±cych protoko³ów: FastTrack (KaZaa, Grokster...),
eDonkey (eDonkey, eMule...), Direct Connect, Gnutella (zwykli klienci
oraz gnutella 2 Shareazy), BitTorrent, OpenFT (giFT).

Ten pakiet zawiera modu³ j±dra Linuksa.

%package -n kernel-smp-net-p2p
Summary:	P2P - a netfilter extension to identify P2P filesharing traffic
Summary(pl):	P2P - rozszerzenie filtra pakietów identyfikuj±ce ruch P2P
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_smp}
Requires(post,postun):	/sbin/depmod

%description -n kernel-smp-net-p2p
iptables-p2p is a P2P match module for iptables. It supports the
detection of the following protocols: FastTrack (KaZaa, Grokster,
...), eDonkey (eDonkey, eMule, ...), Direct Connect, Gnutella
(regular clients and Shareaza's gnutella 2), BitTorrent, OpenFT
(giFT).

This package contains Linux SMP kernel module.

%description -n kernel-smp-net-p2p -l pl
iptables-p2p to modu³ dopasowywania P2P dla iptables. Obs³uguje
wykrywanie nastêpuj±cych protoko³ów: FastTrack (KaZaa, Grokster...),
eDonkey (eDonkey, eMule...), Direct Connect, Gnutella (zwykli klienci
oraz gnutella 2 Shareazy), BitTorrent, OpenFT (giFT).

Ten pakiet zawiera modu³ j±dra Linuksa SMP.

%package -n iptables-p2p
Summary:	P2P - a netfilter extension to identify P2P filesharing traffic
Summary(pl):	P2P - rozszerzenie filtra pakietów identyfikuj±ce ruch P2P
Release:	%{_rel}
Group:		Base/Kernel
Requires:	iptables

%description -n iptables-p2p
iptables-p2p is a P2P match module for iptables. It supports the
detection of the following protocols: FastTrack (KaZaa, Grokster,
...), eDonkey (eDonkey, eMule, ...), Direct Connect, Gnutella
(regular clients and Shareaza's gnutella 2), BitTorrent, OpenFT
(giFT).

%description -n iptables-p2p -l pl
iptables-p2p to modu³ dopasowywania P2P dla iptables. Obs³uguje
wykrywanie nastêpuj±cych protoko³ów: FastTrack (KaZaa, Grokster...),
eDonkey (eDonkey, eMule...), Direct Connect, Gnutella (zwykli klienci
oraz gnutella 2 Shareazy), BitTorrent, OpenFT (giFT).

%prep
%setup -q -n iptables-p2p-%{version}
%patch0 -p1

%build
%if %{with userspace}
# iptables module
cd iptables
cat << EOF > Makefile
CC		= %{__cc}
CFLAGS		= %{rpmcflags} -fPIC -DIPTABLES_VERSION=\\"1.2.9\\"
INCPATH		= -I../common
LD		= %{__ld}
.SUFFIXES:	.c .o .so
.c.o:
		\$(CC) \$(CFLAGS) \$(INCPATH) -c -o \$@ \$<
.o.so:
		\$(LD) -shared -o \$@ \$<
all:		libipt_%{_orig_name}.so
EOF
%{__make}
cd ..
%endif

%if %{with kernel}
# kernel module(s)
cd kernel
cp ../common/ipt_p2p.h .
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
    if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
	exit 1
    fi
    rm -rf include
    install -d include/{linux,config}
    %{__make} -C %{_kernelsrcdir} mrproper \
	SUBDIRS=$PWD \
	O=$PWD \
	%{?with_verbose:V=1}
    ln -sf %{_kernelsrcdir}/config-$cfg .config
    ln -sf %{_kernelsrcdir}/include/linux/autoconf-${cfg}.h include/linux/autoconf.h
    touch include/config/MARKER
    %{__make} -C %{_kernelsrcdir} modules \
	SUBDIRS=$PWD \
	O=$PWD \
	%{?with_verbose:V=1}
    mv ipt_%{_orig_name}.ko ipt_%{_orig_name}-$cfg.ko
done
cd ..
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
install -d $RPM_BUILD_ROOT%{_libdir}/iptables
install iptables/libipt_%{_orig_name}.so $RPM_BUILD_ROOT%{_libdir}/iptables
%endif

%if %{with kernel}
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/kernel/net/ipv4/netfilter
install kernel/ipt_%{_orig_name}-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/net/ipv4/netfilter/ipt_%{_orig_name}.ko
%if %{with smp} && %{with dist_kernel}
install kernel/ipt_%{_orig_name}-smp.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/kernel/net/ipv4/netfilter/ipt_%{_orig_name}.ko
%endif
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post
%depmod %{_kernel_ver}

%postun
%depmod %{_kernel_ver}

%post -n kernel-smp-net-p2p
%depmod %{_kernel_ver}

%postun -n kernel-smp-net-p2p
%depmod %{_kernel_ver}

%if %{with kernel}
%files
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/kernel/net/ipv4/netfilter/*

%if %{with smp} && %{with dist_kernel}
%files -n kernel-smp-net-p2p
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/kernel/net/ipv4/netfilter/*
%endif
%endif

%if %{with userspace}
%files -n iptables-p2p
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/iptables/*.so
%endif
