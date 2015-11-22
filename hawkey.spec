# libsolv minimum version
%global libsolv_version 0.6.14-1

%bcond_without python3

# The C API and valgrind tests currently fail,
# while the Python tests pass. FIX AND ENABLE ASAP!
%bcond_with tests

%define major 2
%define libname %mklibname hawkey %{major}
%define devname %mklibname hawkey -d
# Fedora package release versions are committed as versions in upstream
%define origrel 1

Name:		hawkey
Version:	0.6.2
Release:	1
Summary:	Library providing simplified C and Python API to libsolv
Group:		System/Libraries
License:	LGPLv2+
URL:		https://github.com/rpm-software-management/%{name}
Source0:	https://github.com/rpm-software-management/%{name}/archive/%{name}-%{version}-%{origrel}.tar.gz

BuildRequires:	solv-devel >= %{libsolv_version}
BuildRequires:	cmake
BuildRequires:	pkgconfig(expat)
BuildRequires:	pkgconfig(rpm)
BuildRequires:	pkgconfig(zlib)
BuildRequires:	pkgconfig(check)

%if %{with tests}
# Needed for some of the tests
BuildRequires:	valgrind
%endif

# We cannot prevent provides from nonstandard paths for now, since rpm adds Requires if we do:
# %%define __noautoprovfiles %{python2_sitearch}/.*\\.so\\|%{python3_sitearch}/.*\\.so\\|%{python2_sitearch}/hawkey/test/.*\\.so\\|%{python3_sitearch}/hawkey/test/.*\\.so

%description
A Library providing simplified C and Python API to libsolv.


%package -n %{libname}
Summary:	Libraries for %{name}
Group:		System/Libraries
Requires:	%{_lib}solv0%{?_isa} >= %{libsolv_version}

%description -n %{libname}
Libraries for %{name}

%package -n %{devname}
Summary:	A Library providing simplified C and Python API to libsolv
Group:		Development/C
Provides:	%{name}-devel = %{version}-%{release}
Requires:	%{libname}%{?_isa} = %{version}-%{release}
Requires:	solv-devel

%description -n %{devname}
Development files for %{name}.

%package -n python2-hawkey
Summary:	Python 2 bindings for the hawkey library
Group:		Development/Python
BuildRequires:	python2-devel
BuildRequires:	python2-nose
BuildRequires:	python2-sphinx
%if %{without python3}
Provides:	python-%{name} = %{version}-%{release}
%endif
Requires:	%{libname}%{?_isa} = %{version}-%{release}

%description -n python2-hawkey
Python 2 bindings for the hawkey library.

%if %{with python3}
%package -n python-hawkey
Summary:	Python 3 bindings for the hawkey library
Group:		Development/Python
Provides:	python3-%{name} = %{version}-%{release}
BuildRequires:	python-devel
BuildRequires:	python-nose
BuildRequires:	python-sphinx
Requires:	%{libname}%{?_isa} = %{version}-%{release}

%description -n python-hawkey
Python 3 bindings for the hawkey library.
%endif

%prep
%setup -q -n %{name}-%{name}-%{version}-%{origrel}

%if %{with python3}
rm -rf py3
mkdir py3
%endif

%build
%cmake -DCMAKE_BUILD_TYPE=RelWithDebInfo
%make
make doc-man

%if %{with python3}
pushd ../py3
%cmake -DCMAKE_BUILD_TYPE=RelWithDebInfo -DPYTHON_DESIRED:str=3 ../../
%make
make doc-man
popd
%endif

%if %{with tests}
%check
# The test suite doesn't automatically know to look at the "built"
# library, so we force it by creating an LD_LIBRARY_PATH
export LD_LIBRARY_PATH=%{_libdir}:%{buildroot}%{_libdir}
pushd ./build
make ARGS="-V" test
popd
%if %{with python3}
# Run just the Python tests, not all of them, since
# we have coverage of the core from the first build
pushd ./py3/build/tests/python
make ARGS="-V" test
popd
%endif
%endif

%install
pushd ./build
%makeinstall_std
popd
%if %{with python3}
pushd ./py3/build
%makeinstall_std
popd
%endif

%files -n %{libname}
%doc COPYING README.rst
%{_libdir}/libhawkey.so.%{major}

%files -n %{devname}
%{_libdir}/libhawkey.so
%{_libdir}/pkgconfig/hawkey.pc
%{_includedir}/hawkey/
%{_mandir}/man3/hawkey.3*

%files -n python2-hawkey
%{python2_sitearch}/hawkey

%if %{with python3}
%files -n python-hawkey
%{python3_sitearch}/hawkey
%endif

