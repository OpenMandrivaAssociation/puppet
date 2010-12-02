%define name    puppet
%define version 2.6.4
%define release %mkrel 1

%define ppconfdir conf/redhat

Name:           %{name}  
Version:        %{version}
Release:        %{release}
Summary:        System Automation and Configuration Management Software
License:        GPLv2+
Group:          Monitoring
URL:            http://www.puppetlabs.com/
Source0:        http://puppetlabs.com/downloads/puppet/%{name}-%{version}.tar.gz
Source100:        puppet.init
Source101:        puppetmaster.init
BuildArch:      noarch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildRequires:	ruby facter
Requires:       ruby >= 1.8.1
Requires:       facter >= 1.1
Requires(post): rpm-helper
Requires(preun):rpm-helper

%description
Puppet lets you centrally manage every important aspect of your system using a 
cross-platform specification language that manages all the separate elements 
normally aggregated in different files, like users, cron jobs, and hosts, 
along with obviously discrete elements like packages, services, and files.

This package provide the puppet client daemon.


%package server
Group:          Monitoring 
Summary:        Server for the puppet system management tool
Requires:       %{name} = %{version}
Requires(post): rpm-helper
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
%{__rm} -rf %{buildroot}

ruby install.rb --destdir=%{buildroot} --quick --no-rdoc

%{__install} -d -m 0755 %{buildroot}%{_sysconfdir}/%{name}/manifests
%{__install} -d -m 0755 %{buildroot}%{_initrddir}
%{__install} -d -m 0755 %{buildroot}%{_defaultdocdir}/%{name}
%{__install} -d -m 0755 %{buildroot}%{_localstatedir}/lib/%{name}
%{__install} -d -m 0755 %{buildroot}%{_var}/run/%{name}
%{__install} -d -m 0755 %{buildroot}%{_logdir}/%{name}

#%{__find} %{buildroot}%{ruby_sitelibdir}/%{name} -type f -perm +ugo+x -print0 | xargs -0 -r %{__chmod} a-x
#
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

%clean
rm -rf %{buildroot}

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
%doc CHANGELOG COPYING LICENSE README examples
%dir %{_sysconfdir}/puppet
%{_bindir}/puppet
%{_bindir}/ralsh
%{_bindir}/pi
%{_bindir}/filebucket
%{_bindir}/puppetdoc
%{_sbindir}/puppetd
%{ruby_sitelibdir}/puppet.rb
%{ruby_sitelibdir}/%{name}
%{_initrddir}/puppet

%{_mandir}/man8/puppet.*
%{_mandir}/man8/ralsh.*
%{_mandir}/man8/pi.*
%{_mandir}/man8/filebucket.*
%{_mandir}/man8/puppetdoc.*
%{_mandir}/man8/puppetd.*
%{_mandir}/man5/puppet.conf.*
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
