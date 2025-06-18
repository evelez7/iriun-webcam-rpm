Name:           iriunwebcam
Version:        2.8.6
Release:        1%{?dist}
Summary:        Use your phone's camera as a wireless webcam in your PC
License:        LicenseRef-Iriun
URL:            https://iriun.com/
Source0:        http://iriun.gitlab.io/iriunwebcam-%{version}.deb
Source1:        LICENSE.iriun.txt
BuildArch:      x86_64

%global debug_package %{nil}

# Build dependencies
BuildRequires:  patchelf

# Runtime dependencies
Requires:       alsa-lib
Requires:       avahi
Requires:       libusbmuxd
Requires:       qt5-qtbase
Requires:       akmod-v4l2loopback 
Recommends:     qt5-qtwayland 
# For Wayland display server support

%description
Iriun Webcam allows you to use your phone's camera as a wireless webcam in your PC.

Install also Iriun Webcam app to your mobile phone and start using the phone with your favourite video applications.

%prep
%setup -q -c -T
# Extract the contents of the .deb package
ar x %{SOURCE0}
tar -xf data.tar.zst
cp %{SOURCE1} .

%build
# No explicit build steps needed as we are extracting from a pre-built .deb

%install
# Create necessary directories
install -d -m 755 %{buildroot}%{_bindir}
install -d -m 755 %{buildroot}%{_datadir}/applications
install -d -m 755 %{buildroot}%{_datadir}/licenses/%{name}
install -d -m 755 %{buildroot}%{_datadir}/icons/hicolor/48x48/apps/ # Assuming 48x48 is a reasonable size for the PNG icon
install -d -m 755 %{buildroot}%{_sysconfdir}/modprobe.d/
install -d -m 755 %{buildroot}%{_sysconfdir}/modules-load.d/

# Install binary
install -m 755 usr/local/bin/iriunwebcam %{buildroot}%{_bindir}/iriunwebcam

# Apply patches/fixes
# Fix libusbmuxd dependency
patchelf --replace-needed libusbmuxd-2.0.so.6 libusbmuxd-2.0.so %{buildroot}%{_bindir}/iriunwebcam
# Fix .desktop file path (remove /usr/local/bin from Exec= line)
sed -E -e 's&/usr/local/bin/&&' -i usr/share/applications/iriunwebcam.desktop
install -m 644 usr/share/applications/iriunwebcam.desktop %{buildroot}%{_datadir}/applications/iriunwebcam.desktop

# Install configuration files
install -m 644 etc/modprobe.d/iriunwebcam-options.conf %{buildroot}%{_sysconfdir}/modprobe.d/iriunwebcam-options.conf
install -m 644 etc/modules-load.d/iriunwebcam.conf %{buildroot}%{_sysconfdir}/modules-load.d/iriunwebcam.conf

# Install icon (PNG)
install -m 644 usr/share/pixmaps/iriunwebcam.png %{buildroot}%{_datadir}/icons/hicolor/48x48/apps/iriunwebcam.png
# If you still want the SVG from the PKGBUILD, you'd need to fetch it as another Source and install it.

# Install license
install -m 644 LICENSE.iriun.txt %{buildroot}%{_datadir}/licenses/%{name}/

%post
# Update desktop and icon caches
# Note: These macros handle updating the caches more robustly than raw commands.
%update_desktop_database
%gtk_update_icon_cache

%postun
# Update desktop and icon caches on uninstallation
%update_desktop_database
%gtk_update_icon_cache

%files
%license %{_datadir}/licenses/%{name}/LICENSE.iriun.txt
%{_bindir}/iriunwebcam
%{_datadir}/applications/iriunwebcam.desktop
%{_datadir}/icons/hicolor/48x48/apps/iriunwebcam.png
%{_sysconfdir}/modprobe.d/iriunwebcam-options.conf
%{_sysconfdir}/modules-load.d/iriunwebcam.conf

%changelog
* Sat May 24 2025 Erick Velez <erickvelez7@gmail.com> 2.8.6-1
- Initial RPM package based on Debian .deb extraction
