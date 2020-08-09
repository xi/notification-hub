# https://github.com/dunst-project/dunst/blob/master/src/dbus.c
# https://lazka.github.io/pgi-docs/GLib-2.0/classes/VariantType.html
# https://stackoverflow.com/questions/28949009/glib-gio-critical-error-while-invoking-a-method-on-dbus-interface

import sys
import sqlite3
from datetime import datetime

from gi.repository import Gio
from gi.repository import GLib

VERSION = '0.0.0'

FDN_PATH = '/org/freedesktop/Notifications'
FDN_IFAC = 'org.freedesktop.Notifications'
FDN_IFAC2 = 'org.xi.Hub'

INTROSPECTION_XML = """<?xml version="1.0" encoding="UTF-8"?>
<node name="/org/freedesktop/Notifications">
    <interface name="org.freedesktop.Notifications">
        <method name="GetCapabilities">
            <arg direction="out" name="capabilities"    type="as"/>
        </method>
        <method name="Notify">
            <arg direction="in"  name="app_name"        type="s"/>
            <arg direction="in"  name="replaces_id"     type="u"/>
            <arg direction="in"  name="app_icon"        type="s"/>
            <arg direction="in"  name="summary"         type="s"/>
            <arg direction="in"  name="body"            type="s"/>
            <arg direction="in"  name="actions"         type="as"/>
            <arg direction="in"  name="hints"           type="a{sv}"/>
            <arg direction="in"  name="expire_timeout"  type="i"/>
            <arg direction="out" name="id"              type="u"/>
        </method>
        <method name="CloseNotification">
            <arg direction="in"  name="id"              type="u"/>
        </method>
        <method name="GetServerInformation">
            <arg direction="out" name="name"            type="s"/>
            <arg direction="out" name="vendor"          type="s"/>
            <arg direction="out" name="version"         type="s"/>
            <arg direction="out" name="spec_version"    type="s"/>
        </method>
        <signal name="NotificationClosed">
            <arg name="id"         type="u"/>
            <arg name="reason"     type="u"/>
        </signal>
        <signal name="ActionInvoked">
            <arg name="id"         type="u"/>
            <arg name="action_key" type="s"/>
        </signal>
   </interface>
   <interface name="org.xi.Hub">
        <method name="GetNotifications">
            <arg direction="out" name="notifications"   type="a(usss)"/>
        </method>
        <method name="CountNotifications">
            <arg direction="out" name="count"           type="u"/>
        </method>
        <method name="DeleteNotification">
            <arg direction="in"  name="id"              type="u"/>
        </method>
        <signal name="Changed">
            <arg name="count"      type="u"/>
        </signal>
   </interface>
</node>"""

# close reasons
EXPIRED = 1
DISMISSED = 2
CLOSED = 3
UNDEFINED = 4

node_info = Gio.DBusNodeInfo.new_for_xml(INTROSPECTION_XML)
dbus_conn = None
db = sqlite3.connect(':memory:')


def delete(_id):
    db.execute('DELETE from notifications WHERE id=?', (_id,))
    sig_changed()


def add(sender, app_name, replaces_id, icon, summary, body, actions, hints, timeout):
    if replaces_id == 0:
        sql = 'INSERT INTO notifications (sender, app_name, summary, dt) VALUES (?, ?, ?, ?)'
        db.execute(sql, (sender, app_name, summary, datetime.now()))
        db.commit()
        sig_changed()
        row = db.execute('SELECT last_insert_rowid()').fetchone()
        return row[0]
    else:
        sql = 'UPDATE notifications SET sender=?, app_name=?, summary=?, dt=? WHERE id=?'
        db.execute(sql, (sender, app_name, summary, datetime.now(), replaces_id))
        db.commit()
        sig_changed()
        return replaces_id


def count():
    row = db.execute('SELECT COUNT(*) FROM notifications').fetchone()
    return row[0]


def getall():
    return db.execute('SELECT id, app_name, summary, dt FROM notifications').fetchall()


def on_call(conn, sender, path, interface, method, parameters, invocation, user_data=None):
    if method == 'GetCapabilities':
        reply = GLib.Variant('()', [])
    elif method == 'Notify':
        print(sender, parameters)
        value = add(sender, *parameters)
        reply = GLib.Variant('(u)', [value])
    elif method == 'CloseNotification':
        delete(*parameters)
        reply = None
    elif method == 'GetServerInformation':
        info = ['notification-hub', 'xi', VERSION, '1.2']
        reply = GLib.Variant('(ssss)', info)
    elif method == 'CountNotifications':
        reply = GLib.Variant('(u)', [count()])
    elif method == 'GetNotifications':
        l = getall()
        builder = GLib.VariantBuilder(GLib.VariantType('a(usss)'))
        for notification in l:
            builder.add_value(GLib.Variant('(usss)', notification))
        reply = builder.end()
        reply = GLib.Variant.new_tuple(reply)
    elif method == 'DeleteNotification':
        delete(*parameters)
        sig_notification_closed(*parameters, DISMISSED)
        reply = None
    else:
        print(f'Unknown method: {method}')
        return
    invocation.return_value(reply)
    conn.flush()


def sig_notification_closed(_id, reason):
    # TODO: send only to owner of notification
    body = GLib.Variant('(uu)', (_id, reason))
    dbus_conn.emit_signal(None, FDN_PATH, FDN_IFAC, 'NotificationClosed', body);


def sig_changed():
    body = GLib.Variant('(u)', [count()])
    dbus_conn.emit_signal(None, FDN_PATH, FDN_IFAC2, 'Changed', body);


def on_bus_acquired(conn, name, user_data=None):
    global dbus_conn
    dbus_conn = conn

    conn.register_object(FDN_PATH, node_info.interfaces[0], on_call)
    conn.register_object(FDN_PATH, node_info.interfaces[1], on_call)


def on_name_lost(conn, name, user_data=None):
    sys.exit('name lost')


if __name__ == '__main__':
    db.execute("""CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY,
        sender TEXT,
        app_name TEXT,
        summary TEXT,
        dt TEXT
    );""")

    owner_id = Gio.bus_own_name(
        Gio.BusType.SESSION,
        FDN_IFAC,
        Gio.BusNameOwnerFlags.NONE,
        on_bus_acquired,
        None,
        on_name_lost,
    )

    loop = GLib.MainLoop()
    loop.run()

    Gio.bus_unown_name(owner_id);
