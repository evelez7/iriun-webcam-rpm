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
#BuildRequires:  ar 
# Needed to extract files from .deb (ar x %{SOURCE0})

# Runtime dependencies
Requires:       alsa-lib
Requires:       avahi
Requires:       libusbmuxd
Requires:       qt5-qtbase
Requires:       akmod-v4l2loopback 
# Fedora equivalent of v4l2loopback-dkms
#Requires:       mod_proxy_http
# Likely needed for HTTP proxying (wireless stream) - common dependency for this type of app
# Recommends are for optional but useful dependencies
Recommends:     android-tools-adb
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
# Copy the control files for reference, though we don't install them
#cp control DEBIAN/control
#cp postinst DEBIAN/postinst

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
# For now, we'll just go with the PNG from the .deb

# Install license
install -m 644 LICENSE.iriun.txt %{buildroot}%{_datadir}/licenses/%{name}/

%post
# Update desktop and icon caches
# Note: These macros handle updating the caches more robustly than raw commands.
%update_desktop_database
%gtk_update_icon_cache

# The following lines are from the original postinst, but cannot be directly
# replicated in a generic RPM %post due to dynamic config modification and
# potential module unloading issues during installation.
# The modules will be loaded via modules-load.d at boot.
# If dynamic 'snd-aloop' index setting is critical, it would require a separate
# helper script run by the user or more advanced systemd integration.
# sudo rmmod v4l2loopback
# sudo modprobe v4l2loopback
# sudo modprobe snd-aloop
# ID=$(grep -F "[Loopback" < /proc/asound/cards | awk '{print $1}')
# if [ $(echo "$ID" | grep -E "^[0-9]$") ]
# then
#     sed -i "s/#cardid/options snd-aloop index=$ID/g" /etc/modprobe.d/iriunwebcam-options.conf
# else
#     echo "Please check ALSA Loopback card number"
# fi

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
* Fri May 24 2025 Erick Velez <erickvelez7@gmail.com> - 2.8.6-1
- Initial RPM package based on Debian .deb extraction
