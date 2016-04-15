# Homesmarts: Cheap Lightswitchs for Phillips Hue Lights

`homesmarts` is a python program to allow me to use a cheap Amazon Dash button as a lightswitch for my Phillips Hue lights. Rather than spend $60 on an "official" Phillips Hue switch, I decided to buy multiple $5 Amazon Dash buttons and hack them to operate my Hue lights (instead of order things off Amazon). It runs on my Raspberry Pi 3.

## Disclaimer

This idea was **heavily** incluenced from:
- [Ted Benson's original blog](https://medium.com/@edwardbenson/how-i-hacked-amazon-s-5-wifi-button-to-track-baby-data-794214b0bdd8#.t5yyzqcde) on how he hacked Amazon Dash buttons to track baby data
- The "listen for ARP requests" code was based on Bob Steinbeiser's comment from the above blog

## Dependencies
- [rabbitmq-server](http://rabbitmq.com): Implementation of AMQP
- [pika](https://pika.readthedocs.org): Pika Python AMQP Client Library
- [phue](https://github.com/studioimaginaire/phue): A Phillips Hue python library

## Install
To install on a Debian system (I'm running everything on my [Raspberry Pi](raspberrypi.org)):
- Install and run `rabbitmq-server`
- Clone this repository

## Configure and Run
First off, I highly recommend you read [Ted Benson's original blog](https://medium.com/@edwardbenson/how-i-hacked-amazon-s-5-wifi-button-to-track-baby-data-794214b0bdd8#.t5yyzqcde). It's a great read and does a great job giving an overview how everything works together. (Keep in mind, we'll be interacting with Phillips Hue lights instead of tracking baby poops. :)

> `IMPORTANT`: Before running any `homesmarts` python program for the first time, be sure to press your Phillips Hue bridge button. This allows the `phue` library to create a Hue username so it can access the Phillips Hue API.

- Discover MAC address for all Dash buttons. You can run [dash-listener](./homesmarts/dash_listener.py), which should log unknown MAC addresses to standard output.
- Edit your local [homesmarts_config.yaml](./homesmarts_config.yaml) with your own details. Be sure to include:
  - IP address of your Phillips Hue bridge
  - Defaults to use for when toggling your Phillips Hue lights under `light-defaults` YAML section
  - Add all Amazon Dash buttons to your `switches` YAML section. Each Amazon Dash button can be associated with a single light (using `light_id`) or a group of lights (using `group_id`).
- Once everything is configured, run: `sudo python homesmarts/dash_listener.py`

### Helpful Links
Here are some links I found to be very helpful when writing and setting up `homesmarts`:
- Phillips Hue: [Developer's Getting Started](http://www.developers.meethue.com/documentation/getting-started)
- Phillips Hue: [Full Phillips Hue API](http://www.developers.meethue.com/philips-hue-api) (`NOTE`: requires user registration)
- [phue](https://github.com/studioimaginaire/phue): A Phillips Hue python library
- [RabbitMQ Tutorial](https://www.rabbitmq.com/tutorials/tutorial-one-python.html)

## FAQs

#### It won't connect to my Phillips Hue bridge
Be sure you have the correct IP address for your bridge in `homesmarts_config.yaml`. Also be sure you press the Bridge's button before running the program the first time.

#### It fails with the error "No privileges"
You need to run `dash_listener.py` with **sudo** privileges to enable listening for all ARP requests.

#### Why use a RabbitMQ dependency? It doesn't seem necessary...
It isn't necessary. I wanted to get experience with AMQP / enterprise messaging. Originally I planned on separate executables; one for listening for ARP messages (which requires `sudo` privileges) and publishes messages to the queue, and one for processing the messages (which could be run without `sudo`.

However, I later opted to keep everything in a single executable to make my life easier... but I still wanted to keep my AMQP code as a reference.
