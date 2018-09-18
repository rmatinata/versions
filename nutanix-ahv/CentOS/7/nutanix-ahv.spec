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
Source1003: 15-nutanix-ahv.preset
Source1004: modules_ipmi.conf

BuildRequires: systemd-units
BuildRequires: systemd-devel

# Direct dependencies of files in this package.
Requires: /usr/bin/cgclassify

# Base OpenPower Host OS with virtualization support.
Requires: open-power-host-os-release = 2.0-10%{dist}%{?buildid}
Requires: open-power-host-os-base    = 2.0-10%{dist}%{?buildid}
Requires: open-power-host-os-virt    = 2.0-10%{dist}%{?buildid}
Requires: open-power-host-os-ras     = 2.0-10%{dist}%{?buildid}

# Extra packages required by Nutanix AHV.
Requires: openvswitch >= 2.5.2-2%{dist}%{?buildid}
Requires: nutanix-frodo >= 1.0-1%{dist}%{?buildid}
Requires: tunctl >= 1.5-3%{dist}%{?buildid}
Requires: kernel-tools = 4.9.85-1%{dist}%{?buildid}
Requires: kernel-bootwrapper = 4.9.85-1%{dist}%{?buildid}
Requires: opal-prd

# Required by AHV management stack.
Requires: ipmitool
Requires: libvirt-python
Requires: net-tools
Requires: rsync
Requires: lldpd

# Required by Foundation
Requires: ntp

# Nice to haves.
Requires(post): nano
Requires(post): psmisc
Requires(post): wget

# Actually required for running %post
Requires(post): systemd-units
Requires(post): openssh-server

%description release
%{summary}

%build
exit 0

%install
mkdir -p %{buildroot}%{_sysconfdir}/libvirt/hooks
install -m 0755 %{SOURCE1001} %{buildroot}%{_sysconfdir}/libvirt/hooks/qemu
mkdir -p %{buildroot}%{_sysconfdir}/sysctl.d/
cp %{SOURCE1002} %{buildroot}%{_sysconfdir}/sysctl.d/90-nutanix-ahv.conf
install -D -p -m 644 %{SOURCE1003} %{buildroot}%{_presetdir}/15-nutanix-ahv.preset
mkdir -p %{buildroot}%{_sysconfdir}/modules-load.d/
cp %{SOURCE1004} %{buildroot}%{_sysconfdir}/modules-load.d/ipmi.conf

%files release
%{_sysconfdir}/libvirt/hooks/qemu
%{_sysconfdir}/sysctl.d/90-nutanix-ahv.conf
%{_sysconfdir}/modules-load.d/ipmi.conf
%{_presetdir}/15-nutanix-ahv.preset

%post release
grep -q -e '^stdio_handler' %{_sysconfdir}/libvirt/qemu.conf || \
  echo 'stdio_handler = "file"' >> %{_sysconfdir}/libvirt/qemu.conf
%systemd_post firewalld.service
%systemd_post openvswitch.service
%systemd_post libvirtd.service
%systemd_post libvirtd-guests.service
systemctl preset opal-prd.service >/dev/null 2>&1 || :
systemctl preset tuned.service >/dev/null 2>&1 || :
sed -i "s/.*UseDNS.*/UseDNS = no/" %{_sysconfdir}/ssh/sshd_config || :
sed -i "s/.*GSSAPIAuthentication.*/GSSAPIAuthentication = no/" %{_sysconfdir}/ssh/sshd_config || :
