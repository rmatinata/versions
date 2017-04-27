
%define with_python3 0
%if 0%{?fedora} > 18
%define with_python3 1
%endif

Summary: The libvirt virtualization API python2 binding
Name: libvirt-python
Version: 2.2.0
Release: 1%{?dist}
Source0: %{name}.tar.gz

Url: http://libvirt.org
License: LGPLv2+
Group: Development/Libraries
BuildRequires: git
BuildRequires: libvirt-devel = 2.2.0
BuildRequires: python-devel
BuildRequires: python-nose
BuildRequires: python-lxml
%if %{with_python3}
BuildRequires: python3-devel
BuildRequires: python3-nose
BuildRequires: python3-lxml
%endif

# Don't want provides for python shared objects
%{?filter_provides_in: %filter_provides_in %{python_sitearch}/.*\.so}
%{?filter_setup}

%description
The libvirt-python package contains a module that permits applications
written in the Python programming language to use the interface
supplied by the libvirt library to use the virtualization capabilities
of recent versions of Linux (and other OSes).

%if %{with_python3}
%package -n libvirt-python3
Summary: The libvirt virtualization API python3 binding
Url: http://libvirt.org
License: LGPLv2+
Group: Development/Libraries

%description -n libvirt-python3
The libvirt-python package contains a module that permits applications
written in the Python programming language to use the interface
supplied by the libvirt library to use the virtualization capabilities
of recent versions of Linux (and other OSes).
%endif

%prep
%setup -q -n %{name}

# Unset execute bit for example scripts; it can introduce spurious
# RPM dependencies, like /usr/bin/python which can pull in python2
# for the -python3 package
find examples -type f -exec chmod 0644 \{\} \;

# Patches have to be stored in a temporary file because RPM has
# a limit on the length of the result of any macro expansion;
# if the string is longer, it's silently cropped
%{lua:
    tmp = os.tmpname();
    f = io.open(tmp, "w+");
    count = 0;
    for i, p in ipairs(patches) do
        f:write(p.."\n");
        count = count + 1;
    end;
    f:close();
    print("PATCHCOUNT="..count.."\n")
    print("PATCHLIST="..tmp.."\n")
}

git init -q
git config user.name rpm-build
git config user.email rpm-build
git config gc.auto 0
git add .
git commit -q -a --author 'rpm-build <rpm-build>' \
           -m '%{name}-%{version} base'

COUNT=$(grep '\.patch$' $PATCHLIST | wc -l)
if [ $COUNT -ne $PATCHCOUNT ]; then
    echo "Found $COUNT patches in $PATCHLIST, expected $PATCHCOUNT"
    exit 1
fi
if [ $COUNT -gt 0 ]; then
    xargs git am <$PATCHLIST || exit 1
fi
echo "Applied $COUNT patches"
rm -f $PATCHLIST


%build
CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build
%if %{with_python3}
CFLAGS="$RPM_OPT_FLAGS" %{__python3} setup.py build
%endif

%install
%{__python} setup.py install --skip-build --root=%{buildroot}
%if %{with_python3}
%{__python3} setup.py install --skip-build --root=%{buildroot}
%endif
rm -f %{buildroot}%{_libdir}/python*/site-packages/*egg-info

%check
%{__python} setup.py test
%if %{with_python3}
%{__python3} setup.py test
%endif

%files
%defattr(-,root,root)
%{_libdir}/python2*/site-packages/libvirt.py*
%{_libdir}/python2*/site-packages/libvirt_qemu.py*
%{_libdir}/python2*/site-packages/libvirt_lxc.py*
%{_libdir}/python2*/site-packages/libvirtmod*

%if %{with_python3}
%files -n libvirt-python3
%defattr(-,root,root)
%{_libdir}/python3*/site-packages/libvirt.py*
%{_libdir}/python3*/site-packages/libvirt_qemu.py*
%{_libdir}/python3*/site-packages/libvirt_lxc.py*
%{_libdir}/python3*/site-packages/__pycache__/libvirt.cpython-*.py*
%{_libdir}/python3*/site-packages/__pycache__/libvirt_qemu.cpython-*.py*
%{_libdir}/python3*/site-packages/__pycache__/libvirt_lxc.cpython-*.py*
%{_libdir}/python3*/site-packages/libvirtmod*
%endif

%changelog
* Thu Apr 27 2017 Mike Cui <cui@nutanix.com> - 2.2.0-1
- Rebased to libvirt-python-2.2.0

* Fri Jul  1 2016 Jiri Denemark <jdenemar@redhat.com> - 2.0.0-1
- Rebased to libvirt-python-2.0.0 (rhbz#1286680)

* Wed Jun  8 2016 Jiri Denemark <jdenemar@redhat.com> - 1.3.5-1
- Rebased to libvirt-python-1.3.5 (rhbz#1286680)

* Tue May  3 2016 Jiri Denemark <jdenemar@redhat.com> - 1.3.4-1
- Rebased to libvirt-python-1.3.4 (rhbz#1286680)
- The rebase also fixes the following bugs:
    rhbz#1286680, rhbz#1326839

* Wed Apr  6 2016 Jiri Denemark <jdenemar@redhat.com> - 1.3.3-1
- Rebased to libvirt-python-1.3.3 (rhbz#1286680)
- The rebase also fixes the following bugs:
    rhbz#

* Wed Mar  2 2016 Jiri Denemark <jdenemar@redhat.com> - 1.3.2-1
- Rebased to libvirt-python-1.3.2 (rhbz#1286680)
- The rebase also fixes the following bugs:
    rhbz#1311058

* Tue Aug  4 2015 Jiri Denemark <jdenemar@redhat.com> - 1.2.17-2
- examples: Introduce nodestats example (rhbz#1051494)
- iothread: Fix crash if virDomainGetIOThreadInfo returns error (rhbz#1248295)
- Check return value of PyList_Append (rhbz#1249511)

* Thu Jul  2 2015 Jiri Denemark <jdenemar@redhat.com> - 1.2.17-1
- Rebased to libvirt-python-1.2.17 (rhbz#1194594)
- The rebase also fixes the following bugs:
    rhbz#1194594, rhbz#1222795

* Thu Jun  4 2015 Jiri Denemark <jdenemar@redhat.com> - 1.2.16-1
- Rebased to libvirt-python-1.2.16 (rhbz#1194594)

* Mon May  4 2015 Jiri Denemark <jdenemar@redhat.com> - 1.2.15-1
- Rebased to libvirt-python-1.2.15 (rhbz#1194594)
- The rebase also fixes the following bugs:
    rhbz#1212168

* Thu Apr  2 2015 Jiri Denemark <jdenemar@redhat.com> - 1.2.14-1
- Rebased to libvirt-python-1.2.14 (rhbz#1194594)
- The rebase also fixes the following bugs:
    rhbz#1198518

* Thu Mar 26 2015 Jiri Denemark <jdenemar@redhat.com> - 1.2.13-1
- Rebased to libvirt-python-1.2.13 (rhbz#1194594)
- The rebase also fixes the following bugs:
    rhbz#1154918, rhbz#1175795, rhbz#1195848

* Wed Dec 17 2014 Jiri Denemark <jdenemar@redhat.com> - 1.2.8-7
- Rebuild libvirt-python to pick up the new flag for fetching backing chain statistics (rhbz#1175276)

* Tue Nov 25 2014 Jiri Denemark <jdenemar@redhat.com> - 1.2.8-6
- event: Add bindings for agent lifecycle event (rhbz#1167336)
- RHEL-only: downgrade version check for agent lifecycle event (rhbz#1167336)

* Thu Nov  6 2014 Jiri Denemark <jdenemar@redhat.com> - 1.2.8-5
- Fix parsing of 'flags' argument for bulk stats functions (rhbz#1155016)
- flags cannot get right value for blockCopy function (rhbz#1155484)
- virDomainBlockCopy: initialize flags to 0 (rhbz#1155484)
- implement new tunable event (rhbz#1147639)
- RHEL: change version checking from 1.2.9 to 1.2.8 for tunable event (rhbz#1147639)
- Check return value of libvirt_uintUnwrap (rhbz#1161039)
- Rebuild libvirt-python to pick up new additions to libvirt.h (rhbz#1160792)

* Mon Sep 29 2014 Jiri Denemark <jdenemar@redhat.com> - 1.2.8-4
- Rebuild libvirt-python to pick up new additions to libvirt.h (rhbz#1147022)

* Fri Sep 19 2014 Jiri Denemark <jdenemar@redhat.com> - 1.2.8-3
- generator: Free strings after libvirt_charPtrWrap (rhbz#1140998)
- Rebuild to pick up the new flag for removing NVRAM files (rhbz#1144284)

* Wed Sep 10 2014 Jiri Denemark <jdenemar@redhat.com> - 1.2.8-2
- override: Fix two uninitialized variables in convertDomainStatsRecord (rhbz#1136354)
- Rebuild to pick up the new flag for completed migration stats (rhbz#1138570)

* Tue Sep  2 2014 Jiri Denemark <jdenemar@redhat.com> - 1.2.8-1
- Rebased to libvirt-python-1.2.8 (rhbz#1116978)
- libvirt-override: fix some build warnings (rhbz#1116978)

* Tue Aug  5 2014 Jiri Denemark <jdenemar@redhat.com> - 1.2.7-1
- Rebased to libvirt-python-1.2.7 (rhbz#1116978)

* Fri Aug  1 2014 Jiri Denemark <jdenemar@redhat.com> - 1.2.6-1
- Rebased to libvirt-python-1.2.6 (rhbz#1116978)

* Mon Mar 24 2014 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-29
- nwfilter: Increase buffer size for libpcap (rhbz#1078347)
- nwfilter: Display pcap's error message when pcap setup fails (rhbz#1078347)
- nwfilter: Fix double free of pointer (rhbz#1071181)

* Tue Mar 18 2014 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-28
- qemu: Forbid "sgio" support for SCSI generic host device (rhbz#957292)
- qemu: monitor: Fix invalid parentheses (rhbz#1075973)
- qemu: Introduce qemuDomainDefCheckABIStability (rhbz#1076503)

* Wed Mar 12 2014 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-27
- spec: Let translations be properly updated (rhbz#1030368)
- Update translation to supported languages (rhbz#1030368)
- Add a mutex to serialize updates to firewall (rhbz#1074003)

* Wed Mar  5 2014 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-26
- virNetDevVethCreate: Serialize callers (rhbz#1014604)
- qemuBuildNicDevStr: Adapt to new advisory on multiqueue (rhbz#1071888)

* Wed Feb 26 2014 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-25
- maint: fix comma style issues: conf (rhbz#1032370)
- Allow <source> for type=block to have no dev (rhbz#1032370)
- Allow LUN type disks to have no source (rhbz#1032370)
- virsh-volume: Unify strigification of volume type (rhbz#1032370)
- conf: Refactor virDomainDiskSourcePoolDefParse (rhbz#1032370)
- conf: Split out code to parse the source of a disk definition (rhbz#1032370)
- conf: Rename virDomainDiskHostDefFree to virDomainDiskHostDefClear (rhbz#1032370)
- conf: Refactor virDomainDiskSourceDefParse (rhbz#1032370)
- storage: fix RNG validation of gluster via netfs (rhbz#1032370)
- maint: fix comment typos. (rhbz#1032370)
- storage: use valid XML for awkward volume names (rhbz#1032370)
- build: Don't fail on '&lt; ' or '&gt; ' with old xmllint (rhbz#1032370)
- storage: allow interleave in volume XML (rhbz#1032370)
- storage: expose volume meta-type in XML (rhbz#1032370)
- storage: initial support for linking with libgfapi (rhbz#1032370)
- storage: document existing pools (rhbz#1032370)
- storage: document gluster pool (rhbz#1032370)
- storage: implement rudimentary glusterfs pool refresh (rhbz#1032370)
- storage: add network-dir as new storage volume type (rhbz#1032370)
- storage: improve directory support in gluster pool (rhbz#1032370)
- storage: improve allocation stats reported on gluster files (rhbz#1032370)
- storage: improve handling of symlinks in gluster (rhbz#1032370)
- storage: probe qcow2 volumes in gluster pool (rhbz#1032370)
- storage: fix typo in previous patch (rhbz#1032370)
- conf: Export virStorageVolType enum helper functions (rhbz#1032370)
- test: Implement fake storage pool driver in qemuxml2argv test (rhbz#1032370)
- storage: reduce number of stat calls (rhbz#1032370)
- storage: use simpler 'char *' (rhbz#1032370)
- storage: refactor backing chain division of labor (rhbz#1032370)
- storage: always probe type with buffer (rhbz#1032370)
- storage: don't read storage volumes in nonblock mode (rhbz#1032370)
- storage: skip selinux cleanup when fd not available (rhbz#1032370)
- storage: use correct type for array count (rhbz#1032370)
- storage: allow interleave in pool XML (rhbz#1032370)
- qemuxml2argv: Add test to verify correct usage of disk type="volume" (rhbz#1032370)
- qemuxml2argv: Add test for disk type='volume' with iSCSI pools (rhbz#1032370)
- tests: Fix comment for fake storage pool driver (rhbz#1032370)
- conf: Support disk source formatting without needing a virDomainDiskDefPtr (rhbz#1032370)
- conf: Clean up virDomainDiskSourceDefFormatInternal (rhbz#1032370)
- conf: Split out seclabel formating code for disk source (rhbz#1032370)
- conf: Export disk source formatter and parser (rhbz#1032370)
- snapshot: conf: Use common parsing and formatting functions for source (rhbz#1032370)
- snapshot: conf: Fix NULL dereference when <driver> element is empty (rhbz#1032370)
- conf: Add functions to copy and free network disk source definitions (rhbz#1032370)
- qemu: snapshot: Detect internal snapshots also for sheepdog and RBD (rhbz#1032370)
- conf: Add helper do clear disk source authentication struct (rhbz#1032370)
- qemu: snapshot: Touch up error message (rhbz#1032370)
- qemu: snapshot: Add functions similar to disk source pool translation (rhbz#1032370)
- qemu: Refactor qemuTranslateDiskSourcePool (rhbz#1032370)
- qemu: Split out formatting of network disk source URI (rhbz#1032370)
- qemu: Simplify call pattern of qemuBuildDriveURIString (rhbz#1032370)
- qemu: Use qemuBuildNetworkDriveURI to handle http/ftp and friends (rhbz#1032370)
- qemu: Migrate sheepdog source generation into common function (rhbz#1032370)
- qemu: Split out NBD command generation (rhbz#1032370)
- qemu: Unify formatting of RBD sources (rhbz#1032370)
- qemu: Refactor disk source string formatting (rhbz#1032370)
- qemu: Clear old translated pool source (rhbz#1032370)
- qemu: snapshots: Declare supported and unsupported snapshot configs (rhbz#1032370)
- domainsnapshotxml2xmltest: Clean up labels and use bool instead of int (rhbz#1032370)
- domainsnapshotxml2xmltest: Allow for better testing of snapshots (rhbz#1032370)
- domainsnapshotxml2xml: Move files with conflicting names (rhbz#1032370)
- domainsnapshotxml2xmltest: Add existing files as new tests (rhbz#1032370)
- domainsnapshotxml2xmltest: Add test case for empty driver element (rhbz#1032370)
- qemu: Fix indentation in qemuTranslateDiskSourcePool (rhbz#1032370)
- qemu: snapshot: Fix incorrect disk type for auto-generated disks (rhbz#1032370)
- storage: fix omitted slash in gluster volume URI (rhbz#1032370)
- virsh: domain: Fix undefine with storage of 'volume' disks (rhbz#1032370)
- snapshot: schema: Split out snapshot disk driver definition (rhbz#1032370)
- storage: Add gluster pool filter and fix virsh pool listing (rhbz#1032370)
- storage: fix bogus target in gluster volume xml (rhbz#1032370)
- storage: Improve error message when a storage backend is missing (rhbz#1032370)
- storage: Break long lines and clean up spaces in storage backend header (rhbz#1032370)
- storage: Support deletion of volumes on gluster pools (rhbz#1032370)
- qemu: snapshot: Avoid libvirtd crash when qemu crashes while snapshotting (rhbz#1032370)
- qemu: snapshot: Forbid snapshots when backing is a scsi passthrough disk (rhbz#1034993)
- qemu: Avoid crash in qemuDiskGetActualType (rhbz#1032370)
- snapshot: Add support for specifying snapshot disk backing type (rhbz#1032370)
- conf: Move qemuDiskGetActualType to virDomainDiskGetActualType (rhbz#1032370)
- conf: Move qemuSnapshotDiskGetActualType to virDomainSnapshotDiskGetActualType (rhbz#1032370)
- storage: Add file storage APIs in the default storage driver (rhbz#1032370)
- storage: add file functions for local and block files (rhbz#1032370)
- storage: Add storage file backends for gluster (rhbz#1032370)
- qemu: Switch snapshot deletion to the new API functions (rhbz#1032370)
- qemu: snapshot: Use new APIs to detect presence of existing storage files (rhbz#1032370)
- qemu: snapshot: Add support for external active snapshots on gluster (rhbz#1032370)
- storage: Fix build with older compilers afeter gluster snapshot series (rhbz#1032370)
- storage: gluster: Don't leak private data when storage file init fails (rhbz#1032370)
- spec: Use correct versions of libgfapi in RHEL builds (rhbz#1032370)
- spec: Fix braces around macros (rhbz#1032370)
- build: use --with-systemd-daemon as configure option (rhbz#1032695)
- spec: require device-mapper-devel for storage-disk (rhbz#1032695)
- spec: make systemd_daemon usage configurable (rhbz#1032695)

* Tue Feb 25 2014 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-24
- Block info query: Add check for transient domain (rhbz#1065531)
- Fix minor typos in messages and docs (rhbz#1045643)
- LXC: Free variable vroot in lxcDomainDetachDeviceHostdevUSBLive() (rhbz#1045643)
- LXC: free dst before lxcDomainAttachDeviceDiskLive returns (rhbz#1045643)
- maint: fix comment typos (rhbz#1045643)
- storage: avoid short reads while chasing backing chain (rhbz#1045643)
- Don't block use of USB with containers (rhbz#1045643)
- Fix path used for USB device attach with LXC (rhbz#1045643)
- Record hotplugged USB device in LXC live guest config (rhbz#1045643)
- Fix reset of cgroup when detaching USB device from LXC guests (rhbz#1045643)
- Disks are always block devices, never character devices (rhbz#1045643)
- Move check for cgroup devices ACL upfront in LXC hotplug (rhbz#1045643)
- Add virFileMakeParentPath helper function (rhbz#1045643)
- Add helper for running code in separate namespaces (rhbz#1045643)
- CVE-2013-6456: Avoid unsafe use of /proc/$PID/root in LXC shutdown/reboot code (CVE-2013-6456)
- CVE-2013-6456: Avoid unsafe use of /proc/$PID/root in LXC disk hotplug (CVE-2013-6456)
- CVE-2013-6456: Avoid unsafe use of /proc/$PID/root in LXC USB hotplug (CVE-2013-6456)
- CVE-2013-6456: Avoid unsafe use of /proc/$PID/root in LXC block hostdev hotplug (CVE-2013-6456)
- CVE-2013-6456: Avoid unsafe use of /proc/$PID/root in LXC chardev hostdev hotplug (CVE-2013-6456)
- CVE-2013-6456: Avoid unsafe use of /proc/$PID/root in LXC hotunplug code (CVE-2013-6456)
- Ignore additional fields in iscsiadm output (rhbz#1067173)
- qemuBuildNicDevStr: Set vectors= on Multiqueue (rhbz#1066209)
- Don't depend on syslog.service (rhbz#1032695)
- libvirt-guests: Run only after libvirtd (rhbz#1032695)
- virSystemdCreateMachine: Set dependencies for slices (rhbz#1032695)
- libvirt-guests: Wait for libvirtd to initialize (rhbz#1032695)
- virNetServerRun: Notify systemd that we're accepting clients (rhbz#1032695)

* Wed Feb 12 2014 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-23
- Generate a valid imagelabel even for type 'none' (rhbz#1061657)
- qemu: keep pre-migration domain state after failed migration (rhbz#1057407)
- schema: Fix guest timer specification schema according to the docs (rhbz#1056205)
- conf: Enforce supported options for certain timers (rhbz#1056205)
- qemu: hyperv: Add support for timer enlightenments (rhbz#1056205)
- build: correctly check for SOICGIFVLAN GET_VLAN_VID_CMD command (rhbz#1062665)
- util: Add "shareable" field for virSCSIDevice struct (rhbz#957292)
- util: Fix the indention (rhbz#957292)
- qemu: Don't fail if the SCSI host device is shareable between domains (rhbz#957292)
- util: Add one argument for several scsi utils (rhbz#957292)
- tests: Add tests for scsi utils (rhbz#957292)
- qemu: Fix the error message for scsi host device's shareable checking (rhbz#957292)
- util: Accept test data path for scsi device's sg_path (rhbz#957292)
- tests: Modify the scsi util tests (rhbz#957292)
- event: move event filtering to daemon (regression fix) (rhbz#1047964)

* Wed Feb  5 2014 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-22
- Add a read/write lock implementation (rhbz#1034807)
- Push nwfilter update locking up to top level (rhbz#1034807)
- utils: Introduce functions for kernel module manipulation (rhbz#1045124)
- virCommand: Introduce virCommandSetDryRun (rhbz#1045124)
- tests: Add test for new virkmod functions (rhbz#1045124)
- Honor blacklist for modprobe command (rhbz#1045124)
- qemu: Be sure we're using the updated value of backend during hotplug (rhbz#1056360)
- network: Permit upstream forwarding of unqualified DNS names (rhbz#1061099)
- network: Only prevent forwarding of DNS requests for unqualified names (rhbz#1061099)
- network: Change default of forwardPlainNames to 'yes' (rhbz#1061099)

* Wed Jan 29 2014 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-21
- util: Correct the NUMA node range checking (rhbz#1045958)
- storage: Add document for possible problem on volume detection (rhbz#726797)
- storage: Fix autostart of pool with "fc_host" type adapter (rhbz#726797)

* Fri Jan 24 2014 Daniel Mach <dmach@redhat.com> - 1.1.1-20
- Mass rebuild 2014-01-24

* Wed Jan 22 2014 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-19
- CVE-2013-6436: Fix crash in lxcDomainGetMemoryParameters (rhbz#1049137)
- Fix crash in lxcDomainSetMemoryParameters (rhbz#1052062)
- Don't crash if a connection closes early (CVE-2014-1447)
- Really don't crash if a connection closes early (CVE-2014-1447)
- qemu: Change the default unix monitor timeout (rhbz#892273)
- virSecuritySELinuxSetFileconHelper: Don't fail on read-only NFS (rhbz#996543)
- qemu: Avoid operations on NULL monitor if VM fails early (rhbz#1054785)
- virt-login-shell: Fix regressions in behavior (rhbz#1015247)
- pci: Make reattach work for unbound devices (rhbz#1046919)
- pci: Fix failure paths in detach (rhbz#1046919)
- qemu: Don't detach devices if passthrough doesn't work (rhbz#1046919)
- Fix migration with QEMU 1.6 (rhbz#1053405)
- build: More workarounds for if_bridge.h (rhbz#1042937)
- build: Fix build with latest rawhide kernel headers (rhbz#1042937)
- aarch64: Disable -fstack-protector. (rhbz#1042937)
- AArch64: Parse cputopology from /proc/cpuinfo. (rhbz#1042937)
- virDomainEventCallbackListFree: Don't leak @list->callbacks (rhbz#1047964)
- Fix memory leak in virObjectEventCallbackListRemoveID() (rhbz#1047964)
- event: Filter global events by domain:getattr ACL (CVE-2014-0028)
- Doc: Improve the document for nodesuspend (rhbz#1045089)
- Doc: Add "note" for node-memory-tune (rhbz#1045089)

* Wed Jan  8 2014 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-18
- qemu: Ask for -enable-fips when FIPS is required (rhbz#1035474)
- qemu: Properly set MaxMemLock when hotplugging with VFIO (rhbz#1035490)
- qemu: Avoid duplicate security label restore on hostdev attach failure (rhbz#1035490)
- qemu: Re-add hostdev interfaces to hostdev array on libvirtd restart (rhbz#1045002)
- domain: Don't try to interpret <driver> as virtio config for hostdev interfaces (rhbz#1046337)
- virBitmapParse: Fix behavior in case of error and fix up callers (rhbz#1047234)
- qemu: Fix live pinning to memory node on NUMA system (rhbz#1047234)
- qemu: Clean up qemuDomainSetNumaParameters (rhbz#1047234)
- qemu: Range check numa memory placement mode (rhbz#1047234)
- virkeycode: Allow ANSI_A (rhbz#1044806)
- Fix argument order of qemuMigrationPerformJob(). (rhbz#1049338)
- qemu: Do not access stale data in virDomainBlockStats (CVE-2013-6458)
- qemu: Avoid using stale data in virDomainGetBlockInfo (CVE-2013-6458)
- qemu: Fix job usage in qemuDomainBlockJobImpl (CVE-2013-6458)
- qemu: Fix job usage in qemuDomainBlockCopy (rhbz#1048643)
- qemu: Fix job usage in virDomainGetBlockIoTune (CVE-2013-6458)
- PanicCheckABIStability: Need to check for existence (rhbz#996520)
- virsh: Improve usability of '--print-xml' flag for attach-disk command (rhbz#1049529)
- virsh: Don't use legacy API if --current is used on device hot(un)plug (rhbz#1049529)
- virsh: Use inactive definition when removing disk from config (rhbz#1049529)

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 1.1.1-17
- Mass rebuild 2013-12-27

* Wed Dec 18 2013 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-16
- qemu: Check for reboot-timeout on monitor (rhbz#1042690)
- virsh: Fix return value error of cpu-stats (rhbz#1043388)
- tools: Fix virsh connect man page (rhbz#1043260)
- conf: Introduce generic ISA address (rhbz#996520)
- conf: Add support for panic device (rhbz#996520)
- qemu: Add support for -device pvpanic (rhbz#996520)
- Fix invalid read in virNetSASLSessionClientStep debug log (rhbz#1043864)
- virsh: man: Mention that volumes need to be in storage pool for undefine (rhbz#1044445)

* Fri Dec 13 2013 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-15
- spec: Don't save/restore running VMs on libvirt-client update (rhbz#1033626)
- qemu: hotplug: Only label hostdev after checking device conflicts (rhbz#1025108)
- qemu: hotplug: Fix double free on USB collision (rhbz#1025108)
- qemu: hotplug: Fix adding USB devices to the driver list (rhbz#1025108)
- docs: Enhance memoryBacking/locked documentation (rhbz#1035954)
- util: Fix two virCompareLimitUlong bugs (rhbz#1024272)
- cgroups: Redefine what "unlimited" means wrt memory limits (rhbz#1024272)
- qemu: Report VIR_DOMAIN_MEMORY_PARAM_UNLIMITED properly (rhbz#1024272)
- qemu: Fix minor inconsistency in error message (rhbz#1024272)
- conf: Don't format memtune with unlimited values (rhbz#1024272)
- qemu_process: Read errors from child (rhbz#1035955)
- network: Properly update iptables rules during net-update (rhbz#1035336)
- Tie SASL callbacks lifecycle to virNetSessionSASLContext (rhbz#1039991)
- screenshot: Implement multiple screen support (rhbz#1026966)
- Switch to private redhat namespace for QMP I/O error reason (rhbz#1026966)
- Support virtio disk hotplug in JSON mode (rhbz#1026966)

* Fri Dec  6 2013 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-14
- nodedev: Resolve Relax-NG validity error (rhbz#1035792)
- test-lib: Make case skipping possible (rhbz#1034380)
- tests: Don't test user config file if ran as root (rhbz#1034380)
- Improve cgroups docs to cover systemd integration (rhbz#1004340)
- Fix busy wait loop in LXC container I/O handling (rhbz#1032705)
- tests: Guarantee abs_srcdir in all C tests (rhbz#1035403)
- Introduce standard methods for sorting strings with qsort (rhbz#1035403)
- Add virFileIsMountPoint function (rhbz#1035403)
- Pull lxcContainerGetSubtree out into shared virfile module (rhbz#1035403)
- Fix bug in identifying sub-mounts (rhbz#1035403)
- LXC: Ensure security context is set when mounting images (rhbz#923903)
- Ensure to zero out the virDomainBlockJobInfo arg (rhbz#1028846)
- qemu: Default to vfio for nodedev-detach (rhbz#1035188)
- daemon: Run virStateCleanup conditionally (rhbz#1033061)
- qemu: Add "-boot strict" to commandline whenever possible (rhbz#1037593)
- tests: Add forgotten boot-strict test files (rhbz#1037593)
- conf: Fix XML formatting of RNG device info (rhbz#1035118)
- qemu: Improve error when setting invalid count of vcpus via agent (rhbz#1035108)
- Add qxl ram size to ABI stability check (rhbz#1035123)

* Fri Nov 22 2013 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-13
- virsh-domain: Mark --live and --config mutually exclusive in vcpucount (rhbz#1024245)
- virSecurityLabelDefParseXML: Don't parse label on model='none' (rhbz#1028962)
- qemuMonitorIO: Don't use @mon after it's unrefed (rhbz#1018267)
- qemu: Allow hotplug of multiple SCSI devices (rhbz#1031062)
- qemu: Call qemuSetupHostdevCGroup later during hotplug (rhbz#1025108)
- virscsi: Hostdev SCSI AdapterId retrieval fix (rhbz#1031079)
- storage: Returns earlier if source adapter of the scsi pool is a HBA (rhbz#1027680)
- spec: Restrict virt-login-shell usage (rhbz#1033614)
- spec: Don't save/restore running VMs on libvirt-client update (rhbz#1033626)
- Don't start a nested job in qemuMigrationPrepareAny (rhbz#1018267)

* Fri Nov  8 2013 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-12
- virpci: Don't error on unbinded devices (rhbz#1019387)
- network: Fix connections count in case of allocate failure (rhbz#1020135)
- qemu: Clean up migration ports when migration cancelled (rhbz#1019237)
- qemuMigrationBeginPhase: Check for 'drive-mirror' for NBD (rhbz#1022393)
- Allow root directory in filesystem source dir schema (rhbz#1028107)
- Use a port from the migration range for NBD as well (rhbz#1025699)
- qemu: Avoid double free of VM (rhbz#1018267)
- util: Use size_t instead of unsigned int for num_virtual_functions (rhbz#1025397)
- pci: Properly handle out-of-order SRIOV virtual functions (rhbz#1025397)
- conf: Do better job when comparing features ABI compatibility (rhbz#1008989)
- schema: Rename option 'hypervtristate' to 'featurestate' (rhbz#1008989)
- conf: Mark user provided strings in error messages when parsing XML (rhbz#1008989)
- cpu: Add support for loading and storing CPU data (rhbz#1008989)
- cpu: x86: Rename struct cpuX86cpuid as virCPUx86CPUID (rhbz#1008989)
- cpu: x86: Rename struct cpuX86Data as virCPUx86Data (rhbz#1008989)
- cpu: x86: Rename x86DataFree() as virCPUx86DataFree() (rhbz#1008989)
- Ensure 'arch' is always set in cpuArchNodeData (rhbz#1008989)
- cpu: x86: Rename x86MakeCPUData as virCPUx86MakeData (rhbz#1008989)
- cpu: x86: Rename x86DataAddCpuid as virCPUx86DataAddCPUID (rhbz#1008989)
- cpu: x86: Rename data_iterator and DATA_ITERATOR_INIT (rhbz#1008989)
- cpu: x86: Fix return types of x86cpuidMatch and x86cpuidMatchMasked (rhbz#1008989)
- cpu: x86: Use whitespace to clarify context and use consistent labels (rhbz#1008989)
- cpu: x86: Clean up error messages in x86VendorLoad() (rhbz#1008989)
- cpu: Export few x86-specific APIs (rhbz#1008989)
- cpu: x86: Parse the CPU feature map only once (rhbz#1008989)
- cpu_x86: Refactor storage of CPUID data to add support for KVM features (rhbz#1008989)
- qemu: Add monitor APIs to fetch CPUID data from QEMU (rhbz#1008989)
- cpu: x86: Add internal CPUID features support and KVM feature bits (rhbz#1008989)
- conf: Refactor storing and usage of feature flags (rhbz#1008989)
- qemu: Add support for paravirtual spinlocks in the guest (rhbz#1008989)
- qemu: process: Validate specific CPUID flags of a guest (rhbz#1008989)

* Fri Nov  1 2013 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-11
- Add helpers for getting env vars in a setuid environment (rhbz#1015247)
- Only allow 'stderr' log output when running setuid (CVE-2013-4400)
- Close all non-stdio FDs in virt-login-shell (CVE-2013-4400)
- Don't link virt-login-shell against libvirt.so (CVE-2013-4400)
- build: Fix linking virt-login-shell (rhbz#1015247)
- build: Fix build of virt-login-shell on systems with older gnutls (rhbz#1015247)
- Set a sane $PATH for virt-login-shell (rhbz#1015247)
- spec: Fix rpm build when lxc disabled (rhbz#1015247)
- Move virt-login-shell into libvirt-login-shell sub-RPM (rhbz#1015247)
- Make virCommand env handling robust in setuid env (rhbz#1015247)
- Remove all direct use of getenv (rhbz#1015247)
- Block all use of getenv with syntax-check (rhbz#1015247)
- Only allow the UNIX transport in remote driver when setuid (rhbz#1015247)
- Don't allow remote driver daemon autostart when running setuid (rhbz#1015247)
- Add stub getegid impl for platforms lacking it (rhbz#1015247)
- Remove (nearly) all use of getuid()/getgid() (rhbz#1015247)
- Block all use of libvirt.so in setuid programs (rhbz#1015247)
- spec: Clean up distribution of ChangeLog (and others) (rhbz#1024393)
- Push RPM deps down into libvirt-daemon-driver-XXXX sub-RPMs (rhbz#1024393)

* Wed Oct 23 2013 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-10
- qemu_process: Make qemuProcessReadLog() more versatile and reusable (rhbz#1001738)
- qemu: monitor: Add infrastructure to access VM logs for better err msgs (rhbz#1001738)
- qemu: monitor: Produce better errors on monitor hangup (rhbz#1001738)
- qemu: Wire up better early error reporting (rhbz#1001738)
- qemu: process: Silence coverity warning when rewinding log file (rhbz#1001738)
- qemu: hostdev: Refactor PCI passhrough handling (rhbz#1001738)
- qemu: hostdev: Fix function spacing and header formatting (rhbz#1001738)
- qemu: hostdev: Add checks if PCI passthrough is available in the host (rhbz#1001738)
- qemu: Prefer VFIO for PCI device passthrough (rhbz#1001738)
- qemu: Init @pcidevs in qemuPrepareHostdevPCIDevices (rhbz#1001738)
- Fix max stream packet size for old clients (rhbz#950416)
- Adjust legacy max payload size to account for header information (rhbz#950416)
- rpc: Correct the wrong payload size checking (rhbz#950416)
- qemu: Simplify calling qemuDomainHostdevNetConfigRestore (rhbz#1005682)
- qemu: Move qemuDomainRemoveNetDevice to avoid forward reference (rhbz#1005682)
- qemu: Fix removal of <interface type='hostdev'> (rhbz#1005682)
- remote: Fix regression in event deregistration (rhbz#1020376)
- qemu: managedsave: Add support for compressing managed save images (rhbz#1017227)
- qemu: snapshot: Add support for compressing external snapshot memory (rhbz#1017227)
- Migration: Introduce VIR_MIGRATE_PARAM_LISTEN_ADDRESS (rhbz#1015215)
- virsocket: Introduce virSocketAddrIsWildcard (rhbz#1015215)
- qemu: Implement support for VIR_MIGRATE_PARAM_LISTEN_ADDRESS (rhbz#1015215)
- qemu_conf: Introduce "migration_address" (rhbz#1015215)
- qemu: Include listenAddress in debug prints (rhbz#1015215)
- docs: Expand description of host-model CPU mode (rhbz#1014682)
- qemu: Avoid assigning unavailable migration ports (rhbz#1019237)
- qemu: Make migration port range configurable (rhbz#1019237)
- qemu: Fix augeas support for migration ports (rhbz#1019237)
- Fix perms for virConnectDomainXML{To, From}Native (CVE-2013-4401)

* Tue Oct 15 2013 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-9
- virNetDevBandwidthEqual: Make it more robust (rhbz#1014503)
- qemu_hotplug: Allow QoS update in qemuDomainChangeNet (rhbz#1014503)
- qemu: Check actual netdev type rather than config netdev type during init (rhbz#1012824)
- Fix crash in libvirtd when events are registered & ACLs active (CVE-2013-4399) (rhbz#1011429)
- Remove virConnectPtr arg from virNWFilterDefParse* (rhbz#1015108)
- Don't pass virConnectPtr in nwfilter 'struct domUpdateCBStruct' (rhbz#1015108)
- Remove use of virConnectPtr from all remaining nwfilter code (rhbz#1015108)
- Don't set netdev offline in container cleanup (rhbz#1014604)
- Avoid reporting an error if veth device is already deleted (rhbz#1014604)
- Avoid deleting NULL veth device name (rhbz#1014604)
- Retry veth device creation on failure (rhbz#1014604)
- Use 'vnet' as prefix for veth devices (rhbz#1014604)
- Free cmd in virNetDevVethDelete (rhbz#1014604)
- Free cmd in virNetDevVethCreate (rhbz#1014604)
- LXC: Fix handling of RAM filesystem size units (rhbz#1015689)
- build: Add lxc testcase to dist list (rhbz#1015689)
- tests: Work with older dbus (rhbz#1018730)
- virdbus: Add virDBusHasSystemBus() (rhbz#1018730)
- virsystemd: Don't fail to start VM if DBus isn't available or compiled in (rhbz#1018730)
- DBus: Introduce virDBusIsServiceEnabled (rhbz#1018730)
- Change way we fake dbus method calls (rhbz#1018730)
- Fix virsystemdtest for previous commit (rhbz#1018730)
- LXC: Workaround machined uncleaned data with containers running systemd. (rhbz#1018730)
- Allow use of a private dbus bus connection (rhbz#998365)
- Add a method for closing the dbus system bus connection (rhbz#998365)
- Make LXC controller use a private dbus connection & close it (rhbz#998365)
- Fix flaw in detecting log format (rhbz#927072)
- Fix exit status of lxc controller (rhbz#927072)
- Improve error reporting with LXC controller (rhbz#927072)
- nwfilter: Don't fail to start if DBus isn't available (rhbz#927072)
- Don't ignore all dbus connection errors (rhbz#927072)
- LXC: Check the existence of dir before resolving symlinks (rhbz#927072)
- Ensure lxcContainerMain reports errors on stderr (rhbz#927072)
- Ensure lxcContainerResolveSymlinks reports errors (rhbz#927072)
- Improve log filtering in virLXCProcessReadLogOutputData (rhbz#927072)
- Initialize threading & error layer in LXC controller (rhbz#1018725)
- qemu_migration: Avoid crashing if domain dies too quickly (rhbz#1018267)
- Convert uuid to a string before printing it (rhbz#1019023)

* Wed Oct  2 2013 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-8
- conf: Don't crash on invalid chardev source definition of RNGs and other (rhbz#1012196)
- rpc: Increase bound limit for virDomainGetJobStats (rhbz#1012818)
- qemu: Free all driver data in qemuStateCleanup (rhbz#1011330)
- qemu: Don't leak reference to virQEMUDriverConfigPtr (rhbz#1011330)
- qemu: Eliminate redundant if clauses in qemuCollectPCIAddress (rhbz#1003983)
- qemu: Allow some PCI devices to be attached to PCIe slots (rhbz#1003983)
- qemu: Replace multiple strcmps with a switch on an enum (rhbz#1003983)
- qemu: Support ich9-intel-hda audio device (rhbz#1003983)
- qemu: Turn if into switch in qemuDomainValidateDevicePCISlotsQ35 (rhbz#1003983)
- qemu: Prefer to put a Q35 machine's dmi-to-pci-bridge at 00:1E.0 (rhbz#1003983)

* Wed Sep 25 2013 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-7
- Fix crash in remoteDispatchDomainMemoryStats (CVE-2013-4296)
- LXC: Don't mount securityfs when user namespace enabled (rhbz#872648)
- Move array of mounts out of lxcContainerMountBasicFS (rhbz#872648)
- Ensure root filesystem is recursively mounted readonly (rhbz#872648)
- qemu: Fix seamless SPICE migration (rhbz#1010861)
- qemu: Use "ide" as device name for implicit SATA controller on Q35 (rhbz#1008903)
- qemu: Only parse basename when determining emulator properties (rhbz#1010617)
- qemu: Recognize -machine accel=kvm when parsing native (rhbz#1010617)
- qemu: Don't leave shutdown inhibited on attach failure (rhbz#1010617)
- qemu: Don't leak vm on failure (rhbz#1010617)
- Fix typo in identity code which is pre-requisite for CVE-2013-4311 (rhbz#1006272)

* Thu Sep 19 2013 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-6
- Also store user & group ID values in virIdentity (rhbz#1006272)
- Ensure system identity includes process start time (rhbz#1006272)
- Add support for using 3-arg pkcheck syntax for process (CVE-2013-4311)
- Free slicename in virSystemdCreateMachine (rhbz#1008619)
- qemu: Fix checking of ABI stability when restoring external checkpoints (rhbz#1008340)
- qemu: Use "migratable" XML definition when doing external checkpoints (rhbz#1008340)
- qemu: Fix memleak after commit 59898a88ce8431bd3ea249b8789edc2ef9985827 (rhbz#1008340)
- qemu: Avoid dangling job in qemuDomainSetBlockIoTune (rhbz#700443)

* Sat Sep 14 2013 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-5
- Pass AM_LDFLAGS to driver modules too (rhbz#1006299)
- virsh domjobinfo: Do not return 1 if job is NONE (rhbz#1006864)
- Fix polkit permission names for storage pools, vols & node devices (rhbz#700443)
- Fix naming of permission for detecting storage pools (rhbz#700443)
- security: Provide supplemental groups even when parsing label (CVE-2013-4291) (rhbz#1006513)
- virFileNBDDeviceAssociate: Avoid use of uninitialized variable (CVE-2013-4297)
- Rename "struct interface_driver" to virNetcfDriverState (rhbz#983026)
- netcf driver: Use a single netcf handle for all connections (rhbz#983026)
- virDomainDefParseXML: Set the argument of virBitmapFree to NULL after calling virBitmapFree (rhbz#1006722)
- Add test for the nodemask double free crash (rhbz#1006722)
- qemu: Fix checking of guest ABI compatibility when reverting snapshots (rhbz#1006886)

* Fri Sep  6 2013 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-4
- Don't crash in qemuBuildDeviceAddressStr (rhbz#1003526)
- Fix leaks in python bindings (rhbz#1003828)
- Process virtlockd.conf instead of libvirtd.conf (rhbz#1003685)
- test_virtlockd.aug.in: Use the correct file (rhbz#1003685)
- qemu: Make domain renaming work during migration (rhbz#999352)
- qemu: Handle huge number of queues correctly (rhbz#651941)
- conf: Remove the actual hostdev when removing a network (rhbz#1003537)
- conf: Don't deref NULL actual network in virDomainNetGetActualHostdev() (rhbz#1003537)
- python: Fix a PyList usage mistake (rhbz#1002558)
- Add '<nat>' element to '<forward>' network schemas (rhbz#1004364)
- Always specify qcow2 compat level on qemu-img command line (rhbz#997977)
- selinux: Distinguish failure to label from request to avoid label (rhbz#924153)
- selinux: Enhance test to cover nfs label failure (rhbz#924153)

* Fri Aug 30 2013 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-3
- RPC: Don't accept client if it would overcommit max_clients (rhbz#981729)
- Introduce max_queued_clients (rhbz#981729)
- conf: Add default USB controller in qemu post-parse callback (rhbz#819968)
- qemu: Rename some functions in qemu_command.c (rhbz#819968)
- qemu: Eliminate almost-duplicate code in qemu_command.c (rhbz#819968)
- qemu: Enable auto-allocate of all PCI addresses (rhbz#819968)
- qemu: Add pcie-root controller (rhbz#819968)
- qemu: Add dmi-to-pci-bridge controller (rhbz#819968)
- qemu: Fix handling of default/implicit devices for q35 (rhbz#819968)
- qemu: Properly set/use device alias for pci controllers (rhbz#819968)
- qemu: Enable using implicit sata controller in q35 machines (rhbz#819968)
- qemu: Improve error reporting during PCI address validation (rhbz#819968)
- qemu: Refactor qemuDomainCheckDiskPresence for only disk presence check (rhbz#910171)
- qemu: Add helper functions for diskchain checking (rhbz#910171)
- qemu: Check presence of each disk and its backing file as well (rhbz#910171)
- conf: Add startupPolicy attribute for harddisk (rhbz#910171)
- qemu: Support to drop disk with 'optional' startupPolicy (rhbz#910171)
- Split TLS test into two separate tests (rhbz#994158)
- Avoid re-generating certs every time (rhbz#994158)
- Change data passed into TLS test cases (rhbz#994158)
- Fix validation of CA certificate chains (rhbz#994158)
- Fix parallel runs of TLS test suites (rhbz#994158)
- tests: Fix parallel runs of TLS test suites (rhbz#994158)
- Add a man page for virtlockd daemon (rhbz#991494)
- Add an example config file for virtlockd (rhbz#991494)
- Properly handle -h / -V for --help/--version aliases in virtlockd/libvirtd (rhbz#991494)
- Make check for /dev/loop device names stricter to avoid /dev/loop-control (rhbz#924815)
- Ensure securityfs is mounted readonly in container (rhbz#872642)
- Add info about access control checks into API reference (rhbz#700443)
- Record the where the auto-generated data comes from (rhbz#700443)
- Add documentation for access control system (rhbz#700443)
- virsh-domain: Flip logic in cmdSetvcpus (rhbz#996552)
- Honour root prefix in lxcContainerMountFSBlockAuto (rhbz#924815)
- util: Add virGetUserDirectoryByUID (rhbz#988491)
- Introduce a virt-login-shell binary (rhbz#988491)
- build: Fix compilation of virt-login-shell.c (rhbz#988491)
- Fix double-free and broken logic in virt-login-shell (rhbz#988491)
- Address missed feedback from review of virt-login-shell (rhbz#988491)
- Ensure that /dev exists in the container root filesystem (rhbz#924815)
- remote: Fix a segfault in remoteDomainCreateWithFlags (rhbz#994855)
- build: Avoid -lgcrypt with newer gnutls (rhbz#951637)
- virnettlscontext: Resolve Coverity warnings (UNINIT) (rhbz#994158)
- build: Fix missing max_queued_clients in augeas test file for libvirtd.conf (rhbz#981729)
- virsh-domain: Fix memleak in cmdCPUBaseline (rhbz#997798)
- Fix typo in domain name in polkit acl example (rhbz#700443)
- Update polkit examples to use 'lookup' method (rhbz#700443)
- Add bounds checking on virDomainMigrate*Params RPC calls (CVE-2013-4292) (rhbz#1002667)
- Add bounds checking on virDomainGetJobStats RPC call (rhbz#1002667)
- Add bounds checking on virDomain{SnapshotListAllChildren, ListAllSnapshots} RPC calls (rhbz#1002667)
- Add bounds checking on virConnectListAllDomains RPC call (rhbz#1002667)
- Add bounds checking on virConnectListAllStoragePools RPC call (rhbz#1002667)
- Add bounds checking on virStoragePoolListAllVolumes RPC call (rhbz#1002667)
- Add bounds checking on virConnectListAllNetworks RPC call (rhbz#1002667)
- Add bounds checking on virConnectListAllInterfaces RPC call (rhbz#1002667)
- Add bounds checking on virConnectListAllNodeDevices RPC call (rhbz#1002667)
- Add bounds checking on virConnectListAllNWFilters RPC call (rhbz#1002667)
- Add bounds checking on virConnectListAllSecrets RPC call (rhbz#1002667)
- Prohibit unbounded arrays in XDR protocols (rhbz#1002667)
- virbitmap: Refactor virBitmapParse to avoid access beyond bounds of array (rhbz#997906)
- virbitmaptest: Fix function header formatting (rhbz#997906)
- virbitmaptest: Add test for out of bounds condition (rhbz#997906)
- virsh-domain: Fix memleak in cmdUndefine with storage (rhbz#999057)
- virsh: Modify vshStringToArray to duplicate the elements too (rhbz#999057)
- virsh: Don't leak list of volumes when undefining domain with storage (rhbz#999057)
- Fix URI connect precedence (rhbz#999323)
- tests: Add URI precedence checking (rhbz#999323)
- Don't free NULL network in cmdNetworkUpdate (rhbz#1001094)
- virsh: Fix debugging (rhbz#1001628)
- qemu: Remove hostdev entry when freeing the depending network entry (rhbz#1002669)
- Set security label on FD for virDomainOpenGraphics (rhbz#999925)
- virsh: Free the caps list properly if one of them is invalid (rhbz#1001957)
- virsh: Free the formatting string when listing pool details (rhbz#1001957)
- virsh-pool.c: Don't jump over variable declaration (rhbz#1001957)
- virsh: Free the list from ListAll APIs even for 0 items (rhbz#1001957)
- virsh: Free messages after logging them to a file (rhbz#1001957)
- Reverse logic allowing partial DHCP host XML (rhbz#1001078)
- virsh: Print cephx and iscsi usage (rhbz#1000155)
- qemu_conf: Fix broken logic for adding passthrough iscsi lun (rhbz#1000159)
- Report secret usage error message similarly (rhbz#1000168)
- docs: Update the formatdomain disk examples (rhbz#1000169)
- docs: Update formatsecrets to include more examples of each type (rhbz#1000169)
- docs: Update iSCSI storage pool example (rhbz#1000169)
- docs: Reformat <disk> attribute description in formatdomain (rhbz#1000169)
- qemuBuildNicDevStr: Add mq=on for multiqueue networking (rhbz#651941)
- migration: Do not restore labels on failed migration (rhbz#822052)
- qemu: Drop qemuDomainMemoryLimit (rhbz#1001143)
- docs: Discourage users to set hard_limit (rhbz#1001143)
- docs: Clean 09adfdc62de2b up (rhbz#1001143)
- qemuSetupMemoryCgroup: Handle hard_limit properly (rhbz#1001143)
- qemuBuildCommandLine: Fall back to mem balloon if there's no hard_limit (rhbz#1001143)
- qemuDomainAttachHostPciDevice: Fall back to mem balloon if there's no hard_limit (rhbz#1001143)

* Fri Aug  2 2013 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-2
- spec: Change --enable-werror handling to match upstream
- Delete obsolete / unused python test files (rhbz#884103)
- Remove reference to python/tests from RPM %doc (rhbz#884103)
- spec: Explicitly claim ownership of channel subdir (rhbz#884103)
- Add APIs for formatting systemd slice/scope names (rhbz#980929)
- Add support for systemd cgroup mount (rhbz#980929)
- Cope with races while killing processes (rhbz#980929)
- Enable support for systemd-machined in cgroups creation (rhbz#980929)
- Ensure LXC/QEMU APIs set the filename for errors (rhbz#991348)
- Avoid crash if NULL is passed for filename/funcname in logging (rhbz#991348)

* Tue Jul 30 2013 Jiri Denemark <jdenemar@redhat.com> - 1.1.1-1
- Rebased to libvirt-1.1.1

* Fri Jul 12 2013 Jiri Denemark <jdenemar@redhat.com> - 1.1.0-2
- qemu: Fix double free in qemuMigrationPrepareDirect (rhbz#977961)
- Fix crash when multiple event callbacks were registered (CVE-2013-2230)
- Paused domain should remain paused after migration (rhbz#981139)

* Mon Jul  1 2013 Jiri Denemark <jdenemar@redhat.com> - 1.1.0-1
- Rebased to libvirt-1.1.0

* Mon Jun  3 2013 Jiri Denemark <jdenemar@redhat.com> - 1.0.6-1
- Rebased to libvirt-1.0.6

* Mon May 13 2013 Jiri Denemark <jdenemar@redhat.com> - 1.0.5-2
- virInitctlRequest: Don't hardcode 384 bytes size
- network: Fix network driver startup for qemu:///session
- virInitctlRequest: Unbreak make syntax check
- virInitctlRequest: Unbreak make syntax check
- build: Always include sanitytest in tarball
- qemu: Fix stupid typos in VFIO cgroup setup/teardown
- build: Always include libvirt_lxc.syms in tarball
- build: Clean up stray files found by 'make distcheck'
- spec: Proper soft static allocation of qemu uid
- Fix F_DUPFD_CLOEXEC operation args
- build: Fix mingw build of virprocess.c
- Fix potential use of undefined variable in remote dispatch code
- build: Avoid non-portable cast of pthread_t
- Fix release of resources with lockd plugin
- Fixup rpcgen code on kFreeBSD too
- Make detect_scsi_host_caps a function on all architectures
- qemu: Allocate network connections sooner during domain startup
- tests: Files named '.*-invalid.xml' should fail validation
- conf: Don't crash on a tpm device with no backends
- Don't mention disk controllers in generic controller errors
- iscsi: Don't leak portal string when starting a pool
- util: Fix virFileOpenAs return value and resulting error logs

* Thu May  2 2013 Jiri Denemark <jdenemar@redhat.com> - 1.0.5-1
- Rebased to libvirt-1.0.5

* Fri Apr 19 2013 Daniel Mach <dmach@redhat.com> - 1.0.4-1.1
- Rebuild for cyrus-sasl

* Mon Apr  8 2013 Jiri Denemark <jdenemar@redhat.com> - 1.0.4-1
- Rebased to libvirt-1.0.4

* Mon Apr 08 2013 Richard W.M. Jones <rjones@redhat.com> - 1.0.3-2
- Rebuild against gnutls 3.

* Tue Mar  5 2013 Jiri Denemark <jdenemar@redhat.com> - 1.0.3-1
- Rebased to libvirt-1.0.3

* Thu Jan 31 2013 Jiri Denemark <jdenemar@redhat.com> - 1.0.2-1
- Rebased to libvirt-1.0.2

* Tue Dec 18 2012 Jiri Denemark <jdenemar@redhat.com> - 1.0.1-1
- Rebased to libvirt-1.0.1

* Wed Nov 14 2012 Jiri Denemark <jdenemar@redhat.com> - 1.0.0-1
- Rebased to libvirt-1.0.0

* Tue Oct 30 2012 Cole Robinson <crobinso@redhat.com> - 0.10.2.1-2
- Disable libxl on F18 too

* Sat Oct 27 2012 Cole Robinson <crobinso@redhat.com> - 0.10.2.1-1
- Rebased to version 0.10.2.1
- Fix lvm volume creation when alloc=0 (bz #866481)
- Clarify virsh send-keys man page example (bz #860004)
- Fix occasional deadlock via virDomainDestroy (bz #859009)
- Fix LXC deadlock from ctrl-c (bz #848119)
- Fix occasional selinux denials with macvtap (bz #798605)
- Fix multilib conflict with systemtap files (bz #831425)
- Don't trigger keytab warning in system logs (bz #745203)
- Fix qemu domxml-2-native NIC model out (bz #636832)
- Fix error message if not enough space for lvm vol (bz #609104)

* Thu Oct 25 2012 Cole Robinson <crobinso@redhat.com> - 0.10.2-4
- Disable libxl driver, since it doesn't build with xen 4.2 in rawhide

* Mon Sep 24 2012 Richard W.M. Jones <rjones@redhat.com> - 0.10.2-3
- Re-add Use-qemu-system-i386-as-binary-instead-of-qemu.patch
  NB: This patch is Fedora-specific and not upstream.
- Add upstream patches: don't duplicate environment variables (RHBZ#859596).

* Mon Sep 24 2012 Daniel Veillard <veillard@redhat.com> - 0.10.2-1
- Upstream release 0.10.2
- network: define new API virNetworkUpdate
- add support for QEmu sandbox support
- blockjob: add virDomainBlockCommit
- New APIs to get/set Node memory parameters
- new API virConnectListAllSecrets
- new API virConnectListAllNWFilters
- new API virConnectListAllNodeDevices
- parallels: add support of containers to the driver
- new API virConnectListAllInterfaces
- new API virConnectListAllNetworks
- new API virStoragePoolListAllVolumes
- Add PMSUSPENDED life cycle event
- new API virStorageListAllStoragePools
- Add per-guest S3/S4 state configuration
- qemu: Support for Block Device IO Limits
- a lot of bug fixes, improvements and portability work

* Fri Sep 21 2012 Richard W.M. Jones <rjones@redhat.com> - 0.10.1-5
- Add (upstream) patches to label sockets for SELinux (RHBZ#853393).

* Thu Sep 13 2012 Richard W.M. Jones <rjones@redhat.com> - 0.10.1-4
- Fix for 32 bit qemu renamed to qemu-system-i386 (RHBZ#857026).

* Wed Sep 12 2012 Cole Robinson <crobinso@redhat.com> - 0.10.1-3
- Fix libvirtd segfault with old netcf-libs (bz 853381)
- Drop unneeded dnsmasq --filterwin2k
- Fix unwanted connection closing, needed for boxes

* Wed Sep  5 2012 Daniel P. Berrange <berrange@redhat.com> - 0.10.1-2
- Remove dep on ceph RPM (rhbz #854360)

* Fri Aug 31 2012 Daniel Veillard <veillard@redhat.com> - 0.10.1-1
- upstream release of 0.10.1
- many fixes from 0.10.0

* Wed Aug 29 2012 Daniel Veillard <veillard@redhat.com> - 0.10.0-1
- upstream release of 0.10.0
- agent: add qemuAgentArbitraryCommand() for general qemu agent command
- Introduce virDomainPinEmulator and virDomainGetEmulatorPinInfo functions
- network: use firewalld instead of iptables, when available
- network: make network driver vlan-aware
- esx: Implement network driver
- driver for parallels hypervisor
- Various LXC improvements
- Add virDomainGetHostname
- a lot of bug fixes, improvements and portability work

* Thu Aug 23 2012 Daniel Veillard <veillard@redhat.com> - 0.10.0-0rc1
- release candidate 1 of 0.10.0

* Tue Aug 14 2012 Daniel P. Berrange <berrange@redhat.com> - 0.10.0-0rc0.2
- Enable autotools to make previous patch work

* Tue Aug 14 2012 Daniel Veillard <veillard@redhat.com> - 0.10.0-0rc0.1
- fix security driver missing from the daemon

* Wed Aug  8 2012 Daniel Veillard <veillard@redhat.com> - 0.10.0-0rc0
- snapshot before 0.10.0 in a few weeks
- adds the parallel driver support

* Mon Jul 23 2012 Richard W.M. Jones <rjones@redhat.com> - 0.9.13-3
- Add upstream patch to fix RHBZ#842114.

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.13-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Mon Jul  2 2012 Daniel Veillard <veillard@redhat.com> - 0.9.13-1
- S390: support for s390(x)
- snapshot: implement new APIs for esx and vbox
- snapshot: new query APIs and many improvements
- virsh: Allow users to reedit rejected XML
- nwfilter: add DHCP snooping
- Enable driver modules in libvirt RPM
- Default to enable driver modules for libvirtd
- storage backend: Add RBD (RADOS Block Device) support
- sVirt support for LXC domains inprovement
- a lot of bug fixes, improvements and portability work

* Mon May 14 2012 Daniel Veillard <veillard@redhat.com> - 0.9.12-1
- qemu: allow snapshotting of sheepdog and rbd disks
- blockjob: add new APIs
- a lot of bug fixes, improvements and portability work

* Thu Apr 26 2012 Cole Robinson <crobinso@redhat.com> - 0.9.11.3-1
- Rebased to version 0.9.11.3
- Abide URI username when connecting to hypervisor (bz 811397)
- Fix managed USB mode (bz 814866)
- Fix crash connecting to ESX host (bz 811891)

* Wed Apr  4 2012 Daniel P. Berrange <berrange@redhat.com> - 0.9.11-1
- Update to 0.9.11 release

* Tue Apr  3 2012 Daniel P. Berrange <berrange@redhat.com> - 0.9.10-4
- Revert previous change

* Sat Mar 31 2012 Daniel P. Berrange <berrange@redhat.com> - 0.9.10-3
- Refactor RPM spec to allow install without default configs

* Thu Mar 15 2012 Daniel P. Berrange <berrange@redhat.com> - 0.9.10-2
- Rebuild for libparted soname break

* Mon Feb 13 2012 Daniel P. Berrange <berrange@redhat.com> - 0.9.10-1
- Update to 0.9.10

* Thu Jan 12 2012 Daniel P. Berrange <berrange@redhat.com> - 0.9.9-2
- Fix LXC I/O handling

* Sat Jan  7 2012 Daniel Veillard <veillard@redhat.com> - 0.9.9-1
- Add API virDomain{S,G}etInterfaceParameters
- Add API virDomain{G, S}etNumaParameters
- Add support for ppc64 qemu
- Support Xen domctl v8
- many improvements and bug fixes

* Thu Dec  8 2011 Daniel P. Berrange <berrange@redhat.com> - 0.9.8-2
- Fix install of libvirt-guests.service & libvirtd.service

* Thu Dec  8 2011 Daniel Veillard <veillard@redhat.com> - 0.9.8-1
- Add support for QEMU 1.0
- Add preliminary PPC cpu driver
- Add new API virDomain{Set, Get}BlockIoTune
- block_resize: Define the new API
- Add a public API to invoke suspend/resume on the host
- various improvements for LXC containers
- Define keepalive protocol and add virConnectIsAlive API
- Add support for STP and VLAN filtering
- many improvements and bug fixes

* Mon Nov 14 2011 Justin M. Forbes <jforbes@redhat.com> - 0.9.7-3
- Remove versioned buildreq for yajl as 2.0.x features are not required.

* Thu Nov 10 2011 Daniel P. Berrange <berrange@redhat.com> - 0.9.7-2
- Rebuild for yajl 2.0.1

* Tue Nov  8 2011 Daniel P. Berrange <berrange@redhat.com> - 0.9.7-1
- Update to 0.9.7 release

* Tue Oct 11 2011 Dan Horák <dan[at]danny.cz> - 0.9.6-3
- xenlight available only on Xen arches (#745020)

* Mon Oct  3 2011 Laine Stump <laine@redhat.com> - 0.9.6-2
- Make PCI multifunction support more manual - Bug 742836
- F15 build still uses cgconfig - Bug 738725

* Thu Sep 22 2011 Daniel Veillard <veillard@redhat.com> - 0.9.6-1
- Fix the qemu reboot bug and a few others bug fixes

* Tue Sep 20 2011 Daniel Veillard <veillard@redhat.com> - 0.9.5-1
- many snapshot improvements (Eric Blake)
- latency: Define new public API and structure (Osier Yang)
- USB2 and various USB improvements (Marc-André Lureau)
- storage: Add fs pool formatting (Osier Yang)
- Add public API for getting migration speed (Jim Fehlig)
- Add basic driver for Microsoft Hyper-V (Matthias Bolte)
- many improvements and bug fixes

* Wed Aug  3 2011 Daniel Veillard <veillard@redhat.com> - 0.9.4-1
- network bandwidth QoS control
- Add new API virDomainBlockPull*
- save: new API to manipulate save file images
- CPU bandwidth limits support
- allow to send NMI and key event to guests
- new API virDomainUndefineFlags
- Implement code to attach to external QEMU instances
- bios: Add support for SGA
- various missing python binding
- many improvements and bug fixes

* Sat Jul 30 2011 Dan Hor?k <dan[at]danny.cz> - 0.9.3-3
- xenlight available only on Xen arches

* Wed Jul  6 2011 Peter Robinson <pbrobinson@gmail.com> - 0.9.3-2
- Add ARM to NUMA platform excludes

* Mon Jul  4 2011 Daniel Veillard <veillard@redhat.com> - 0.9.3-1
- new API virDomainGetVcpupinInfo
- Add TXT record support for virtual DNS service
- Support reboots with the QEMU driver
- New API virDomainGetControlInfo API
- New API virNodeGetMemoryStats
- New API virNodeGetCPUTime
- New API for send-key
- New API virDomainPinVcpuFlags
- support multifunction PCI device
- lxc: various improvements
- many improvements and bug fixes

* Wed Jun 29 2011 Richard W.M. Jones <rjones@redhat.com> - 0.9.2-3
- Rebuild because of libparted soname bump (libparted.so.0 -> libparted.so.1).

* Tue Jun 21 2011 Laine Stump <laine@redhat.com> - 0.9.2-2
- add rule to require netcf-0.1.8 during build so that new transactional
  network change APIs are included.
- document that CVE-2011-2178 has been fixed (by virtue of rebase
  to 0.9.2 - see https://bugzilla.redhat.com/show_bug.cgi?id=709777)

* Mon Jun  6 2011 Daniel Veillard <veillard@redhat.com> - 0.9.2-1
- Framework for lock manager plugins
- API for network config change transactions
- flags for setting memory parameters
- virDomainGetState public API
- qemu: allow blkstat/blkinfo calls during migration
- Introduce migration v3 API
- Defining the Screenshot public API
- public API for NMI injection
- Various improvements and bug fixes

* Wed May 25 2011 Richard W.M. Jones <rjones@redhat.com> - 0.9.1-3
- Add upstream patches:
    0001-json-Avoid-passing-large-positive-64-bit-integers-to.patch
    0001-qemudDomainMemoryPeek-change-ownership-selinux-label.patch
    0002-remote-remove-bogus-virDomainFree.patch
  so that users can try out virt-dmesg.
- Change /var/cache mode to 0711.

* Thu May  5 2011 Daniel Veillard <veillard@redhat.com> - 0.9.1-1
- support various persistent domain updates
- improvements on memory APIs
- Add virDomainEventRebootNew
- various improvements to libxl driver
- Spice: support audio, images and stream compression
- Various improvements and bug fixes

* Thu Apr  7 2011 Daniel Veillard <veillard@redhat.com> - 0.9.0-1
- Support cputune cpu usage tuning
- Add public APIs for storage volume upload/download
- Add public API for setting migration speed on the fly
- Add libxenlight driver
- qemu: support migration to fd
- libvirt: add virDomain{Get,Set}BlkioParameters
- setmem: introduce a new libvirt API (virDomainSetMemoryFlags)
- Expose event loop implementation as a public API
- Dump the debug buffer to libvirtd.log on fatal signal
- Audit support
- Various improvements and bug fixes

* Mon Mar 14 2011 Daniel Veillard <veillard@redhat.com> - 0.8.8-3
- fix a lack of API check on read-only connections
- CVE-2011-1146

* Mon Feb 21 2011 Daniel P. Berrange <berrange@redhat.com> - 0.8.8-2
- Fix kernel boot with latest QEMU

* Thu Feb 17 2011 Daniel Veillard <veillard@redhat.com> - 0.8.8-1
- expose new API for sysinfo extraction
- cgroup blkio weight support
- smartcard device support
- qemu: Support per-device boot ordering
- Various improvements and bug fixes

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.8.7-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Thu Jan  6 2011 Daniel Veillard <veillard@redhat.com> - 0.8.7-1
- Preliminary support for VirtualBox 4.0
- IPv6 support
- Add VMware Workstation and Player driver driver
- Add network disk support
- Various improvements and bug fixes
- from 0.8.6:
- Add support for iSCSI target auto-discovery
- QED: Basic support for QED images
- remote console support
- support for SPICE graphics
- sysinfo and VMBIOS support
- virsh qemu-monitor-command
- various improvements and bug fixes

* Fri Oct 29 2010 Daniel Veillard <veillard@redhat.com> - 0.8.5-1
- Enable JSON and netdev features in QEMU >= 0.13
- framework for auditing integration
- framework DTrace/SystemTap integration
- Setting the number of vcpu at boot
- Enable support for nested SVM
- Virtio plan9fs filesystem QEMU
- Memory parameter controls
- various improvements and bug fixes

* Wed Sep 29 2010 jkeating - 0.8.4-3
- Rebuilt for gcc bug 634757

* Thu Sep 16 2010 Dan Horák <dan[at]danny.cz> - 0.8.4-2
- disable the nwfilterxml2xmltest also on s390(x)

* Mon Sep 13 2010 Daniel Veillard <veillard@redhat.com> - 0.8.4-1
- Upstream release 0.8.4

* Mon Aug 23 2010 Daniel P. Berrange <berrange@redhat.com> - 0.8.3-2
- Fix potential overflow in boot menu code

* Mon Aug 23 2010 Daniel P. Berrange <berrange@redhat.com> - 0.8.3-1
- Upstream release 0.8.3

* Wed Jul 21 2010 David Malcolm <dmalcolm@redhat.com> - 0.8.2-3
- Rebuilt for https://fedoraproject.org/wiki/Features/Python_2.7/MassRebuild

* Mon Jul 12 2010 Daniel P. Berrange <berrange@redhat.com> - 0.8.2-2
- CVE-2010-2237 ignoring defined main disk format when looking up disk backing stores
- CVE-2010-2238 ignoring defined disk backing store format when recursing into disk
  image backing stores
- CVE-2010-2239 not setting user defined backing store format when creating new image
- CVE-2010-2242 libvirt: improperly mapped source privileged ports may allow for
  obtaining privileged resources on the host

* Mon Jul  5 2010 Daniel Veillard <veillard@redhat.com> - 0.8.2-1
- Upstream release 0.8.2
- phyp: adding support for IVM
- libvirt: introduce domainCreateWithFlags API
- add 802.1Qbh and 802.1Qbg switches handling
- Support for VirtualBox version 3.2
- Init script for handling guests on shutdown/boot
- qemu: live migration with non-shared storage for kvm

* Fri Apr 30 2010 Daniel Veillard <veillard@redhat.com> - 0.8.1-1
- Upstream release 0.8.1
- Starts dnsmasq from libvirtd with --dhcp-hostsfile
- Add virDomainGetBlockInfo API to query disk sizing
- a lot of bug fixes and cleanups

* Mon Apr 12 2010 Daniel Veillard <veillard@redhat.com> - 0.8.0-1
- Upstream release 0.8.0
- Snapshotting support (QEmu/VBox/ESX)
- Network filtering API
- XenAPI driver
- new APIs for domain events
- Libvirt managed save API
- timer subselection for domain clock
- synchronous hooks
- API to update guest CPU to host CPU
- virDomainUpdateDeviceFlags new API
- migrate max downtime API
- volume wiping API
- and many bug fixes

* Tue Mar 30 2010 Richard W.M. Jones <rjones@redhat.com> - 0.7.7-3.fc14
- No change, just rebuild against new libparted with bumped soname.

* Mon Mar 22 2010 Cole Robinson <crobinso@redhat.com> - 0.7.7-2.fc14
- Fix USB devices by product with security enabled (bz 574136)
- Set kernel/initrd in security driver, fixes some URL installs (bz 566425)

* Fri Mar  5 2010 Daniel Veillard <veillard@redhat.com> - 0.7.7-1
- macvtap support
- async job handling
- virtio channel
- computing baseline CPU
- virDomain{Attach,Detach}DeviceFlags
- assorted bug fixes and lots of cleanups

* Tue Feb 16 2010 Adam Jackson <ajax@redhat.com> 0.7.6-2
- libvirt-0.7.6-add-needed.patch: Fix FTBFS from --no-add-needed
- Add BuildRequires: xmlrpc-c-client for libxmlrpc_client.so

* Wed Feb  3 2010 Daniel Veillard <veillard@redhat.com> - 0.7.6-1
- upstream release of 0.7.6
- Use QEmu new device adressing when possible
- Implement CPU topology support for QEMU driver
- Implement SCSI controller hotplug/unplug for QEMU
- Implement support for multi IQN
- a lot of fixes and improvements

* Thu Jan 14 2010 Chris Weyl <cweyl@alumni.drew.edu> 0.7.5-3
- bump for libssh2 rebuild

* Tue Jan 12 2010 Daniel P. Berrange <berrange@redhat.com> - 0.7.5-2
- Rebuild for libparted soname change

* Wed Dec 23 2009 Daniel Veillard <veillard@redhat.com> - 0.7.5-1
- Add new API virDomainMemoryStats
- Public API and domain extension for CPU flags
- vbox: Add support for version 3.1
- Support QEMU's virtual FAT block device driver
- a lot of fixes

* Fri Nov 20 2009 Daniel Veillard <veillard@redhat.com> - 0.7.4-1
- upstream release of 0.7.4
- udev node device backend
- API to check object properties
- better QEmu monitor processing
- MAC address based port filtering for qemu
- support IPv6 and multiple addresses per interfaces
- a lot of fixes

* Thu Nov 19 2009 Daniel P. Berrange <berrange@redhat.com> - 0.7.2-6
- Really fix restore file labelling this time

* Wed Nov 11 2009 Daniel P. Berrange <berrange@redhat.com> - 0.7.2-5
- Disable numactl on s390[x]. Again.

* Wed Nov 11 2009 Daniel P. Berrange <berrange@redhat.com> - 0.7.2-4
- Fix QEMU save/restore permissions / labelling

* Thu Oct 29 2009 Mark McLoughlin <markmc@redhat.com> - 0.7.2-3
- Avoid compressing small log files (#531030)

* Thu Oct 29 2009 Mark McLoughlin <markmc@redhat.com> - 0.7.2-2
- Make libvirt-devel require libvirt-client, not libvirt
- Fix qemu machine types handling

* Wed Oct 14 2009 Daniel Veillard <veillard@redhat.com> - 0.7.2-1
- Upstream release of 0.7.2
- Allow to define ESX domains
- Allows suspend and resulme of LXC domains
- API for data streams
- many bug fixes

* Tue Oct 13 2009 Mark McLoughlin <markmc@redhat.com> - 0.7.1-12
- Fix restore of qemu guest using raw save format (#523158)

* Fri Oct  9 2009 Mark McLoughlin <markmc@redhat.com> - 0.7.1-11
- Fix libvirtd memory leak during error reply sending (#528162)
- Add several PCI hot-unplug typo fixes from upstream

* Tue Oct  6 2009 Mark McLoughlin <markmc@redhat.com> - 0.7.1-10
- Create /var/log/libvirt/{lxc,uml} dirs for logrotate
- Make libvirt-python dependon on libvirt-client
- Sync misc minor changes from upstream spec

* Tue Oct  6 2009 Mark McLoughlin <markmc@redhat.com> - 0.7.1-9
- Change logrotate config to weekly (#526769)

* Thu Oct  1 2009 Mark McLoughlin <markmc@redhat.com> - 0.7.1-8
- Disable sound backend, even when selinux is disabled (#524499)
- Re-label qcow2 backing files (#497131)

* Wed Sep 30 2009 Mark McLoughlin <markmc@redhat.com> - 0.7.1-7
- Fix USB device passthrough (#522683)

* Mon Sep 21 2009 Chris Weyl <cweyl@alumni.drew.edu> - 0.7.1-6
- rebuild for libssh2 1.2

* Mon Sep 21 2009 Mark McLoughlin <markmc@redhat.com> - 0.7.1-5
- Don't set a bogus error in virDrvSupportsFeature()
- Fix raw save format

* Thu Sep 17 2009 Mark McLoughlin <markmc@redhat.com> - 0.7.1-4
- A couple of hot-unplug memory handling fixes (#523953)

* Thu Sep 17 2009 Daniel Veillard <veillard@redhat.com> - 0.7.1-3
- disable numactl on s390[x]

* Thu Sep 17 2009 Daniel Veillard <veillard@redhat.com> - 0.7.1-2
- revamp of spec file for modularity and RHELs

* Tue Sep 15 2009 Daniel Veillard <veillard@redhat.com> - 0.7.1-1
- Upstream release of 0.7.1
- ESX, VBox driver updates
- mutipath support
- support for encrypted (qcow) volume
- compressed save image format for Qemu/KVM
- QEmu host PCI device hotplug support
- configuration of huge pages in guests
- a lot of fixes

* Mon Sep 14 2009 Mark McLoughlin <markmc@redhat.com> - 0.7.1-0.2.gitfac3f4c
- Update to newer snapshot of 0.7.1
- Stop libvirt using untrusted 'info vcpus' PID data (#520864)
- Support relabelling of USB and PCI devices
- Enable multipath storage support
- Restart libvirtd upon RPM upgrade

* Sun Sep  6 2009 Mark McLoughlin <markmc@redhat.com> - 0.7.1-0.1.gitg3ef2e05
- Update to pre-release git snapshot of 0.7.1
- Drop upstreamed patches

* Wed Aug 19 2009 Mark McLoughlin <markmc@redhat.com> - 0.7.0-6
- Fix migration completion with newer versions of qemu (#516187)

* Wed Aug 19 2009 Mark McLoughlin <markmc@redhat.com> - 0.7.0-5
- Add PCI host device hotplug support
- Allow PCI bus reset to reset other devices (#499678)
- Fix stupid PCI reset error message (bug #499678)
- Allow PM reset on multi-function PCI devices (bug #515689)
- Re-attach PCI host devices after guest shuts down (bug #499561)
- Fix list corruption after disk hot-unplug
- Fix minor 'virsh nodedev-list --tree' annoyance

* Thu Aug 13 2009 Daniel P. Berrange <berrange@redhat.com> - 0.7.0-4
- Rewrite policykit support (rhbz #499970)
- Log and ignore NUMA topology problems (rhbz #506590)

* Mon Aug 10 2009 Mark McLoughlin <markmc@redhat.com> - 0.7.0-3
- Don't fail to start network if ipv6 modules is not loaded (#516497)

* Thu Aug  6 2009 Mark McLoughlin <markmc@redhat.com> - 0.7.0-2
- Make sure qemu can access kernel/initrd (bug #516034)
- Set perms on /var/lib/libvirt/boot to 0711 (bug #516034)

* Wed Aug  5 2009 Daniel Veillard <veillard@redhat.com> - 0.7.0-1
- ESX, VBox3, Power Hypervisor drivers
- new net filesystem glusterfs
- Storage cloning for LVM and Disk backends
- interface implementation based on netcf
- Support cgroups in QEMU driver
- QEmu hotplug NIC support
- a lot of fixes

* Fri Jul  3 2009 Daniel Veillard <veillard@redhat.com> - 0.6.5-1
- release of 0.6.5

* Fri May 29 2009 Daniel Veillard <veillard@redhat.com> - 0.6.4-1
- release of 0.6.4
- various new APIs

* Fri Apr 24 2009 Daniel Veillard <veillard@redhat.com> - 0.6.3-1
- release of 0.6.3
- VirtualBox driver

* Fri Apr  3 2009 Daniel Veillard <veillard@redhat.com> - 0.6.2-1
- release of 0.6.2

* Wed Mar  4 2009 Daniel Veillard <veillard@redhat.com> - 0.6.1-1
- release of 0.6.1

* Sat Jan 31 2009 Daniel Veillard <veillard@redhat.com> - 0.6.0-1
- release of 0.6.0

* Tue Nov 25 2008 Daniel Veillard <veillard@redhat.com> - 0.5.0-1
- release of 0.5.0

* Tue Sep 23 2008 Daniel Veillard <veillard@redhat.com> - 0.4.6-1
- release of 0.4.6

* Mon Sep  8 2008 Daniel Veillard <veillard@redhat.com> - 0.4.5-1
- release of 0.4.5

* Wed Jun 25 2008 Daniel Veillard <veillard@redhat.com> - 0.4.4-1
- release of 0.4.4
- mostly a few bug fixes from 0.4.3

* Thu Jun 12 2008 Daniel Veillard <veillard@redhat.com> - 0.4.3-1
- release of 0.4.3
- lots of bug fixes and small improvements

* Tue Apr  8 2008 Daniel Veillard <veillard@redhat.com> - 0.4.2-1
- release of 0.4.2
- lots of bug fixes and small improvements

* Mon Mar  3 2008 Daniel Veillard <veillard@redhat.com> - 0.4.1-1
- Release of 0.4.1
- Storage APIs
- xenner support
- lots of assorted improvements, bugfixes and cleanups
- documentation and localization improvements

* Tue Dec 18 2007 Daniel Veillard <veillard@redhat.com> - 0.4.0-1
- Release of 0.4.0
- SASL based authentication
- PolicyKit authentication
- improved NUMA and statistics support
- lots of assorted improvements, bugfixes and cleanups
- documentation and localization improvements

* Sun Sep 30 2007 Daniel Veillard <veillard@redhat.com> - 0.3.3-1
- Release of 0.3.3
- Avahi support
- NUMA support
- lots of assorted improvements, bugfixes and cleanups
- documentation and localization improvements

* Tue Aug 21 2007 Daniel Veillard <veillard@redhat.com> - 0.3.2-1
- Release of 0.3.2
- API for domains migration
- APIs for collecting statistics on disks and interfaces
- lots of assorted bugfixes and cleanups
- documentation and localization improvements

* Tue Jul 24 2007 Daniel Veillard <veillard@redhat.com> - 0.3.1-1
- Release of 0.3.1
- localtime clock support
- PS/2 and USB input devices
- lots of assorted bugfixes and cleanups
- documentation and localization improvements

* Mon Jul  9 2007 Daniel Veillard <veillard@redhat.com> - 0.3.0-1
- Release of 0.3.0
- Secure remote access support
- unification of daemons
- lots of assorted bugfixes and cleanups
- documentation and localization improvements

* Fri Jun  8 2007 Daniel Veillard <veillard@redhat.com> - 0.2.3-1
- Release of 0.2.3
- lot of assorted bugfixes and cleanups
- support for Xen-3.1
- new scheduler API

* Tue Apr 17 2007 Daniel Veillard <veillard@redhat.com> - 0.2.2-1
- Release of 0.2.2
- lot of assorted bugfixes and cleanups
- preparing for Xen-3.0.5

* Thu Mar 22 2007 Jeremy Katz <katzj@redhat.com> - 0.2.1-2.fc7
- don't require xen; we don't need the daemon and can control non-xen now
- fix scriptlet error (need to own more directories)
- update description text

* Fri Mar 16 2007 Daniel Veillard <veillard@redhat.com> - 0.2.1-1
- Release of 0.2.1
- lot of bug and portability fixes
- Add support for network autostart and init scripts
- New API to detect the virtualization capabilities of a host
- Documentation updates

* Fri Feb 23 2007 Daniel P. Berrange <berrange@redhat.com> - 0.2.0-4.fc7
- Fix loading of guest & network configs

* Fri Feb 16 2007 Daniel P. Berrange <berrange@redhat.com> - 0.2.0-3.fc7
- Disable kqemu support since its not in Fedora qemu binary
- Fix for -vnc arg syntax change in 0.9.0  QEMU

* Thu Feb 15 2007 Daniel P. Berrange <berrange@redhat.com> - 0.2.0-2.fc7
- Fixed path to qemu daemon for autostart
- Fixed generation of <features> block in XML
- Pre-create config directory at startup

* Wed Feb 14 2007 Daniel Veillard <veillard@redhat.com> 0.2.0-1.fc7
- support for KVM and QEmu
- support for network configuration
- assorted fixes

* Mon Jan 22 2007 Daniel Veillard <veillard@redhat.com> 0.1.11-1.fc7
- finish inactive Xen domains support
- memory leak fix
- RelaxNG schemas for XML configs

* Wed Dec 20 2006 Daniel Veillard <veillard@redhat.com> 0.1.10-1.fc7
- support for inactive Xen domains
- improved support for Xen display and vnc
- a few bug fixes
- localization updates

* Thu Dec  7 2006 Jeremy Katz <katzj@redhat.com> - 0.1.9-2
- rebuild against python 2.5

* Wed Nov 29 2006 Daniel Veillard <veillard@redhat.com> 0.1.9-1
- better error reporting
- python bindings fixes and extensions
- add support for shareable drives
- add support for non-bridge style networking
- hot plug device support
- added support for inactive domains
- API to dump core of domains
- various bug fixes, cleanups and improvements
- updated the localization

* Tue Nov  7 2006 Daniel Veillard <veillard@redhat.com> 0.1.8-3
- it's pkgconfig not pgkconfig !

* Mon Nov  6 2006 Daniel Veillard <veillard@redhat.com> 0.1.8-2
- fixing spec file, added %%dist, -devel requires pkgconfig and xen-devel
- Resolves: rhbz#202320

* Mon Oct 16 2006 Daniel Veillard <veillard@redhat.com> 0.1.8-1
- fix missing page size detection code for ia64
- fix mlock size when getting domain info list from hypervisor
- vcpu number initialization
- don't label crashed domains as shut off
- fix virsh man page
- blktapdd support for alternate drivers like blktap
- memory leak fixes (xend interface and XML parsing)
- compile fix
- mlock/munlock size fixes

* Fri Sep 22 2006 Daniel Veillard <veillard@redhat.com> 0.1.7-1
- Fix bug when running against xen-3.0.3 hypercalls
- Fix memory bug when getting vcpus info from xend

* Fri Sep 22 2006 Daniel Veillard <veillard@redhat.com> 0.1.6-1
- Support for localization
- Support for new Xen-3.0.3 cdrom and disk configuration
- Support for setting VNC port
- Fix bug when running against xen-3.0.2 hypercalls
- Fix reconnection problem when talking directly to http xend

* Tue Sep  5 2006 Jeremy Katz <katzj@redhat.com> - 0.1.5-3
- patch from danpb to support new-format cd devices for HVM guests

* Tue Sep  5 2006 Daniel Veillard <veillard@redhat.com> 0.1.5-2
- reactivating ia64 support

* Tue Sep  5 2006 Daniel Veillard <veillard@redhat.com> 0.1.5-1
- new release
- bug fixes
- support for new hypervisor calls
- early code for config files and defined domains

* Mon Sep  4 2006 Daniel Berrange <berrange@redhat.com> - 0.1.4-5
- add patch to address dom0_ops API breakage in Xen 3.0.3 tree

* Mon Aug 28 2006 Jeremy Katz <katzj@redhat.com> - 0.1.4-4
- add patch to support paravirt framebuffer in Xen

* Mon Aug 21 2006 Daniel Veillard <veillard@redhat.com> 0.1.4-3
- another patch to fix network handling in non-HVM guests

* Thu Aug 17 2006 Daniel Veillard <veillard@redhat.com> 0.1.4-2
- patch to fix virParseUUID()

* Wed Aug 16 2006 Daniel Veillard <veillard@redhat.com> 0.1.4-1
- vCPUs and affinity support
- more complete XML, console and boot options
- specific features support
- enforced read-only connections
- various improvements, bug fixes

* Wed Aug  2 2006 Jeremy Katz <katzj@redhat.com> - 0.1.3-6
- add patch from pvetere to allow getting uuid from libvirt

* Wed Aug  2 2006 Jeremy Katz <katzj@redhat.com> - 0.1.3-5
- build on ia64 now

* Thu Jul 27 2006 Jeremy Katz <katzj@redhat.com> - 0.1.3-4
- don't BR xen, we just need xen-devel

* Thu Jul 27 2006 Daniel Veillard <veillard@redhat.com> 0.1.3-3
- need rebuild since libxenstore is now versionned

* Mon Jul 24 2006 Mark McLoughlin <markmc@redhat.com> - 0.1.3-2
- Add BuildRequires: xen-devel

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 0.1.3-1.1
- rebuild

* Tue Jul 11 2006 Daniel Veillard <veillard@redhat.com> 0.1.3-1
- support for HVM Xen guests
- various bugfixes

* Mon Jul  3 2006 Daniel Veillard <veillard@redhat.com> 0.1.2-1
- added a proxy mechanism for read only access using httpu
- fixed header includes paths

* Wed Jun 21 2006 Daniel Veillard <veillard@redhat.com> 0.1.1-1
- extend and cleanup the driver infrastructure and code
- python examples
- extend uuid support
- bug fixes, buffer handling cleanups
- support for new Xen hypervisor API
- test driver for unit testing
- virsh --conect argument

* Mon Apr 10 2006 Daniel Veillard <veillard@redhat.com> 0.1.0-1
- various fixes
- new APIs: for Node information and Reboot
- virsh improvements and extensions
- documentation updates and man page
- enhancement and fixes of the XML description format

* Tue Feb 28 2006 Daniel Veillard <veillard@redhat.com> 0.0.6-1
- added error handling APIs
- small bug fixes
- improve python bindings
- augment documentation and regression tests

* Thu Feb 23 2006 Daniel Veillard <veillard@redhat.com> 0.0.5-1
- new domain creation API
- new UUID based APIs
- more tests, documentation, devhelp
- bug fixes

* Fri Feb 10 2006 Daniel Veillard <veillard@redhat.com> 0.0.4-1
- fixes some problems in 0.0.3 due to the change of names

* Wed Feb  8 2006 Daniel Veillard <veillard@redhat.com> 0.0.3-1
- changed library name to libvirt from libvir, complete and test the python
  bindings

* Sun Jan 29 2006 Daniel Veillard <veillard@redhat.com> 0.0.2-1
- upstream release of 0.0.2, use xend, save and restore added, python bindings
  fixed

* Wed Nov  2 2005 Daniel Veillard <veillard@redhat.com> 0.0.1-1
- created
