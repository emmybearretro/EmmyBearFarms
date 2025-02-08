import os
import sys
import time
import json
import bambulabs_api as bl
import configparser
import logging

import django.db.models
from django.conf import settings
from django import setup
from django.db import connection
from django.utils import timezone


# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EmmyBearFarms.settings')
setup()  # Initialize Django

# Now you should be able to import from your Django app
from bambu.models import Printer, PrinterCommand, PrinterState

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def make_hashable(obj):
    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    elif isinstance(obj, dict):
        return tuple(sorted((k, make_hashable(v)) for k, v in obj.items()))
    elif isinstance(obj, list):
        return tuple(make_hashable(item) for item in obj)
    else:
        return str(obj)  # Convert any other types to strings

def process_command_queue(printer_mqtt:bl.Printer,django_printer:Printer):
    command = None
    try:
        command = PrinterCommand.objects.filter(
            printer=django_printer,
            completed=False,
            archived=False
        ).order_by('position').first()
    except PrinterCommand.DoesNotExist:
        pass
    logging.info("Processing command: %s", command)


    if command is not None:
        can_run = False
        if command.predefined_command.can_run_when_blocked:
            logging.info("Command is being run, even if we are blocked")
            can_run = True
        elif django_printer.blocked == False:
            logging.info("Printer is not blocked")
            can_run = True
        else:
            logging.info("Printer is blocked, doing nothing")

        if can_run:
            logging.info("Running command: %s", command)
            #do the command
            cmdtxt = command.predefined_command.command
            i = 0
            printer_mqtt.call_method_by_name(cmdtxt)

            #printer_mqtt.call_method_by_name("start_print", "example.gcode", 1, True, [0], None)

            i = 0
            if command.predefined_command.blocks_when_run:
                logging.error("SAVING")
                django_printer.blocked = True
                django_printer.save()
                logging.error("BLOCKED")

            command.completed = True
            command.completed_at = timezone.now()
            command.archived = True
            command.archived_at = command.completed_at
            command.save()


    connection.close()  # Close connection after operations

def update_printer_state(printer:Printer, state_values:dict):
    try:
        state_values.pop('current_state') #it's a property
        state = printer.state
        for key, value in state_values.items():
            if hasattr(state, key):
                setattr(state, key, value)
        state.save()
    except Exception as e:
        logging.error(f"Error updating printer state: {e}")
    finally:
        connection.close()  # Close connection after operations


def main():
    config = configparser.ConfigParser()
    config.read('printer.ini')

    try:
        name = config.get('printer', 'name')
        access = config.get('printer', 'access')
        sn = config.get('printer', 'sn')
        ip = config.get('printer', 'ip')
        camera = config.getboolean('printer', 'camera')

        logging.info(f"Configuration: Name={name}, SN={sn}, IP={ip}, Camera={camera}")

    except (configparser.NoSectionError, configparser.NoOptionError) as e:
        logging.error(f"Configuration error: {e}")
        return

    # Initialize and connect to printer
    printer:bl.Printer = bl.Printer(ip_address=ip, access_code=access, serial=sn, camera_thread=camera)
    printer.connect()

    django_printer, created = Printer.objects.get_or_create(
        serial_number=sn,
        defaults={
            'name': name,
            'access_code': access,
            'ip_address': ip,
            'blocked': False  # Default value as per model definition
        }
    )

    if created:
        # If a new printer was created, we need to create an associated PrinterState
        django_printer.save()
        connection.close()  # Close connection after operations
        logging.info(f"Created new printer in database with serial number {sn}")
    else:
        logging.info(f"Found existing printer with serial number {sn}")

    # Process command queue in a loop or as part of your regular operations
    old_json = None
    while True:
        if not printer.get_ready():
            try:
                django_printer.state.current_stage = 256
                django_printer.save()
            except Exception as e:
                logging.error(e)
            continue

        pjson = json.loads(printer.to_json())
        sp = json.dumps(pjson["state"])
        state_values = pjson["state"]
        set_of_values = set(make_hashable(v) for v in pjson["state"].values())
        send_to_api = False

        if old_json is not None:
            if old_json != set_of_values:
                send_to_api = True
        else:
            send_to_api = True

        if send_to_api:
            try:
                django_printer = Printer.objects.get(serial_number=sn)
                update_printer_state(django_printer, state_values)

                logging.info("Printer state updated.")
            except Exception as e:
                logging.error(f"Error updating printer state: {e}")

        old_json = set_of_values

        process_command_queue(printer,django_printer)
        # Here you might want to check printer state or perform other tasks
        time.sleep(5)  # Sleep for a bit to avoid constant polling; adjust as needed


if __name__ == '__main__':
    main()