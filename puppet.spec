%define ppconfdir conf/redhat

Name:		puppet 
Version:	2.7.22
Release:	1
Summary:	System Automation and Configuration Management Software
License:	Apache License v2
Group:		Monitoring
URL:		http://www.puppetlabs.com/
Source0:	http://puppetlabs.com/downloads/puppet/%{name}-%{version}.tar.gz
Source100:	puppet.init
Source101:	puppetmaster.init
BuildRequires:	ruby facter
Requires:	ruby >= 1.8.1
Requires:	facter >= 1.1
Requires(post):	rpm-helper
Requires(preun):rpm-helper
BuildArch:	noarch


%description
Puppet lets you centrally manage every important aspect of your system using a 
cross-platform specification language that manages all the separate elements 
normally aggregated in different files, like users, cron jobs, and hosts, 
along with obviously discrete elements like packages, services, and files.

This package provide the puppet client daemon.


%package server
Group:		Monitoring 
Summary:	Server for the puppet system management tool
Requires:	%{name} = %{version}
Requires(post):	rpm-helper
Requires(preun):rpm-helper
 
%description server
Provides the central puppet server daemon (puppetmaster) which provides
manifests to clients.
The server can also function as a certificate authority and file server.

%prep
%setup -q

%build
# Use /usr/bin/ruby directly instead of /usr/bin/env ruby in
#+ executables. Otherwise, initscripts break since pidof can't
#+ find the right process
for f in bin/* ; do 
  sed -i -e '1c#!/usr/bin/ruby' $f
done

%install
ruby install.rb --destdir=%{buildroot} --quick --no-rdoc

%{__install} -d -m 0755 %{buildroot}%{_sysconfdir}/%{name}/manifests
%{__install} -d -m 0755 %{buildroot}%{_initrddir}
%{__install} -d -m 0755 %{buildroot}%{_defaultdocdir}/%{name}
%{__install} -d -m 0755 %{buildroot}%{_localstatedir}/lib/%{name}
%{__install} -d -m 0755 %{buildroot}%{_var}/run/%{name}
%{__install} -d -m 0755 %{buildroot}%{_logdir}/%{name}

%{__install} -Dp -m 0644 %{ppconfdir}/client.sysconfig %{buildroot}%{_sysconfdir}/sysconfig/puppetd
%{__install} -Dp -m 0644 %{ppconfdir}/server.sysconfig %{buildroot}%{_sysconfdir}/sysconfig/puppetmasterd
%{__install} -m 755 %{SOURCE100} %{buildroot}%{_initrddir}/puppet
%{__install} -m 755 %{SOURCE101} %{buildroot}%{_initrddir}/puppetmaster
%{__install} -Dp -m 0644 %{ppconfdir}/fileserver.conf %{buildroot}%{_sysconfdir}/%{name}/fileserver.conf
%{__install} -Dp -m 0644 %{ppconfdir}/puppet.conf %{buildroot}%{_sysconfdir}/%{name}/puppet.conf
%{__install} -Dp -m 0644 %{ppconfdir}/logrotate %{buildroot}%{_sysconfdir}/logrotate.d/puppet
# We need something for these ghosted files, otherwise rpmbuild
# will complain loudly. They won't be included in the binary packages
touch %{buildroot}%{_sysconfdir}/%{name}/puppetmasterd.conf
touch %{buildroot}%{_sysconfdir}/%{name}/puppetca.conf
touch %{buildroot}%{_sysconfdir}/%{name}/puppetd.conf

## install vim syntax file
%{__install} -d -m 755 %{buildroot}%{_datadir}/vim/syntax
%{__install} -d -m 755 %{buildroot}%{_datadir}/vim/ftdetect

%{__install} -m 644 ext/vim/syntax/puppet.vim %{buildroot}%{_datadir}/vim/syntax
%{__install} -m 644 ext/vim/ftdetect/puppet.vim %{buildroot}%{_datadir}/vim/ftdetect

## install emacs syntax file
%{__install} -d -m 0755 %{buildroot}%{_sysconfdir}/emacs/site-start.d
%{__install} -d -m 0755 %{buildroot}%{_datadir}/emacs/site-lisp
%{__install} -m 0644 ext/emacs/puppet-mode-init.el %{buildroot}%{_sysconfdir}/emacs/site-start.d
%{__install} -m 0644 ext/emacs/puppet-mode.el %{buildroot}%{_datadir}/emacs/site-lisp

## Install logcheck files
%{__install} -d -m 0755 %{buildroot}%{_sysconfdir}/logcheck/ignore.d.{server,workstation}
%{__install} -m 0644 ext/logcheck/puppet %{buildroot}%{_sysconfdir}/logcheck/ignore.d.server/
%{__install} -m 0644 ext/logcheck/puppet %{buildroot}%{_sysconfdir}/logcheck/ignore.d.workstation/

%pre
%_pre_useradd puppet %{_localstatedir}/lib/%{name} /sbin/nologin 

%post
%_post_service puppet

%preun
%_preun_service puppet 


%post server
%_post_service puppetmaster

%preun server
%_preun_service puppetmaster 


%files
%defattr(-, root, root, 0755)
%doc CHANGELOG LICENSE examples
%dir %{_sysconfdir}/puppet
%{_bindir}/puppet
%{_bindir}/ralsh
%{_bindir}/pi
%{_bindir}/filebucket
%{_bindir}/puppetdoc
%{_sbindir}/puppetd
%{ruby_sitelibdir}/puppet.rb
%{ruby_sitelibdir}/semver.rb
%{ruby_sitelibdir}/%{name}
%{_initrddir}/puppet

%{_mandir}/man8/puppet.*
%{_mandir}/man8/ralsh.*
%{_mandir}/man8/pi.*
%{_mandir}/man8/filebucket.*
%{_mandir}/man8/puppetdoc.*
%{_mandir}/man8/puppetd.*
%{_mandir}/man5/puppet.conf.*
%{_mandir}/man8/puppet-*
 
%config(noreplace) %{_sysconfdir}/sysconfig/puppetd
%config(noreplace) %{_sysconfdir}/%{name}/puppet.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/puppet
%ghost %config(noreplace,missingok) %{_sysconfdir}/%{name}/puppetd.conf

%{_sysconfdir}/logcheck/ignore.d.workstation/%{name}
%{_sysconfdir}/logcheck/ignore.d.server/
%{_sysconfdir}/emacs/site-start.d/puppet-mode-init.el
%{_datadir}/emacs/site-lisp/puppet-mode.el
%{_datadir}/vim/syntax/puppet.vim
%{_datadir}/vim/ftdetect/puppet.vim

# These need to be owned by puppet so the server can
# write to them
%attr(-, %{name}, %{name}) %{_var}/run/%{name}
%attr(-, %{name}, %{name}) %{_logdir}/%{name}
%attr(-, %{name}, %{name}) %{_localstatedir}/lib/%{name}

%files server
%defattr(-, root, root, 0755)
%doc ext/rack
%{_sbindir}/puppetmasterd
%{_sbindir}/puppetca
%{_sbindir}/puppetrun
%{_sbindir}/puppetqd
%{_initrddir}/puppetmaster
%config(noreplace) %{_sysconfdir}/%{name}/fileserver.conf
%config(noreplace) %{_sysconfdir}/%{name}/auth.conf
%dir %{_sysconfdir}/puppet/manifests
%config(noreplace) %{_sysconfdir}/sysconfig/puppetmasterd
%ghost %config(noreplace,missingok) %{_sysconfdir}/%{name}/puppetca.conf
%ghost %config(noreplace,missingok) %{_sysconfdir}/%{name}/puppetmasterd.conf

%{_mandir}/man8/puppetca.*
%{_mandir}/man8/puppetrun.*
%{_mandir}/man8/puppetqd.*
%{_mandir}/man8/puppetmasterd.*


%changelog
* Tue Apr 17 2012 Alexander Khrukin <akhrukin@mandriva.org> 2.7.13-1mdv2012.0
+ Revision: 791425
- version update 2.7.13

* Thu Mar 15 2012 Alexander Khrukin <akhrukin@mandriva.org> 2.7.12-1
+ Revision: 785052
- version update 2.7.12

* Tue Feb 14 2012 Bogdano Arendartchuk <bogdano@mandriva.com> 2.7.10-1
+ Revision: 773898
- updated version 2.7.10 (to fix upstream issue #10269)

* Mon Oct 24 2011 Michael Scherer <misc@mandriva.org> 2.7.6-1
+ Revision: 706103
- upgrade to 2.7.6

* Thu Oct 06 2011 Michael Scherer <misc@mandriva.org> 2.7.1-3
+ Revision: 703341
- revert previous commit, no need to add useless requires just for documentation

  + Alexander Barakin <abarakin@mandriva.org>
    - fix #61042

* Thu Jun 23 2011 Michael Scherer <misc@mandriva.org> 2.7.1-1
+ Revision: 686749
- update to 2.7.1

* Tue May 10 2011 Sandro Cazzaniga <kharec@mandriva.org> 2.6.8-1
+ Revision: 673207
- new bugfixe release

* Tue Apr 05 2011 Sandro Cazzaniga <kharec@mandriva.org> 2.6.7-1
+ Revision: 650710
- new version 2.6.7

* Mon Mar 21 2011 Michael Scherer <misc@mandriva.org> 2.6.6-2
+ Revision: 647415
- license was changed upstream

* Wed Mar 16 2011 Sandro Cazzaniga <kharec@mandriva.org> 2.6.6-1
+ Revision: 645655
- new version 2.6.6 (bugfix release)

  + Guillaume Rousse <guillomovitch@mandriva.org>
    - new version
    - ship files needed for running puppetmaster with passenger as documentation

* Wed Jan 19 2011 Guillaume Rousse <guillomovitch@mandriva.org> 2.6.4-2
+ Revision: 631707
- patch0, from upstream: fix syntax parsing with --ignoreimport option

* Thu Dec 02 2010 Michael Scherer <misc@mandriva.org> 2.6.4-1mdv2011.0
+ Revision: 604643
- update to 2.6.4 ( security fix )

* Mon Nov 29 2010 Michael Scherer <misc@mandriva.org> 2.6.3-1mdv2011.0
+ Revision: 603105
- update to new version 2.6.3

* Mon Nov 01 2010 Michael Scherer <misc@mandriva.org> 2.6.2-1mdv2011.0
+ Revision: 591482
- update to new version 2.6.2

* Sat Sep 18 2010 Guillaume Rousse <guillomovitch@mandriva.org> 2.6.1-1mdv2011.0
+ Revision: 579557
- update to new version 2.6.1

* Wed Aug 25 2010 Michael Scherer <misc@mandriva.org> 2.6.0-1mdv2011.0
+ Revision: 573154
- update to 2.6.0 version
- really fix the issue of puppet being killed on log rotation

* Thu Aug 05 2010 Michael Scherer <misc@mandriva.org> 0.25.4-2mdv2011.0
+ Revision: 566099
- fix initscript so reload do not kill puppet, by sending SIGTERM instead of SIGHUP ( as seen on cooker, but not on my 2010.1 server )

* Mon Apr 12 2010 Michael Scherer <misc@mandriva.org> 0.25.4-1mdv2010.1
+ Revision: 533709
- fix Url
- update to 0.25.4
- use install.rb instead of doing it by hand
- add man pages

* Thu Jan 21 2010 Michael Scherer <misc@mandriva.org> 0.24.7-3mdv2010.1
+ Revision: 494418
- fix initscript configuration

* Sun Aug 16 2009 Michael Scherer <misc@mandriva.org> 0.24.7-2mdv2010.0
+ Revision: 416752
- fix loop on status, patch by roudoudou, bug #40414
- fix error when no site.pp exist, bug #52895

* Tue Dec 30 2008 Guillaume Rousse <guillomovitch@mandriva.org> 0.24.7-1mdv2009.1
+ Revision: 321401
- update to new version 0.24.7

* Fri Sep 12 2008 Olivier Thauvin <nanardon@mandriva.org> 0.24.5-2mdv2009.0
+ Revision: 284057
- fix sysconfig/* filename

* Fri Aug 01 2008 Michael Scherer <misc@mandriva.org> 0.24.5-1mdv2009.0
+ Revision: 259425
- new version

* Fri Aug 01 2008 Thierry Vignaud <tv@mandriva.org> 0.23.2-4mdv2009.0
+ Revision: 259355
- rebuild

* Thu Jul 24 2008 Thierry Vignaud <tv@mandriva.org> 0.23.2-3mdv2009.0
+ Revision: 247238
- rebuild
- fix description-line-too-long
- kill re-definition of %%buildroot on Pixel's request

  + Pixel <pixel@mandriva.com>
    - adapt to %%_localstatedir now being /var instead of /var/lib (#22312)

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

* Tue Oct 30 2007 Funda Wang <fwang@mandriva.org> 0.23.2-1mdv2008.1
+ Revision: 103930
- BR ruby
- import puppet

