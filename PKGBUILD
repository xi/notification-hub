pkgname='notification-hub'
pkgver='0.0.0'
pkgdesc='Distraction-free notification daemon for simple linux desktops'
arch=('all')
url='https://github.com/xi/notification-hub'
license='MIT'

package() {
	install -Dm 755 notification_hub.py "$pkgdir/usr/bin/notification-hub"
	install -Dm 644 dbus.service "$pkgdir/usr/share/dbus-1/services/org.xi.notification-hub.service"
	install -Dm 644 systemd.service "$pkgdir/usr/lib/systemd/user/notification-hub.service"
}
