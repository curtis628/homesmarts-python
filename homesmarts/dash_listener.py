#!/usr/bin/env python

"""
homesmarts.dash_listener
~~~~~~~~~~~~~

This module contains logic for listening (and responding) to Dash button clicks.
"""

import binascii
import logging
import socket
import struct
import threading

import config
import messaging

logger = logging.getLogger(__name__)


class DashListener(threading.Thread):
    """This class represents a 'hacked' Amazon Dash button to act as a Phillip's Hue lightswitch."""
    def __init__(self, dash_id, mac, hue_unit, config):
        """Initializes the listener object to be associated with 'dash_id' and 'hue_unit'

          - 'dash_id' is the id of the Amazon Dash button
          - 'hue_unit' is either a phue.Light or phue.Group associated with the Dash button
          - 'config' is 'smarts-config' class storing defaults to use for Lighting
        """
        threading.Thread.__init__(self)

        self.dash_id = dash_id
        self.mac = mac
        self.hue_unit = hue_unit
        self.config = config
        self.channel = messaging.create_rabbitmq_channel()
        self.daemon = True  # Exit main program if only daemon threads are running

    def __str__(self):
        return "DashListener: [dash_id={}] [hue_unit={}]".format(self.dash_id, self.hue_unit)

    def button_pressed(self, channel, method, properties, body):
        """Callback method for when Dash button is pressed. It should toggle its associated light(s)."""
        logger.info("button_pressed: [key=%s] [body=%s]", method.routing_key, body)
        current_state = self.hue_unit.on
        logger.debug("Light was [current_state=%s]. Inverting state and setting defaults...", current_state)

        # Toggle the light, and set default brightness/saturation/hue to levels from config file
        self.hue_unit.on = not current_state
        self.hue_unit.brightness = self.config.default_light_brightness()
        self.hue_unit.saturation = self.config.default_light_saturation()
        self.hue_unit.hue = self.config.default_light_hue()

    def run(self):
        """Once this thread is started, create a RabbitMQ queue and listen for messages with key of 'dash_id'"""
        result = self.channel.queue_declare(exclusive=True)
        queue_name = result.method.queue

        self.channel.queue_bind(exchange=messaging.DASH_EXCHANGE, queue=queue_name, routing_key=self.dash_id)
        self.channel.basic_consume(self.button_pressed, queue=queue_name, no_ack=True)

        logger.info("Running: %s", self)
        self.channel.start_consuming()


def listen_for_arp(mac_to_message_key_dict):
    """Listens to all ARP requests and processes logic for any configured Dash button that's been configured

    The parameter 'mac_to_message_key_dict' is a dictionary with a MAC address as the key, and the Dash Button
    id (as specified in homesmarts_config.yaml) as the value.

    NOTE: This code was heavily influenced from Bob Steinbeiser's comment on Ted Benson's "Track Baby Data" blog:
    https://medium.com/@edwardbenson/how-i-hacked-amazon-s-5-wifi-button-to-track-baby-data-794214b0bdd8#.t5yyzqcde
    """
    logger.debug("Listening for ARP requests...")
    rawSocket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0003))
    while True:
        packet = rawSocket.recvfrom(2048)
        ethernet_header = packet[0][0:14]
        ethernet_detailed = struct.unpack("!6s6s2s", ethernet_header)
        arp_header = packet[0][14:42]
        arp_detailed = struct.unpack("2s2s1s1s2s6s4s6s4s", arp_header)
        ethertype = ethernet_detailed[2]
        # skip non-ARP packets
        if ethertype != '\x08\x06':
            continue

        source_mac = binascii.hexlify(arp_detailed[5])
        dest_ip = socket.inet_ntoa(arp_detailed[8])
        if dest_ip == '192.168.0.1':
            logger.debug("Ignoring ARP with dest_ip 192.168.0.1 [mac=%s]", source_mac)
            continue

        if source_mac in mac_to_message_key_dict.keys():
            dash_id = mac_to_message_key_dict[source_mac]
            logging.info("%s Dash button pressed!", dash_id)
            messaging.publish_message(dash_id, "Button pressed")
        else:
            logger.debug("Unknown ARP for [ip=%s] [mac=%s]", dest_ip, source_mac)


if __name__ == "__main__":
    config = config.init()

    for listener in config.dash_listeners:
        listener.start()

    listen_for_arp(config.get_mac_to_message_key_dict())
