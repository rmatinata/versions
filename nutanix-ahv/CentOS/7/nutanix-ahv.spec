Name: nutanix-ahv
Version: 6.0
Release: 1%{dist}%{?buildid}
Summary: Nutanix Acropolis Hypervisor metapacakges
Group: System Environment/Base
License: Nutanix EULA
BuildArch: noarch

%description
%{summary}

%package release

Summary: Nutanix AHV Release

Source1001: libvirt-qemu-hook
Source1002: sysctl.conf

# Direct dependencies of files in this package.
Requires: /usr/bin/cgclassify

# Base OpenPower Host OS with virtualization support.
Requires: open-power-host-os-release = 2.0-9%{dist}%{?buildid}
Requires: open-power-host-os-base    = 2.0-9%{dist}%{?buildid}
Requires: open-power-host-os-virt    = 2.0-9%{dist}%{?buildid}
Requires: open-power-host-os-ras     = 2.0-9%{dist}%{?buildid}

# Extra packages required by Nutanix AHV.
Requires(post): libvirt-python = 2.2.0-1%{dist}
Requires(post): openvswitch = 2.5.2-2%{dist}%{?buildid}
Requires(post): nutanix-frodo = 1.0-1%{dist}%{?buildid}

# Required by AHV management stack.
Requires: net-tools
Requires: rsync

# Nice to haves.
Requires(post): nano
Requires(post): psmisc

%description release
%{summary}

%build
exit 0

%install
mkdir -p %{buildroot}%{_sysconfdir}/libvirt/hooks
install -m 0755 %{SOURCE1001} %{buildroot}%{_sysconfdir}/libvirt/hooks/qemu
mkdir -p %{buildroot}%{_sysconfdir}/sysctl.d/
cp %{SOURCE1002} %{buildroot}%{_sysconfdir}/sysctl.d/90-nutanix-ahv.conf

%files release
%{_sysconfdir}/libvirt/hooks/qemu
%{_sysconfdir}/sysctl.d/90-nutanix-ahv.conf
