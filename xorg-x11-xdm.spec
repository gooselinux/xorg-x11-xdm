%define pkgname xdm

Summary: X.Org X11 xdm - X Display Manager
Name: xorg-x11-%{pkgname}
Version: 1.1.6
Release: 14.1%{?dist}
# NOTE: Remove Epoch line if/when the package ever gets renamed.
Epoch: 1
License: MIT
Group: User Interface/X
URL: http://www.x.org
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Source0: ftp://ftp.x.org/pub/individual/app/xdm-%{version}.tar.bz2
Source1: Xsetup_0
Source10: xdm.init
Source11: xdm.pamd

# NOTE: Change xdm-config to invoke Xwilling with "-s /bin/bash" instead
# of "-c" to fix bug (#86505)
Patch10: xdm-1.0.1-redhat-xdm-config-fix.patch
Patch11: xdm-1.0.5-sessreg-utmp-fix-bug177890.patch

# NOTE: Change authorization to be saved in /var/lib/xdm (for
# cooperating with SELinux, see bug 388431 for more info)
Patch12: xdm-1.1.6-authDir-var-bug388431.patch

# Fix missing #endif in the Xresources (#470348)
Patch13: xdm-1.1.6-redhat-Xresources-fix.patch

# FIXME: Temporary build dependencies for autotool dependence.
BuildRequires: autoconf, automake, libtool

BuildRequires: pkgconfig
BuildRequires: xorg-x11-util-macros
BuildRequires: xorg-x11-xtrans-devel
BuildRequires: libXaw-devel
BuildRequires: libXmu-devel
BuildRequires: libXt-devel
BuildRequires: libSM-devel
BuildRequires: libICE-devel
BuildRequires: libXext-devel
BuildRequires: libXpm-devel
BuildRequires: libX11-devel
# FIXME: There's no autotool dep on libXdmcp currently, but it fails with the
# following:
# configure: error: Library requirements (xdmcp) not met; consider adjusting
# the PKG_CONFIG_PATH environment variable if your libraries are in a
# nonstandard prefix so pkg-config can find them.
BuildRequires: libXdmcp-devel
# FIXME: There's no autotool specified dep on this currently, but everything
# explodes looking for X11/Xauth.h without it:
BuildRequires: libXau-devel
BuildRequires: libXinerama-devel
BuildRequires: pam-devel

Provides: xdm

Obsoletes: XFree86-xdm
Obsoletes: xinitrc

# NOTE: Support for the new audit system was added to rawhide in FC3/pam-0.77-10,
# requiring a change to xdm.pamd (bug #159332). Support for pam_stack.so was
# removed from pam, and replaced by a new mechanism in pam-0.78 and later,
# requiring additional changes to xdm.pamd. (bug #170661)
Requires: pam >= 0.78-0

# We want to use the system Xsession script
Requires: xorg-x11-xinit

%description
X.Org X11 xdm - X Display Manager

%prep
%setup -q -n %{pkgname}-%{version}

%patch10 -p0 -b .redhat-xdm-config-fix
%patch11 -p0 -b .redhat-sessreg-utmp-fix-bug177890
%patch12 -p1 -b .authDir-var-bug388431
%patch13 -p1 -b .redhat-xresources-bug470348

%build
export CFLAGS="$RPM_OPT_FLAGS -fno-strict-aliasing"
sed -i '/XAW_/ s/)/, xaw7)/; /XAW_/ s/XAW_CHECK_XPRINT_SUPPORT/PKG_CHECK_MODULES/' configure.ac
aclocal ; libtoolize --force ; automake ; autoconf
%configure \
	--disable-static \
	--disable-xprint \
	--with-xdmconfigdir=%{_sysconfdir}/X11/xdm \
	--with-xdmscriptdir=%{_sysconfdir}/X11/xdm \
	--with-pixmapdir=%{_datadir}/xdm/pixmaps

make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT

# FIXME: Remove all libtool archives (*.la) from modules directory.  This
# should be fixed in upstream Makefile.am or whatever.
find $RPM_BUILD_ROOT -name '*.la' | xargs rm -f --

install -m 755 %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/X11/xdm/Xsetup_0

# Install pam xdm config files
{
   mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/pam.d
   install -c -m 644 %{SOURCE11} $RPM_BUILD_ROOT%{_sysconfdir}/pam.d/xdm
}

rm -f $RPM_BUILD_ROOT%{_sysconfdir}/X11/xdm/Xsession
(cd $RPM_BUILD_ROOT%{_sysconfdir}/X11/xdm; ln -sf ../xinit/Xsession .)

# we need to crate /var/lib/xdm to make authorization work (bug
# 500704)
mkdir -p $RPM_BUILD_ROOT%{_sharedstatedir}/xdm

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc AUTHORS COPYING INSTALL NEWS README ChangeLog
%{_bindir}/xdm
%{_bindir}/xdmshell
%dir %{_sysconfdir}/X11/xdm
# NOTE: The Xaccess file from our "xinitrc" package had no customizations,
# and was out of sync with upstream, so we ship the upstream one now.
%config %{_sysconfdir}/X11/xdm/Xaccess
%config %{_sysconfdir}/X11/xdm/Xresources
%config %{_sysconfdir}/X11/xdm/Xservers
%config %{_sysconfdir}/X11/xdm/xdm-config
%{_sysconfdir}/X11/xdm/GiveConsole
%{_sysconfdir}/X11/xdm/TakeConsole
%config %{_sysconfdir}/X11/xdm/Xreset
%{_sysconfdir}/X11/xdm/Xsession
%config %{_sysconfdir}/X11/xdm/Xsetup_0
%config %{_sysconfdir}/X11/xdm/Xstartup
%config %{_sysconfdir}/X11/xdm/Xwilling
# NOTE: For security, upgrades of this package will install the new pam.d
# files and make backup copies by default.  'noreplace' is intentionally avoided
# here.
%config %attr(0644,root,root) %{_sysconfdir}/pam.d/xdm
%dir %{_datadir}/X11
# NOTE: We intentionally default to OS supplied file being favoured here on
# OS upgrades.
%config %{_datadir}/X11/app-defaults/Chooser
%dir %{_datadir}/xdm
%dir %{_datadir}/xdm/pixmaps
%{_datadir}/xdm/pixmaps/xorg-bw.xpm
%{_datadir}/xdm/pixmaps/xorg.xpm
%dir %{_libdir}/X11/xdm
%dir %{_sharedstatedir}/xdm
%{_libdir}/X11/xdm/chooser
%{_libdir}/X11/xdm/libXdmGreet.so
%{_mandir}/man1/*.1*

%changelog
* Mon Nov 30 2009 Dennis Gregorovic <dgregor@redhat.com> - 1:1.1.6-14.1
- Rebuilt for RHEL 6

* Mon Aug 03 2009 Adam Jackson <ajax@redhat.com> 1.1.6-14
- Un-Requires xorg-x11-filesystem

* Mon Jul 27 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:1.1.6-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Jul 20 2009 Adam Jackson <ajax@redhat.com> 1.1.6-12
- Fix FTBFS due to Xaw xprint build macro disappearing. (#511508)

* Wed Jul 15 2009 Adam Jackson <ajax@redhat.com> 1.1.6-11
- Remove xserver PAM config file, it belongs (unsurprisingly) in
  xserver. (#500469)

* Tue Jun 23 2009 Matěj Cepl <mcepl@redhat.com> - 1:1.1.6-10
- return lost patch for fixing bug 470348.

* Thu May 14 2009 Matěj Cepl <mcepl@redhat.com> - 1:1.1.6-8
- Create /var/lib/xdm to make authorization work (bug 500704)

* Sat Mar 14 2009 Matěj Cepl <mcepl@redhat.com> - 1.1.6-7
- Make XDM work with SELinux (fix bug 388431)

* Thu Feb 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:1.1.6-6.0.bug388431test.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Thu Oct 30 2008 Soren Sandmann <ssp@redhat.com> 1.1.6-5
- Fix xdm.pamd (bug 388431)

* Tue Jul 15 2008 Adam Jackson <ajax@redhat.com> 1.1.6-4
- Fix license tag.

* Wed Feb 20 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 1:1.1.6-3
- Autorebuild for GCC 4.3

* Fri Aug 24 2007 Ray Strode <rstrode@redhat.com> 1:1.1.6-2
- Use system Xsession script (bug 244264)

* Fri Aug 17 2007 Dave Airlie <airlied@redhat.com> 1:1.1.6-1
- Update to 1.1.6

* Sat Aug 11 2007 Dave Airlie <airlied@redhat.com> 1:1.1.5-1
- Update to 1.1.5

* Fri Jan 05 2007 Adam Jackson <ajax@redhat.com> 1:1.1.3-1
- Update to 1.1.3

* Mon Jul 24 2006 Mike A. Harris <mharris@redhat.com> 1:1.0.5-5.fc6
- Added xdm-1.0.5-sessreg-utmp-fix-bug177890.patch to restore GiveConsole to
  what we shipped in 6.8.2, and also fix bug (#177890)

* Wed Jul 19 2006 Mike A. Harris <mharris@redhat.com> 1:1.0.5-4.fc6
- Remove app-defaults dir from file manifest, as it is owned by libXt (#174021)

* Mon Jul 17 2006 Mike A. Harris <mharris@redhat.com> 1:1.0.5-3.fc6
- Added pam_keyinit.so support to xdm.pamd and xserver.pamd (#198631)
- Flag pam.d{xdm,xserver} as attr(0644,root,root) replaceable config files.
- Flag app-defaults/Chooser as a replaceable config file.
- Add conditional {dist} flag to Release field.

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> 1:1.0.5-2
- rebuild

* Wed Jun 28 2006 Mike A. Harris <mharris@redhat.com> 1:1.0.5-1
- Updated xdm to version 1.0.5.
- Remove xdm-1.0.4-setuid.diff as it is integrated in 1.0.5

* Wed Jun 21 2006 Mike A. Harris <mharris@redhat.com> 1:1.0.4-4
- Add missing documentation to doc macro.
- Clean cruft out of specfile.

* Tue Jun 20 2006 Mike A. Harris <mharris@redhat.com> 1:1.0.4-3
- Added xdm-1.0.4-setuid.diff to fix potential security issue (#196094)
- Added temporary "BuildRequires: autoconf, automake, libtool" dependencies
  for mock builds, for as long as we need to run autotools at compile time.

* Tue May 30 2006 Adam Jackson <ajackson@redhat.com> 1:1.0.4-2
- Fix BuildRequires (#191858)

* Thu Apr 27 2006 Adam Jackson <ajackson@redhat.com> 1:1.0.4-1
- Updated to version 1.0.4

* Fri Mar 31 2006 Adam Jackson <ajackson@redhat.com> 1:1.0.3-1
- Updated to version 1.0.3.  Forcibly relibtoolize to avoid present and future
  bogons on libXdmGreet.so losing the .so extension.

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> 1:1.0.1-1.2
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> 1:1.0.1-1.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Mon Jan 09 2006 Mike A. Harris <mharris@redhat.com> 1:1.0.1-1
- Updated xdm to version 1.0.1 from X11R7.
- Added --with-xdmscriptdir option to ./configure to put scripts in /etc
- Updated xdm-1.0.1-redhat-xdm-config-fix.patch to work with xdm 1.0.1

* Thu Nov 24 2005 Mike A. Harris <mharris@redhat.com> 1:0.99.3-6
- Updated xdm.pamd to work with recent pam changes, and bumped the minimum
  pam requirement up to 0.78-0 for FC5 builds. (#170661)
- Added "Requires(pre): xorg-x11-filesystem >= 0.99.2-3", as the xdm package
  puts files into /usr/lib/X11, so we have to make sure it is not a symlink.
- Removed "filesystem" package dependency, as xorg-x11-filesystem carries
  that dependency now, so it can be updated in one spot.
- Added missing "BuildRequires: pkgconfig".
- Added xdm-0.99.3-xdm-app-defaults-in-datadir.patch to force app-defaults
  files to install into _datadir instead of _libdir.
- Added xdm-0.99.3-xdm-scripts-in-configdir.patch to put the xdm scripts in
  _sysconfdir, and removed older xdm-0.99.3-xdm-configdir.patch which hacked
  up Makefile.in.  Fixes a typo that caused Xreset to not get installed
  properly also.

* Mon Nov 14 2005 Jeremy Katz <katzj@redhat.com> 1:0.99.3-5
- require newer filesystem package (#172610)

* Mon Nov 14 2005 Jeremy Katz <katzj@redhat.com> 1:0.99.3-4
- install scripts into /etc/X11/xdm instead of %%{_libdir} (#173081)
- use our Xsetup_0 instead of xorg one (#173083) 

* Sat Nov 12 2005 Mike A. Harris <mharris@redhat.com> 1:0.99.3-3
- Added "Obsoletes: xinitrc", as xdm now provides files that were previously
  part of that package.  xorg-x11-xinit now provides the xinitrc scripts.

* Sat Nov 12 2005 Mike A. Harris <mharris@redhat.com> 1:0.99.3-2
- Rebuild against new libXaw 0.99.2-2, which has fixed DT_SONAME.
- Added xdm-0.99.3-redhat-xdm-config-fix.patch which merges in an
  xdm-config fix present in the forked Red Hat xdm-config from the FC4
  xinitrc package, which invokes Xwilling with "-s /bin/bash" instead
  of "-c" to fix bug (#86505).
- Removed ancient xdm rpm preinstall script, as it should be unnecessary now.

* Fri Nov 11 2005 Mike A. Harris <mharris@redhat.com> 1:0.99.3-1
- Update xdm to 0.99.3 from X11R7 RC2.

* Tue Nov 01 2005 Mike A. Harris <mharris@redhat.com> 1:0.99.2-1.20051031.3
- Build with -fno-strict-aliasing to work around possible pointer aliasing
  issues

* Tue Nov 01 2005 Mike A. Harris <mharris@redhat.com> 1:0.99.2-1.20051031.2
- It is _sysconfdir not _sysconfigdir goofball!
- Add {_sysconfdir}/pam.d/xdm and {_sysconfdir}/pam.d/xserver files that were
  missing from file manifest.

* Mon Oct 31 2005 Mike A. Harris <mharris@redhat.com> 1:0.99.2-1.20051031.1
- Make sure all dirs are owned that xdm creates.
- Misc spec file cleanups

* Mon Oct 31 2005 Mike A. Harris <mharris@redhat.com> 1:0.99.2-1.20051031.0
- Update xdm to 0.99.2 from X11R7 RC1.
- Update to CVS snapshot from 20051031
- Add Epoch 1, and change package to use the xdm version number.  Later, if
  we decide to rename the package to "xdm", we can drop the Epoch tag.
- Disable Xprint support
- Use _smp_mflags
- Add xdm-0.99.2-to-20051031.patch to pick up fixes from CVS head that allow
  us to set the config dir and other dirs.

* Wed Oct 05 2005 Mike A. Harris <mharris@redhat.com> 6.99.99.0-2
- Use Fedora-Extras style BuildRoot tag
- Update BuildRequires to use new library package names

* Wed Aug 24 2005 Mike A. Harris <mharris@redhat.com> 6.99.99.0-1
- Initial build.
