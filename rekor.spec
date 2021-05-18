%global with_devel 0
%global with_bundled 1
%global with_check 0
%global with_unit_test 0

%global with_debug 0

%if 0%{?with_debug}
%global _find_debuginfo_dwz_opts %{nil}
%global _dwz_low_mem_die_limit 0
%else
%global debug_package %{nil}
%endif

%if ! 0%{?gobuild:1}
%define gobuild(o:) GO111MODULE=off go build -buildmode pie -compiler gc -tags="rpm_crashtraceback ${BUILDTAGS:-}" -ldflags "${LDFLAGS:-} -B 0x$(head -c20 /dev/urandom|od -An -tx1|tr -d ' \\n') -extldflags '-Wl,-z,relro -Wl,-z,now -specs=/usr/lib/rpm/redhat/redhat-hardened-ld '" -a -v -x %{?**};
%endif

%global provider github
%global provider_tld com
%global project sigstore
%global repo %{name}
%global import_path %{provider}.%{provider_tld}/%{project}/%{repo}
%global git0 https://%{import_path}

# Used for comparing with latest upstream tag
# to decide whether to autobuild and set download url (non-rawhide only)
%define built_tag v0.1.1
%define built_tag_strip %(b=%{built_tag}; echo ${b:1})
%define download_url %{git0}/archive/%{built_tag}.tar.gz

Name: rekor
Version: 0.1.1
Release: 1%{?dist}
Summary: Manage Pods, Containers and Container Images
License: ASL 2.0
URL: https://%{name}.io/
Source0: %{download_url}
BuildRequires: gcc
BuildRequires: golang
BuildRequires: glib2-devel
BuildRequires: glibc-devel
BuildRequires: glibc-static
BuildRequires: git-core

%description

%package cli
Summary: CLI for Rekor

%description cli
CLI for Rekor

%package server
Summary: Rekor Server

%description server
Rekor server

%prep
%autosetup -Sgit_am -n %{name}-%{built_tag_strip}

%build
export CGO_CFLAGS='-O2 -g -grecord-gcc-switches -pipe -Wall -Werror=format-security -Wp,-D_FORTIFY_SOURCE=2 -specs=/usr/lib/rpm/redhat/redhat-hardened-cc1 -ffat-lto-objects -fexceptions -fasynchronous-unwind-tables -fstack-protector-strong -fstack-clash-protection -D_GNU_SOURCE -D_LARGEFILE_SOURCE -D_LARGEFILE64_SOURCE -D_FILE_OFFSET_BITS=64'
%ifarch x86_64
export CGO_CFLAGS="$CGO_CFLAGS -m64 -mtune=generic"
%if 0%{?fedora} || 0%{?centos} >= 8
export CGO_CFLAGS="$CGO_CFLAGS -fcf-protection"
%endif
%endif

go build -o %{name}-cli ./cmd/cli
go build -o %{name}-server ./cmd/server

%install
install -dp %{buildroot}%{_bindir}
install -p %{name}-cli %{buildroot}%{_bindir}
install -p %{name}-server %{buildroot}%{_bindir}

%check

#define license tag if not already defined
%{!?_licensedir:%global license %doc}

%files cli
%license LICENSE
%doc CODE_OF_CONDUCT.md CONTRIBUTORS.md COPYRIGHT.txt MAINTAINERS.md OWNERS.md README.md
%{_bindir}/%{name}-cli

%files server
%license LICENSE
%doc CODE_OF_CONDUCT.md CONTRIBUTORS.md COPYRIGHT.txt MAINTAINERS.md OWNERS.md README.md
%{_bindir}/%{name}-server

%changelog
* Tue May 18 2021 Lokesh Mandvekar <lsm5@fedoraproject.org> - 0.1.1-1
- initial package

