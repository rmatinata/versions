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

# Base OpenPower Host OS with virtualization support.
Requires: open-power-host-os-release = 2.0-9%{dist}%{?buildid}
Requires: open-power-host-os-base    = 2.0-9%{dist}%{?buildid}
Requires: open-power-host-os-virt    = 2.0-9%{dist}%{?buildid}
Requires: open-power-host-os-ras     = 2.0-9%{dist}%{?buildid}

# Extra packages required by Nutanix AHV.
Requires(post): libvirt-python = 2.2.0-1%{dist}
Requires(post): openvswitch = 2.5.2-2%{dist}%{?buildid}
Requires(post): nutanix-frodo = 1.0-1%{dist}%{?buildid}
Requires: rsync
Requires: psmisc

%description release
%{summary}

%files release
