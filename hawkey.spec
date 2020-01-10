# libsolv minimum version
%global libsolv_version 0.6.21-1

# The C API and valgrind tests currently fail,
# while the Python tests pass. FIX AND ENABLE ASAP!
%bcond_with tests

%define major 2
%define libname %mklibname hawkey %{major}
%define devname %mklibname hawkey -d
# Fedora package release versions are committed as versions in upstream
%define origrel 1

Name:		hawkey
Version:	0.6.4
Release:	2
Summary:	Library providing simplified C and Python API to libsolv
Group:		System/Libraries
License:	LGPLv2+
URL:		https://github.com/rpm-software-management/%{name}
Source0:	https://github.com/rpm-software-management/%{name}/archive/%{name}-%{version}-%{origrel}.tar.gz

# Patches from Mageia
Patch0500:      hawkey-0.6.3-CMake-Add-option-for-docs.patch

BuildRequires:	solv-devel >= %{libsolv_version}
BuildRequires:	cmake
%ifarch %{ix86}
BuildRequires:	gcc
BuildRequires:	gcc-c++
%endif
BuildRequires:	pkgconfig(expat)
BuildRequires:	pkgconfig(rpm)
BuildRequires:	pkgconfig(zlib)
BuildRequires:	pkgconfig(check)

%if %{with tests}
# Needed for some of the tests
BuildRequires:	valgrind
%endif

# We prevent provides/requires from nonstandard paths:
%define __noautoprovfiles %{python2_sitearch}/.*\\.so\\|%{python3_sitearch}/.*\\.so
%define __noautoreqfiles %{python2_sitearch}/hawkey/test/.*\\.so\\|%{python3_sitearch}/hawkey/test/.*\\.so

%description
A Library providing simplified C and Python API to libsolv.


%package -n %{libname}
Summary:	Libraries for %{name}
Group:		System/Libraries
Requires:	%{_lib}solv0%{?_isa} >= %{libsolv_version}
Requires:	%{_lib}solvext0%{?_isa} >= %{libsolv_version}

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
BuildRequires:	pkgconfig(python2)
%if %{with tests}
BuildRequires:	python2-nose
%endif
Requires:	%{libname}%{?_isa} = %{version}-%{release}

%description -n python2-hawkey
Python 2 bindings for the hawkey library.

%package -n python-hawkey
Summary:	Python 3 bindings for the hawkey library
Group:		Development/Python
Provides:	python3-%{name} = %{version}-%{release}
BuildRequires:	pkgconfig(python3)
%if %{with tests}
BuildRequires:	python-nose
%endif
BuildRequires:	python-sphinx
Requires:	%{libname}%{?_isa} = %{version}-%{release}

%description -n python-hawkey
Python 3 bindings for the hawkey library.

%prep
%setup -q -n %{name}-%{name}-%{version}-%{origrel}
%autopatch -p1

rm -rf py2
mkdir py2

%build
# Clang doesn't work with this on x86_32
%ifarch %{ix86}
export CC=gcc
export CXX=g++
%endif

%cmake -DCMAKE_BUILD_TYPE=RelWithDebInfo -DENABLE_SOLV_URPMREORDER=1 -DPYTHON_DESIRED:str=3
%make
make doc-man

pushd ../py2
%cmake -DCMAKE_BUILD_TYPE=RelWithDebInfo -DENABLE_SOLV_URPMREORDER=1 -DPYTHON_DESIRED:str=2 -DPYTHON_EXECUTABLE:str="python2" -DENABLE_DOCUMENTATION=0 ../../
%make
popd

%if %{with tests}
%check
# The test suite doesn't automatically know to look at the "built"
# library, so we force it by creating an LD_LIBRARY_PATH
export LD_LIBRARY_PATH=%{_libdir}:%{buildroot}%{_libdir}
pushd ./build
make ARGS="-V" test
popd

# Run just the Python tests, not all of them, since
# we have coverage of the core from the first build
pushd ./py2/build/tests/python
make ARGS="-V" test
popd
%endif

%install
pushd ./build
%makeinstall_std
popd

pushd ./py2/build
%makeinstall_std
popd


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

%files -n python-hawkey
%{python_sitearch}/hawkey
