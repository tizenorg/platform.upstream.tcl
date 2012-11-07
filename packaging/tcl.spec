Name:           tcl
Version:        8.5.11
Release:        0
License:        SUSE-TCL
Summary:        The Tcl Programming Language
Url:            http://www.tcl.tk
Group:          Development/Languages/Tcl
Source0:        %{name}%{version}-src.tar.gz
Source1:        tcl-rpmlintrc
Source2:        baselibs.conf
Source3:        macros.tcl
BuildRequires:  autoconf
Requires(pre):  /usr/bin/rm
Provides:       tclsh
Provides:       tclsh%{TCL_MINOR}
%define TCL_MINOR %(echo %{version} | cut -c1-3)
BuildRoot:      %{_tmppath}/%{name}-%{version}-build

%description
Tcl (Tool Command Language) is a very powerful but easy to learn
dynamic programming language, suitable for a very wide range of uses,
including web and desktop applications, networking, administration,
testing and many more. Open source and business-friendly, Tcl is a
mature yet evolving language that is truly cross platform, easily
deployed and highly extensible.

For more information on Tcl see http://www.tcl.tk and
http://wiki.tcl.tk .

%package devel
Summary:        Header Files and C API Documentation for Tcl
Group:          Development/Libraries/Tcl
Requires:       tcl = %{version}

%description devel
This package contains header files and documentation needed for writing
Tcl extensions in compiled languages like C, C++, etc., or for
embedding the Tcl interpreter in programs written in such languages.

This package is not needed for writing extensions or applications in
the Tcl language itself.

%prep
%setup -q -n %{name}%{version}
%patch0
%patch1

%build
cd unix
autoconf
%configure \
	--enable-man-symlinks \
	--enable-man-compression=gzip
%define scriptdir %{_libdir}/tcl
MAKE='make %{?_smp_mflags}
	TCL_LIBRARY="%scriptdir/tcl%TCL_MINOR"
	TCL_PACKAGE_PATH="%{_libdir}/tcl %{_datadir}/tcl"
	CFLAGS="%{optflags} $PFLAGS"
	LDFLAGS_OPTIMIZE="%{optflags} $PFLAGS"
	SHLIB_LD="gcc -shared %{optflags} $PFLAGS"'
# Build with instrumentation for profiling
PFLAGS="%{?cflags_profile_generate}"
eval $MAKE
# Some of the regressioin tests write to $HOME, so better redirect them
#mkdir home
#export HOME=$PWD/home
# Run the testsuite to gather some data for the profile-based
# optimisation and let rpmbuild fail on unexpected test failures.
#cat > known-failures <<EOF
#httpold-4.12
#mathop-25.14
#EOF
#%ifnarch %arm
#eval $MAKE test 2>&1 | tee testresults
#grep FAILED testresults | grep -Fqvwf known-failures && exit 1
#%endif
# If we don't do profile based optimisation, we are done at this point.
if test -n "$PFLAGS"; then
    # Rebuild and use the profiling results
    make clean
    PFLAGS="%cflags_profile_feedback"
    eval $MAKE
fi

%install
make -C unix install install-private-headers \
	INSTALL_ROOT=%{buildroot} \
	TCL_LIBRARY="%scriptdir/tcl%TCL_MINOR"
rm -f %{buildroot}%scriptdir/tcl%TCL_MINOR/ldAix
ln -sf tclsh%TCL_MINOR %{buildroot}%{_bindir}/tclsh
mkdir -p %{buildroot}%{_datadir}/tcl
install -D %{SOURCE3} -m 644 %{buildroot}%{_sysconfdir}/rpm/macros.tcl

%files
%defattr(-,root,root,755)
%doc README  license.terms
%doc %{_mandir}/man1/*
%doc %{_mandir}/mann/*
%{_bindir}/*
%{_libdir}/lib*.so
%{_datadir}/tcl
%scriptdir
%exclude %scriptdir/*/tclAppInit.c
%config %{_sysconfdir}/rpm/macros.tcl

%files devel
%defattr(-,root,root)
%doc %{_mandir}/man3/*
%{_includedir}/*
%scriptdir/*/tclAppInit.c
%{_libdir}/*.a
%{_libdir}/tclConfig.sh

%changelog
