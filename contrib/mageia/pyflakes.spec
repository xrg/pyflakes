Name:           pyflakes
Version:        0.5.0
Release:        %mkrel 2
Summary:        Simple program which checks Python source files for errors
License:        MIT
Group:          Development/Python
URL:            https://launchpad.net/pyflakes
Source:         https://launchpad.net/pyflakes/+download/%{name}-%{version}.tar.gz
Buildrequires:  python-devel
BuildArch:      noarch

%description
Pyflakes is a simple program which checks Python source files for errors. It is
similar to PyChecker in scope, but differs in that it does not execute the
modules to check them. This is both safer and faster, although it does not
perform as many checks.
Unlike PyLint, Pyflakes checks only for logical errors in programs; it does
not perform any checks on style.

%prep
%setup -q

%build

%install
%__rm -rf %{buildroot}
%__python setup.py install --root %buildroot

%clean
%__rm -rf %{buildroot}

%files
%defattr(-,root,root)
%{_bindir}/*
%{py_puresitedir}/%{name}
%{py_puresitedir}/*.egg-info


