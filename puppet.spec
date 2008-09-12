%define name    puppet
%define version 0.24.5
%define release %mkrel 2

%define ppconfdir conf/redhat

Name:           %{name}  
Version:        %{version}
Release:        %{release}
Summary:        System Automation and Configuration Management Software
License:        GPLv2+
Group:          Monitoring
URL:            http://puppet.reductivelabs.com/
Source0:        http://reductivelabs.com/downloads/puppet/%{name}-%{version}.tgz
Source100:        puppet.init
Source101:        puppetmaster.init
BuildArch:      noarch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildRequires:	ruby
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
%{__install} -d -m 0755 %{buildroot}%{_sbindir}
%{__install} -d -m 0755 %{buildroot}%{_bindir}
%{__install} -d -m 0755 %{buildroot}%{ruby_sitelibdir}/%{name}
%{__install} -d -m 0755 %{buildroot}%{_sysconfdir}/%{name}/manifests
%{__install} -d -m 0755 %{buildroot}%{_sysconfdir}/sysconfig
%{__install} -d -m 0755 %{buildroot}%{_initrddir}
%{__install} -d -m 0755 %{buildroot}%{_defaultdocdir}/%{name}
%{__install} -d -m 0755 %{buildroot}%{_localstatedir}/lib/%{name}
%{__install} -d -m 0755 %{buildroot}%{_var}/run/%{name}
%{__install} -d -m 0755 %{buildroot}%{_logdir}/%{name}
%{__install} -Dp -m 0755 bin/* %{buildroot}%{_sbindir}
%{__mv} %{buildroot}%{_sbindir}/puppet %{buildroot}%{_bindir}/puppet
%{__mv} %{buildroot}%{_sbindir}/ralsh %{buildroot}%{_bindir}/ralsh
%{__mv} %{buildroot}%{_sbindir}/filebucket %{buildroot}%{_bindir}/filebucket
%{__mv} %{buildroot}%{_sbindir}/puppetdoc %{buildroot}%{_bindir}/puppetdoc
#FIXME: puppetrun dans puppetmaster ?
%{__mv} %{buildroot}%{_sbindir}/puppetrun %{buildroot}%{_bindir}/puppetrun
%{__install} -Dp -m 0644 lib/puppet.rb %{buildroot}%{ruby_sitelibdir}/puppet.rb
%{__cp} -a lib/puppet/* %{buildroot}%{ruby_sitelibdir}/%{name}
%{__find} %{buildroot}%{ruby_sitelibdir}/%{name} -type f -perm +ugo+x -print0 | xargs -0 -r %{__chmod} a-x
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

# install vim syntax file
%{__install} -d -m 755 %{buildroot}%{_datadir}/vim/syntax
%{__install} -d -m 755 %{buildroot}%{_datadir}/vim/ftdetect

%{__install} -m 644 ext/vim/syntax/puppet.vim %{buildroot}%{_datadir}/vim/syntax
%{__install} -m 644 ext/vim/ftdetect/puppet.vim %{buildroot}%{_datadir}/vim/ftdetect

# install emacs syntax file
%{__install} -d -m 0755 %{buildroot}%{_sysconfdir}/emacs/site-start.d
%{__install} -d -m 0755 %{buildroot}%{_datadir}/emacs/site-lisp
%{__install} -m 0644 ext/emacs/puppet-mode-init.el %{buildroot}%{_sysconfdir}/emacs/site-start.d
%{__install} -m 0644 ext/emacs/puppet-mode.el %{buildroot}%{_datadir}/emacs/site-lisp

# Install logcheck files
%{__install} -d -m 0755 %{buildroot}%{_sysconfdir}/logcheck/ignore.d.{server,workstation}
%{__install} -m 0644 ext/logcheck/puppet %{buildroot}%{_sysconfdir}/logcheck/ignore.d.server/
%{__install} -m 0644 ext/logcheck/puppet %{buildroot}%{_sysconfdir}/logcheck/ignore.d.workstation/

# Install other ext/* files
%{__install} -d -m 0755  %{buildroot}%{_datadir}/%{name}/ext
%{__cp}  -a ext/{module_puppet,puppet-test,ldap} %{buildroot}%{_datadir}/%{name}/ext/

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
%{_bindir}/filebucket
%{_bindir}/puppetdoc
%{_sbindir}/puppetd
%{ruby_sitelibdir}/puppet.rb
%{ruby_sitelibdir}/%{name}
%{_initrddir}/puppet
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
%{_datadir}/%{name}

# These need to be owned by puppet so the server can
# write to them
%attr(-, %{name}, %{name}) %{_var}/run/%{name}
%attr(-, %{name}, %{name}) %{_logdir}/%{name}
%attr(-, %{name}, %{name}) %{_localstatedir}/lib/%{name}

%files server
%defattr(-, root, root, 0755)
%{_sbindir}/puppetmasterd
%{_sbindir}/puppetca
%{_bindir}/puppetrun
%{_initrddir}/puppetmaster
%config(noreplace) %{_sysconfdir}/%{name}/fileserver.conf
%dir %{_sysconfdir}/puppet/manifests
%config(noreplace) %{_sysconfdir}/sysconfig/puppetmasterd
%ghost %config(noreplace,missingok) %{_sysconfdir}/%{name}/puppetca.conf
%ghost %config(noreplace,missingok) %{_sysconfdir}/%{name}/puppetmasterd.conf

