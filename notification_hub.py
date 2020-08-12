# https://github.com/dunst-project/dunst/blob/master/src/dbus.c
# https://lazka.github.io/pgi-docs/GLib-2.0/classes/VariantType.html
# https://stackoverflow.com/questions/28949009/glib-gio-critical-error-while-invoking-a-method-on-dbus-interface
# https://lazka.github.io/pgi-docs/AyatanaAppIndicator3-0.1/classes/Indicator.html

import sys

import gi

gi.require_version('AyatanaAppIndicator3', '0.1')

from gi.repository import Gio  # noqa
from gi.repository import GLib  # noqa
from gi.repository import AyatanaAppIndicator3 as AppIndicator3  # noqa

VERSION = '0.0.0'

FDN_PATH = '/org/freedesktop/Notifications'
FDN_IFAC = 'org.freedesktop.Notifications'

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
</node>"""

next_id = 1
indicator = None


def on_call(
    conn, sender, path, interface, method, params, invocation, user_data=None
):
    global next_id
    if method == 'GetCapabilities':
        # announce fake capabilities to avoid firefox fallback
        reply = GLib.Variant('(as)', [['actions', 'body', 'body-hyperlinks']])
    elif method == 'Notify':
        indicator.set_status(AppIndicator3.IndicatorStatus.ATTENTION)
        reply = GLib.Variant('(u)', [next_id])
        next_id += 1
    elif method == 'CloseNotification':
        reply = None
    elif method == 'GetServerInformation':
        info = ['notification-hub', 'xi', VERSION, '1.2']
        reply = GLib.Variant('(ssss)', info)
    else:
        print(f'Unknown method: {method}')
        return
    invocation.return_value(reply)
    conn.flush()


def on_bus_acquired(conn, name, user_data=None):
    node_info = Gio.DBusNodeInfo.new_for_xml(INTROSPECTION_XML)
    conn.register_object(FDN_PATH, node_info.interfaces[0], on_call)


def on_name_acquired(conn, name, user_data=None):
    print(f'Aquired name {name}')


def on_name_lost(conn, name, user_data=None):
    sys.exit('name lost')


if __name__ == '__main__':
    owner_id = Gio.bus_own_name(
        Gio.BusType.SESSION,
        FDN_IFAC,
        Gio.BusNameOwnerFlags.NONE,
        on_bus_acquired,
        on_name_acquired,
        on_name_lost,
    )

    indicator = AppIndicator3.Indicator.new(
        'notify',
        'user-available',
        AppIndicator3.IndicatorCategory.APPLICATION_STATUS,
    )
    indicator.set_status(AppIndicator3.IndicatorStatus.PASSIVE)

    try:
        loop = GLib.MainLoop()
        loop.run()
    finally:
        Gio.bus_unown_name(owner_id)
