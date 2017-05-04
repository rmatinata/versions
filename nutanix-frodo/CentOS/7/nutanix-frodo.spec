Name:           nutanix-frodo
Version:        1.0
Release:        1%{?dist}%{?buildid}
Summary:        Nutanix vhost-scsi userspace backened, a.k.a. FRODO
License:        Nutanix EULA

Source0:	%{name}.tar.gz

Requires:       %{_libexecdir}/qemu-kvm, %{_bindir}/chcon
BuildRequires:  cmake, libuuid-devel, json-c-devel

%description
Nutanix vhost-scsi userspace backend for passing through SCSI requests from
guest directly to the CVM. This alternative datapath bypasses SCSI
emulation and block layer of QEMU.

%prep
%setup -n %{name}

%build
sed -i 's/-ggdb/-g/' CMakeLists.txt
sed -i 's/-pie/-pie -Wl,--build-id/' CMakeLists.txt
CFLAGS="$OPM_OPT_FLAGS" CC=gcc \
  make %{?_smp_mflags} BUILD_TYPE=release VERBOSE=1

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT%{_libexecdir}/
install build/release/frodo/frodo $RPM_BUILD_ROOT%{_libexecdir}/
cp scripts/qemu-kvm-frodo $RPM_BUILD_ROOT%{_libexecdir}/qemu-kvm-frodo
chmod a+x $RPM_BUILD_ROOT%{_libexecdir}/qemu-kvm-frodo

%post
chcon --reference %{_libexecdir}/qemu-kvm \
  %{_libexecdir}/frodo \
  %{_libexecdir}/qemu-kvm-frodo

%files
%{_libexecdir}/frodo
%{_libexecdir}/qemu-kvm-frodo

%changelog
