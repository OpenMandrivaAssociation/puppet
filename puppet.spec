%define ppconfdir conf/redhat
%define confdir   ext/redhat
%define puppet_libdir   %{ruby_vendorlibdir}

Name:		puppet
Version:	3.4.3
Release:	2
Summary:	System Automation and Configuration Management Software
License:	Apache License v2
Group:		Monitoring
URL:		http://www.puppetlabs.com/
Source0:	http://downloads.puppetlabs.com/puppet/%{name}-%{version}.tar.gz
Source1:        http://downloads.puppetlabs.com/%{name}/%{name}-%{version}.tar.gz.asc
Source2:        puppet-nm-dispatcher
Source3:        puppet-nm-dispatcher.systemd
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
chmod +x ext/puppet-load.rb ext/regexp_nodes/regexp_nodes.rb


%install
ruby install.rb --destdir=%{buildroot} --quick --no-rdoc --sitelibdir=%{puppet_libdir}

install -d -m0755 %{buildroot}%{_sysconfdir}/puppet/manifests
install -d -m0755 %{buildroot}%{_datadir}/%{name}/modules
install -d -m0755 %{buildroot}%{_localstatedir}/lib/puppet
install -d -m0755 %{buildroot}%{_localstatedir}/run/puppet
install -d -m0750 %{buildroot}%{_localstatedir}/log/puppet

%{__install} -d -m0755  %{buildroot}%{_unitdir}
install -Dp -m0644 ext/systemd/puppet.service %{buildroot}%{_unitdir}/puppet.service
install -Dp -m0644 ext/systemd/puppetmaster.service %{buildroot}%{_unitdir}/puppetmaster.service

install -Dp -m0644 %{confdir}/fileserver.conf %{buildroot}%{_sysconfdir}/puppet/fileserver.conf
install -Dp -m0644 %{confdir}/puppet.conf %{buildroot}%{_sysconfdir}/puppet/puppet.conf
install -Dp -m0644 %{confdir}/logrotate %{buildroot}%{_sysconfdir}/logrotate.d/puppet

# Install a NetworkManager dispatcher script to pickup changes to
# /etc/resolv.conf and such (https://b.*illa.redhat.com/532085).
install -Dpv %{SOURCE3} \
    %{buildroot}%{_sysconfdir}/NetworkManager/dispatcher.d/98-%{name}

# Install the ext/ directory to %%{_datadir}/%%{name}
install -d %{buildroot}%{_datadir}/%{name}
cp -a ext/ %{buildroot}%{_datadir}/%{name}
# emacs and vim bits are installed elsewhere
rm -rf %{buildroot}%{_datadir}/%{name}/ext/{emacs,vim}
# remove misc packaging artifacts in source not applicable to rpm
rm -rf %{buildroot}%{_datadir}/%{name}/ext/{gentoo,freebsd,solaris,suse,windows,osx,ips,debian}
rm -f %{buildroot}%{_datadir}/%{name}/ext/{build_defaults.yaml,project_data.yaml}
rm -f %{buildroot}%{_datadir}/%{name}/ext/redhat/*.init

# Install emacs mode files
emacsdir=%{buildroot}%{_datadir}/emacs/site-lisp
install -Dp -m0644 ext/emacs/puppet-mode.el $emacsdir/puppet-mode.el
install -Dp -m0644 ext/emacs/puppet-mode-init.el \
    $emacsdir/site-start.d/puppet-mode-init.el

# Install vim syntax files
vimdir=%{buildroot}%{_datadir}/vim/vimfiles
install -Dp -m0644 ext/vim/ftdetect/puppet.vim $vimdir/ftdetect/puppet.vim
install -Dp -m0644 ext/vim/syntax/puppet.vim $vimdir/syntax/puppet.vim

# Setup tmpfiles.d config
mkdir -p %{buildroot}%{_sysconfdir}/tmpfiles.d
echo "D /var/run/%{name} 0755 %{name} %{name} -" > \
    %{buildroot}%{_sysconfdir}/tmpfiles.d/%{name}.conf

# Create puppet modules directory for puppet module tool
mkdir -p %{buildroot}%{_sysconfdir}/%{name}/modules

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
%doc LICENSE README.md examples
%{_bindir}/puppet
%{_bindir}/extlookup2hiera
%{puppet_libdir}/*
%{_unitdir}/puppet.service
%dir %{_sysconfdir}/puppet
%dir %{_sysconfdir}/%{name}/modules
%config(noreplace) %{_sysconfdir}/tmpfiles.d/%{name}.conf
%config(noreplace) %{_sysconfdir}/puppet/puppet.conf
%config(noreplace) %{_sysconfdir}/puppet/auth.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/puppet
%dir %{_sysconfdir}/NetworkManager
%dir %{_sysconfdir}/NetworkManager/dispatcher.d
%{_sysconfdir}/NetworkManager/dispatcher.d/98-puppet
# We don't want to require emacs or vim, so we need to own these dirs
%{_datadir}/emacs
%{_datadir}/vim
%{_datadir}/%{name}
# These need to be owned by puppet so the server can
# write to them
%attr(-, puppet, puppet) %{_localstatedir}/run/puppet
%attr(0750, puppet, puppet) %{_localstatedir}/log/puppet
%attr(-, puppet, puppet) %{_localstatedir}/lib/puppet
%{_mandir}/man5/puppet.conf.5.*
%{_mandir}/man8/puppet.8.*
%{_mandir}/man8/puppet-agent.8.*
%{_mandir}/man8/puppet-apply.8.*
%{_mandir}/man8/puppet-catalog.8.*
%{_mandir}/man8/puppet-describe.8.*
%{_mandir}/man8/puppet-ca.8.*
%{_mandir}/man8/puppet-cert.8.*
%{_mandir}/man8/puppet-certificate.8.*
%{_mandir}/man8/puppet-certificate_request.8.*
%{_mandir}/man8/puppet-certificate_revocation_list.8.*
%{_mandir}/man8/puppet-config.8.*
%{_mandir}/man8/puppet-device.8.*
%{_mandir}/man8/puppet-doc.8.*
%{_mandir}/man8/puppet-facts.8.*
%{_mandir}/man8/puppet-file.8.*
%{_mandir}/man8/puppet-filebucket.8.*
%{_mandir}/man8/puppet-help.8.*
%{_mandir}/man8/puppet-inspect.8.*
%{_mandir}/man8/puppet-instrumentation_data.8.*
%{_mandir}/man8/puppet-instrumentation_listener.8.*
%{_mandir}/man8/puppet-instrumentation_probe.8.*
%{_mandir}/man8/puppet-key.8.*
%{_mandir}/man8/puppet-man.8.*
%{_mandir}/man8/puppet-module.8.*
%{_mandir}/man8/puppet-node.8.*
%{_mandir}/man8/puppet-parser.8.*
%{_mandir}/man8/puppet-plugin.8.*
%{_mandir}/man8/puppet-report.8.*
%{_mandir}/man8/puppet-resource.8.*
%{_mandir}/man8/puppet-resource_type.8.*
%{_mandir}/man8/puppet-secret_agent.8.*
%{_mandir}/man8/puppet-status.8.*
%{_mandir}/man8/extlookup2hiera.8.*

%files server
%defattr(-, root, root, 0755)
%{_unitdir}/puppetmaster.service
%config(noreplace) %{_sysconfdir}/puppet/fileserver.conf
%dir %{_sysconfdir}/puppet/manifests
%{_mandir}/man8/puppet-kick.8.*
%{_mandir}/man8/puppet-master.8.*
%{_mandir}/man8/puppet-queue.8.*
