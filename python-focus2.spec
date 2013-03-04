%global mod_name focus

Name:           python-focus2
Version:        1.0
Release:        0%{?dist}
Summary:        Sample interface to OpenStack

Group:          Development/Libraries
License:        GNU LGPL 2.1
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python-setuptools

Requires:       python-flask >= 0.9
Requires:       python-flask-wtf >= 0.6
Requires:       MySQL-python
Requires:       python-requests >= 0.8
Requires:       python-jsonschema >= 0.2, python-jsonschema < 1.0

Requires:       start-stop-daemon

%description


%prep
%setup -q


%build
%{__python} setup.py build


%install
rm -rf %{buildroot}
%{__python} setup.py install -O1 --skip-build --root %{buildroot}
rm -rf %{buildroot}%{python_sitelib}/*/tests

cd redhat
for script in *.init; do
    install -p -D -m755 "$script" "%{buildroot}%{_initrddir}/${script%.init}"
done
cd ..
mkdir -p %{buildroot}/etc/focus2
install -p -D -m644 etc/* %{buildroot}/etc/focus2

install -d -m755 %{buildroot}%{_localstatedir}/{log,lib,run}/focus2

%clean
%__rm -rf %{buildroot}


%pre
getent group focus2 >/dev/null || groupadd -r focus2
getent passwd focus2 >/dev/null || \
useradd -r -g focus2 -d %{_sharedstatedir}/focus2 -s /sbin/nologin \
-c "Focus2 Daemon" focus2
exit 0


%preun
if [ $1 -eq 0 ] ; then
    /sbin/service focus2 stop >/dev/null 2>&1
    /sbin/chkconfig --del focus2
fi
exit 0


%postun
if [ $1 -eq 1 ] ; then
    /sbin/service focus2 condrestart
fi
exit 0

%files
%doc README* COPYING
%defattr(-,root,root,-)
%{python_sitelib}/*
%{_usr}/bin/*
%{_initrddir}/*

%attr(770,focus2,focus2) %dir %{_localstatedir}/*/focus2

%defattr(-,focus2,focus2,-)
%dir /etc/focus2
%config(noreplace) /etc/focus2/*

%changelog
* Tue Feb 26 2013 Alessio Ababilov <aababilov@griddynamics.com> - 1.0-0
- Initial RPM release
