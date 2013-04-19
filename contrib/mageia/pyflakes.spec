%define git_repo pyflakes
%define git_head HEAD

Name:		pyflakes
Version:	%git_get_ver
Release:	%mkrel %git_get_rel2
Summary:        Simple program which checks Python source files for errors
License:        MIT
Group:          Development/Python
URL:            https://launchpad.net/pyflakes
Source:		%git_bs_source %{name}-%{version}.tar.gz
Source1:	%{name}-gitrpm.version
Source2:	%{name}-changelog.gitrpm.txt
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
%git_get_source
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


