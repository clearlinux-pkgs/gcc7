%define keepstatic 1
%define gcc_target x86_64-generic-linux
%define libstdcxx_maj 6
%define libstdcxx_full 6.0.24
%define isl_version 0.16.1
%define gccver 7.5.0
%define gccpath gcc-7.5.0

# Highest optimisation ABI we target
%define mtune haswell

# Lowest compatible ABI (must be lowest of current targets & OBS builders)
# avoton (silvermont target) && ivybridge (OBS builders) = westmere
%define march westmere
%define abi_package %{nil}

Name     : gcc7
Version  : 7.5.0
Release  : 442
URL      : http://www.gnu.org/software/gcc/
Source0  : https://mirrors.kernel.org/gnu/gcc/gcc-7.5.0/gcc-7.5.0.tar.gz
Source1  : https://gcc.gnu.org/pub/gcc/infrastructure/isl-0.16.1.tar.bz2
Source2  : DATESTAMP
Source3  : REVISION
Summary  : GNU cc and gcc C compilers
Group    : Development/Tools
License  : BSD-3-Clause BSL-1.0 GFDL-1.2 GFDL-1.3 GPL-2.0 GPL-3.0 LGPL-2.1 LGPL-3.0 MIT

Patch0   : gcc-stable-branch.patch
Patch1   : 0001-Fix-stack-protection-issues.patch
Patch2   : openmp-vectorize.patch
Patch3   : fortran-vector.patch
Patch5   : optimize.patch
Patch6   : ipa-cp.patch
Patch7   : max-is-safe-on-x86.patch
Patch8	 : optimize-at-least-some.patch
Patch9   : gomp-relax.patch
Patch10	 : distribute.patch
Patch11  : memcpy-avx2.patch


Patch15  : revert-regression.patch
# simplified version of gcc 8 upstream patch
Patch16  : skylake.patch
Patch17  : pow-optimization.patch
# backport from gcc 8
patch18  : 0001-Option-mprefer-avx256-added-for-Intel-AVX512-configu.patch
Patch19  : prefer-256.patch

# simplified version of gcc 8 upstream patch
Patch20  : narrow-vpxor.patch

# zero registers on ret to make ROP harder
Patch21  : zero-regs.patch

# drop on next rebase
Patch100 : debug-fma.patch


BuildRequires : bison
BuildRequires : flex
BuildRequires : gmp-dev
BuildRequires : libstdc++
BuildRequires : libunwind-dev
BuildRequires : mpc-dev
BuildRequires : mpfr-dev
BuildRequires : pkgconfig(zlib)
BuildRequires : sed
BuildRequires : texinfo
BuildRequires : dejagnu
BuildRequires : expect
BuildRequires : autogen
BuildRequires : guile
BuildRequires : tcl
BuildRequires : valgrind-dev
BuildRequires : libxml2-dev
BuildRequires : libxslt
BuildRequires : graphviz
BuildRequires : gdb-dev
BuildRequires : procps-ng
BuildRequires : docbook-xml docbook-utils doxygen


Requires: gcc-libubsan
Requires: gcc-doc

%description
GNU cc and gcc C compilers.

%package dev
License:        GPL-3.0-with-GCC-exception and GPL-3.0
Summary:        GNU cc and gcc C compilers
Group:          devel
Provides:       libgcov-dev
Provides:       libssp-dev
Provides:       libssp-staticdev
Provides:       libgomp-dev
Provides:       libgomp-staticdev
Provides:       libgcc-s-dev
Provides:       gcc-plugin-dev
Provides:       libstdc++-dev
Requires:       gcc-libs-math
Requires:       libstdc++

%description dev
GNU cc and gcc C compilers dev files




%package libgcc1
License:        GPL-3.0-with-GCC-exception and GPL-3.0
Summary:        GNU cc and gcc C compilers
Group:          devel
Requires:       filesystem
Provides:       libssp0
Provides:       libgomp1

%description libgcc1
GNU cc and gcc C compilers.

%package libubsan
License:        GPL-3.0-with-GCC-exception and GPL-3.0
Summary:        GNU cc and gcc C compilers
Group:          devel

%description libubsan
Address sanitizer runtime libs

%package libstdc++
License:        GPL-3.0-with-GCC-exception and GPL-3.0
Summary:        GNU cc and gcc C compilers
Group:          devel

%description libstdc++
GNU cc and gcc C compilers.

%package doc
License:        GPL-3.0-with-GCC-exception and GPL-3.0
Summary:        GNU cc and gcc C compilers
Group:          doc

%package go
License:        GPL-3.0-with-GCC-exception and GPL-3.0
Summary:        GNU Compile Collection GO compiler
Group:          devel

%description go
GNU Compile Collection GO compiler

%package go-lib
License:        GPL-3.0-with-GCC-exception and GPL-3.0
Summary:        GNU Compile Collection GO runtime
Group:          devel

%description go-lib
GNU Compile Collection GO runtime

%description doc
GNU cc and gcc C compilers.

%package locale
License:        GPL-3.0-with-GCC-exception and GPL-3.0
Summary:        GNU cc and gcc C compilers
Group:          libs

%description locale
GNU cc and gcc C compilers.

%package libs-math
License:        GPL-3.0-with-GCC-exception and GPL-3.0
Summary:        GNU cc and gcc C compilers
Group:          libs

%description libs-math
GNU cc and gcc C compilers.


%prep
%setup -q -n %{gccpath}
#%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch5 -p1
%patch6 -p1
%patch8 -p1
%patch9 -p1
%patch10 -p1
%patch11 -p1
%patch15 -p1
%patch16 -p1
%patch17 -p1
%patch18 -p1
%patch19 -p1
%patch20 -p1

%patch21 -p1

%patch100 -p1



%build

# Live in the gcc source tree
tar xf %{SOURCE1} && ln -sf isl-%{isl_version} isl

# Update the DATESTAMP and add a revision
tee `find -name DATESTAMP` > /dev/null < %{SOURCE2}
cp %{SOURCE3} gcc/

rm -rf ../gcc-build
mkdir ../gcc-build
pushd ../gcc-build
unset CFLAGS
unset CXXFLAGS
export CFLAGS="-march=westmere -g1 -O3 -fstack-protector -Wl,-z -Wl,now -Wl,-z -Wl,relro  -Wl,-z,max-page-size=0x1000 -mtune=skylake"
export CXXFLAGS="-march=westmere -g1 -O3  -Wl,-z,max-page-size=0x1000 -mtune=skylake"
export CFLAGS_FOR_TARGET="$CFLAGS"
export CXXFLAGS_FOR_TARGET="$CXXFLAGS"
export FFLAGS_FOR_TARGET="$FFLAGS"

export CPATH=/usr/include
export LIBRARY_PATH=/usr/lib64

../%{gccpath}/configure \
    --program-suffix=7 \
    --prefix=/usr \
    --with-pkgversion='Clear Linux OS for Intel Architecture'\
    --libdir=/usr/lib64/ \
    --enable-libstdcxx-pch\
    --libexecdir=/usr/lib64 \
    --with-system-zlib\
    --enable-shared\
    --enable-gnu-indirect-function \
    --disable-vtable-verify \
    --enable-threads=posix\
    --enable-__cxa_atexit\
    --enable-plugin\
    --enable-ld=default\
    --enable-clocale=gnu\
    --disable-multiarch\
    --disable-multilib\
    --enable-lto\
    --enable-linker-build-id \
    --build=%{gcc_target}\
    --target=%{gcc_target}\
    --enable-languages="c,c++" \
    --enable-bootstrap \
    --with-ppl=yes \
    --with-isl \
    --includedir=/usr/include \
    --exec-prefix=/usr \
    --with-glibc-version=2.28 \
    --disable-libunwind-exceptions \
    --disable-libsanitizer \
    --with-gnu-ld \
    --with-tune=haswell \
    --with-arch=westmere \
    --enable-cet \
    --with-gcc-major-version-only \
    --enable-default-pie \
    --disable-libmpx
# For GCC 9, add:
#  --with-gcc-major-version-only
#  --enable-default-pie

make %{?_smp_mflags} profiledbootstrap

popd

#%check
#pushd ../gcc-build
#export CHECK_TEST_FRAMEWORK=1
#make -k  %{?_smp_mflags} check  || :
#popd


%install
export CPATH=/usr/include
export LIBRARY_PATH=/usr/lib64
pushd ../gcc-build
%make_install
cd -

cd %{buildroot}/usr/bin

find %{buildroot}/usr/ -name libiberty.a | xargs rm -f
find %{buildroot}/usr/ -name libiberty.h | xargs rm -f

chmod a+x %{buildroot}/usr/bin
chmod a+x %{buildroot}/usr/lib64
find %{buildroot}/usr/lib64 %{buildroot}/usr/lib*/gcc -name '*.so*' -print0 | xargs -r0 chmod 755
find %{buildroot}/usr/lib64 %{buildroot}/usr/lib*/gcc -name '*.o' -print0 | xargs -r0 chmod 644


# This is only for gdb
mkdir -p %{buildroot}//usr/share/gdb/auto-load//usr/lib64

rm -rf %{buildroot}/usr/share/locale 

rm -f %{buildroot}/usr/bin/abifiles.list
rm -f %{buildroot}/usr/bin/c++7
rm -f %{buildroot}/usr/bin/gcov-dump7
rm -f %{buildroot}/usr/lib64/libatomic.so
rm -f %{buildroot}/usr/lib64/libitm.so
rm -f %{buildroot}/usr/lib64/libitm.spec
rm -f %{buildroot}/usr/lib64/libquadmath.so
rm -f %{buildroot}/usr/lib64/libstdc++.so

%files
/usr/bin/%{gcc_target}-gcc-ar7
/usr/bin/%{gcc_target}-gcc-ranlib7
/usr/bin/%{gcc_target}-gcc-nm7
/usr/bin/%{gcc_target}-gcc7

/usr/bin/%{gcc_target}-gcc-7
/usr/bin/gcc7
/usr/bin/gcc-ar7
/usr/bin/gcc-nm7
/usr/bin/gcc-ranlib7
/usr/bin/gcov7
/usr/bin/gcov-tool7
/usr/bin/cpp7
#/usr/lib64/libvtv*
%exclude /usr/lib64/libcc1*
/usr/lib64/gcc/%{gcc_target}/7/include-fixed/
/usr/lib64/gcc/%{gcc_target}/7/install-tools/
/usr/lib64/gcc/%{gcc_target}/7/include/
/usr/lib64/gcc/%{gcc_target}/7/lto1
/usr/lib64/gcc/%{gcc_target}/7/lto-wrapper
/usr/lib64/gcc/%{gcc_target}/7/collect2
/usr/lib64/gcc/%{gcc_target}/7/cc1plus
/usr/lib64/gcc/%{gcc_target}/7/liblto_plugin.so.0.0.0
/usr/lib64/gcc/%{gcc_target}/7/liblto_plugin.so.0
/usr/lib64/gcc/%{gcc_target}/7/cc1
/usr/lib64/gcc/%{gcc_target}/7/plugin/gtype.state
/usr/lib64/gcc/%{gcc_target}/7/plugin/*.so.*
/usr/lib64/gcc/%{gcc_target}/7/plugin/include/
/usr/bin/x86_64-generic-linux-c++7

/usr/share/gcc-7
%exclude /usr/lib64/*.a
%exclude /usr/lib64/*.o


#g++
/usr/bin/%{gcc_target}-g++7
/usr/bin/g++7

# gcc-dev
/usr/lib64/gcc/%{gcc_target}/7/liblto_plugin.so
/usr/lib64/gcc/%{gcc_target}/7/plugin/*.so

%files dev
# libgcc-s-dev
/usr/lib64/gcc/x86_64-generic-linux/7/libgcc.a
/usr/lib64/gcc/x86_64-generic-linux/7/crtendS.o
/usr/lib64/gcc/x86_64-generic-linux/7/libgcc_eh.a
/usr/lib64/gcc/x86_64-generic-linux/7/crtprec32.o
/usr/lib64/gcc/x86_64-generic-linux/7/crtend.o
/usr/lib64/gcc/x86_64-generic-linux/7/crtbegin.o
/usr/lib64/gcc/x86_64-generic-linux/7/crtprec80.o
/usr/lib64/gcc/x86_64-generic-linux/7/crtfastmath.o
/usr/lib64/gcc/x86_64-generic-linux/7/crtbeginS.o
/usr/lib64/gcc/x86_64-generic-linux/7/crtprec64.o
/usr/lib64/gcc/x86_64-generic-linux/7/crtbeginT.o
%exclude /usr/lib64/libgcc_s.so
/usr/lib64/gcc/x86_64-generic-linux/7/libgcov.a
/usr/lib64/gcc/%{gcc_target}/7/include/ssp
%exclude /usr/lib64/libssp*.a
%exclude /usr/lib64/libgomp.a
# gcc-plugin-dev
/usr/lib64/gcc/%{gcc_target}/7/plugin/gengtype

# libstdc++
/usr/include/c++/*
%exclude /usr/lib64/libstdc++fs.a
%exclude /usr/bin/abifiles.list


%files libgcc1
%exclude /usr/lib64/libgcc_s.so.1

%files libs-math
%exclude /usr/lib64/libssp.so*
%exclude /usr/lib64/libgomp*so*
%exclude /usr/lib64/libgomp.spec
%exclude /usr/lib64/libatomic*.so.*
%exclude /usr/lib64/libitm*.so.*
%exclude /usr/lib64/libquadmath*.so.*

%files libstdc++
%exclude /usr/lib64/libstdc++.so.*


%files doc
%exclude %{_mandir}/man1
%exclude %{_mandir}/man7
%exclude %{_infodir}


%files libubsan
%exclude    /usr/lib64/libcilkrts.so
%exclude    /usr/lib64/libcilkrts.so.5
%exclude    /usr/lib64/libcilkrts.so.5.0.0
%exclude    /usr/lib64/libcilkrts.spec
