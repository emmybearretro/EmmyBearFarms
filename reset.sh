#!/bin/bash
rm db.sqlite3

for d in */
do
  module=`realpath $d --relative-to=.`
  echo "clearing $module"
  if [ -d $d/__pycache__ ] ;
  then
    rm -rf $d/__pycache__
  fi

  if [ -d $d/migrations ] ;
  then
    rm -rf $d/migrations/*
    python manage.py makemigrations $module
  fi

done

rm -f "gcode/*"
rm -f "threemf/*"
rm -rf "media/*"
rm -rf "static/"


python manage.py migrate

python manage.py shell << EOF
from bambu.models import Folder  # Adjust the import to match your app's structure

Folder.objects.create(name="default")
EOF

python manage.py shell << EOF
from bambu.models import PredefinedCommand
from bambulabs_api import Printer # Adjust the import to match your app's structure

PredefinedCommand.objects.create(name="Mqtt Dump",can_run_when_blocked=True,command='{"mqtt_dump":{}}',description="Execute the mqtt_dump function of the printer")
PredefinedCommand.objects.create(name="Turn Light On",can_run_when_blocked=True,command='{"turn_light_on":{}}',description="Execute the turn_light_on function of the printer")
PredefinedCommand.objects.create(name="Turn Light Off",can_run_when_blocked=True,command='{"turn_light_off":{}}',description="Execute the turn_light_off function of the printer")
PredefinedCommand.objects.create(name="Gcode",can_run_when_blocked=True,command='{"gcode":{}}',description="Execute the gcode function of the printer")
PredefinedCommand.objects.create(name="Upload File",can_run_when_blocked=False,command='{"upload_file":{}}',description="Execute the upload_file function of the printer")
PredefinedCommand.objects.create(name="Start Print",can_run_when_blocked=False,command='{"start_print":{}}',description="Execute the start_print function of the printer")
PredefinedCommand.objects.create(name="Stop Print",can_run_when_blocked=True,command='{"stop_print":{}}',description="Execute the stop_print function of the printer")
PredefinedCommand.objects.create(name="Pause Print",can_run_when_blocked=True,command='{"pause_print":{}}',description="Execute the pause_print function of the printer")
PredefinedCommand.objects.create(name="Resume Print",can_run_when_blocked=True,command='{"resume_print":{}}',description="Execute the resume_print function of the printer")
PredefinedCommand.objects.create(name="Set Bed Temperature",can_run_when_blocked=True,command='{"set_bed_temperature":{}}',description="Execute the set_bed_temperature function of the printer")
PredefinedCommand.objects.create(name="Home Printer",can_run_when_blocked=False,command='{"home_printer":{}}',description="Execute the home_printer function of the printer")
PredefinedCommand.objects.create(name="Move Z Axis",can_run_when_blocked=False,command='{"move_z_axis":{}}',description="Execute the move_z_axis function of the printer")
PredefinedCommand.objects.create(name="Set Filament Printer",can_run_when_blocked=False,command='{"set_filament_printer":{}}',description="Execute the set_filament_printer function of the printer")
PredefinedCommand.objects.create(name="Set Nozzle Temperature",can_run_when_blocked=True,command='{"set_nozzle_temperature":{}}',description="Execute the set_nozzle_temperature function of the printer")
PredefinedCommand.objects.create(name="Set Print Speed",can_run_when_blocked=True,command='{"set_print_speed":{}}',description="Execute the set_print_speed function of the printer")
PredefinedCommand.objects.create(name="Delete File",can_run_when_blocked=False,command='{"delete_file":{}}',description="Execute the delete_file function of the printer")
PredefinedCommand.objects.create(name="Calibrate Printer",can_run_when_blocked=False,command='{"calibrate_printer":{}}',description="Execute the calibrate_printer function of the printer")
PredefinedCommand.objects.create(name="Load Filament Spool",can_run_when_blocked=True,command='{"load_filament_spool":{}}',description="Execute the load_filament_spool function of the printer")
PredefinedCommand.objects.create(name="Unload Filament Spool",can_run_when_blocked=True,command='{"unload_filament_spool":{}}',description="Execute the unload_filament_spool function of the printer")
PredefinedCommand.objects.create(name="Retry Filament Action",can_run_when_blocked=True,command='{"retry_filament_action":{}}',description="Execute the retry_filament_action function of the printer")
PredefinedCommand.objects.create(name="Skip Objects",can_run_when_blocked=True,command='{"skip_objects":{}}',description="Execute the skip_objects function of the printer")
PredefinedCommand.objects.create(name="Set Part Fan Speed",can_run_when_blocked=True,command='{"set_part_fan_speed":{}}',description="Execute the set_part_fan_speed function of the printer")
PredefinedCommand.objects.create(name="Set Aux Fan Speed",can_run_when_blocked=True,command='{"set_aux_fan_speed":{}}',description="Execute the set_aux_fan_speed function of the printer")
PredefinedCommand.objects.create(name="Set Chamber Fan Speed",can_run_when_blocked=True,command='{"set_chamber_fan_speed":{}}',description="Execute the set_chamber_fan_speed function of the printer")
PredefinedCommand.objects.create(name="Set Auto Step Recovery",can_run_when_blocked=False,command='{"set_auto_step_recovery":{}}',description="Execute the set_auto_step_recovery function of the printer")
#PredefinedCommand.objects.create(name="Vt Tray",can_run_when_blocked=False,command='{"vt_tray":{}}',description="Execute the vt_tray function of the printer")
#PredefinedCommand.objects.create(name="Ams Hub",can_run_when_blocked=False,command='{"ams_hub":{}}',description="Execute the ams_hub function of the printer")
#PredefinedCommand.objects.create(name="Get Chamber Temperature",can_run_when_blocked=True,command='{"get_chamber_temperature":{}}',description="Execute the get_chamber_temperature function of the printer")
#PredefinedCommand.objects.create(name="Get Print Stage",can_run_when_blocked=True,command='{"get_print_stage":{}}',description="Execute the get_print_stage function of the printer")
#PredefinedCommand.objects.create(name="Get Heatbreak Fan Speed",can_run_when_blocked=True,command='{"get_heatbreak_fan_speed":{}}',description="Execute the get_heatbreak_fan_speed function of the printer")
#PredefinedCommand.objects.create(name="Get Cooling Fan Speed",can_run_when_blocked=True,command='{"get_cooling_fan_speed":{}}',description="Execute the get_cooling_fan_speed function of the printer")
#PredefinedCommand.objects.create(name="Get Big Fan1 Speed",can_run_when_blocked=True,command='{"get_big_fan1_speed":{}}',description="Execute the get_big_fan1_speed function of the printer")
#PredefinedCommand.objects.create(name="Get Big Fan2 Speed",can_run_when_blocked=True,command='{"get_big_fan2_speed":{}}',description="Execute the get_big_fan2_speed function of the printer")
#PredefinedCommand.objects.create(name="Get Print Percentage",can_run_when_blocked=True,command='{"get_print_percentage":{}}',description="Execute the get_print_percentage function of the printer")
#PredefinedCommand.objects.create(name="Get Remaining Print Time",can_run_when_blocked=True,command='{"get_remaining_print_time":{}}',description="Execute the get_remaining_print_time function of the printer")
#PredefinedCommand.objects.create(name="Get Ams Status",can_run_when_blocked=True,command='{"get_ams_status":{}}',description="Execute the get_ams_status function of the printer")
#PredefinedCommand.objects.create(name="Get Ams Rfid Status",can_run_when_blocked=True,command='{"get_ams_rfid_status":{}}',description="Execute the get_ams_rfid_status function of the printer")
#PredefinedCommand.objects.create(name="Get Hardware Switch State",can_run_when_blocked=True,command='{"get_hardware_switch_state":{}}',description="Execute the get_hardware_switch_state function of the printer")
#PredefinedCommand.objects.create(name="Get Print Speed Level",can_run_when_blocked=True,command='{"get_print_speed_level":{}}',description="Execute the get_print_speed_level function of the printer")
#PredefinedCommand.objects.create(name="Get Print Error",can_run_when_blocked=True,command='{"get_print_error":{}}',description="Execute the get_print_error function of the printer")
#PredefinedCommand.objects.create(name="Get Lifecycle",can_run_when_blocked=True,command='{"get_lifecycle":{}}',description="Execute the get_lifecycle function of the printer")
#PredefinedCommand.objects.create(name="Get Wifi Signal",can_run_when_blocked=True,command='{"get_wifi_signal":{}}',description="Execute the get_wifi_signal function of the printer")
#PredefinedCommand.objects.create(name="Get Gcode State",can_run_when_blocked=True,command='{"get_gcode_state":{}}',description="Execute the get_gcode_state function of the printer")
#PredefinedCommand.objects.create(name="Get Gcode File Prepare Percentage",can_run_when_blocked=True,command='{"get_gcode_file_prepare_percentage":{}}',description="Execute the get_gcode_file_prepare_percentage function of the printer")
#PredefinedCommand.objects.create(name="Get Queue Number",can_run_when_blocked=True,command='{"get_queue_number":{}}',description="Execute the get_queue_number function of the printer")
#PredefinedCommand.objects.create(name="Get Queue Total",can_run_when_blocked=True,command='{"get_queue_total":{}}',description="Execute the get_queue_total function of the printer")
#PredefinedCommand.objects.create(name="Get Queue Estimated Time",can_run_when_blocked=True,command='{"get_queue_estimated_time":{}}',description="Execute the get_queue_estimated_time function of the printer")
#PredefinedCommand.objects.create(name="Get Queue Status",can_run_when_blocked=True,command='{"get_queue_status":{}}',description="Execute the get_queue_status function of the printer")
#PredefinedCommand.objects.create(name="Get Project Id",can_run_when_blocked=True,command='{"get_project_id":{}}',description="Execute the get_project_id function of the printer")
#PredefinedCommand.objects.create(name="Get Profile Id",can_run_when_blocked=True,command='{"get_profile_id":{}}',description="Execute the get_profile_id function of the printer")
#PredefinedCommand.objects.create(name="Get Task Id",can_run_when_blocked=True,command='{"get_task_id":{}}',description="Execute the get_task_id function of the printer")
#PredefinedCommand.objects.create(name="Get Subtask Id",can_run_when_blocked=True,command='{"get_subtask_id":{}}',description="Execute the get_subtask_id function of the printer")
#PredefinedCommand.objects.create(name="Get Subtask Name",can_run_when_blocked=True,command='{"get_subtask_name":{}}',description="Execute the get_subtask_name function of the printer")
#PredefinedCommand.objects.create(name="Get Gcode File",can_run_when_blocked=True,command='{"get_gcode_file":{}}',description="Execute the get_gcode_file function of the printer")
#PredefinedCommand.objects.create(name="Get Current Stage",can_run_when_blocked=True,command='{"get_current_stage":{}}',description="Execute the get_current_stage function of the printer")
#PredefinedCommand.objects.create(name="Get Print Type",can_run_when_blocked=True,command='{"get_print_type":{}}',description="Execute the get_print_type function of the printer")
#PredefinedCommand.objects.create(name="Get Home Flag",can_run_when_blocked=True,command='{"get_home_flag":{}}',description="Execute the get_home_flag function of the printer")
#PredefinedCommand.objects.create(name="Get Print Line Number",can_run_when_blocked=True,command='{"get_print_line_number":{}}',description="Execute the get_print_line_number function of the printer")
#PredefinedCommand.objects.create(name="Get Print Sub Stage",can_run_when_blocked=True,command='{"get_print_sub_stage":{}}',description="Execute the get_print_sub_stage function of the printer")
#PredefinedCommand.objects.create(name="Get Sdcard Status",can_run_when_blocked=True,command='{"get_sdcard_status":{}}',description="Execute the get_sdcard_status function of the printer")
#PredefinedCommand.objects.create(name="Get Force Upgrade Status",can_run_when_blocked=True,command='{"get_force_upgrade_status":{}}',description="Execute the get_force_upgrade_status function of the printer")
#PredefinedCommand.objects.create(name="Get Production State",can_run_when_blocked=True,command='{"get_production_state":{}}',description="Execute the get_production_state function of the printer")
#PredefinedCommand.objects.create(name="Get Current Layer Number",can_run_when_blocked=True,command='{"get_current_layer_number":{}}',description="Execute the get_current_layer_number function of the printer")
#PredefinedCommand.objects.create(name="Get Total Layer Number",can_run_when_blocked=True,command='{"get_total_layer_number":{}}',description="Execute the get_total_layer_number function of the printer")
#PredefinedCommand.objects.create(name="Get Filament Backup",can_run_when_blocked=True,command='{"get_filament_backup":{}}',description="Execute the get_filament_backup function of the printer")
#PredefinedCommand.objects.create(name="Get Fan Gear Status",can_run_when_blocked=True,command='{"get_fan_gear_status":{}}',description="Execute the get_fan_gear_status function of the printer")
#PredefinedCommand.objects.create(name="Get Calibration Version",can_run_when_blocked=True,command='{"get_calibration_version":{}}',description="Execute the get_calibration_version function of the printer")
#PredefinedCommand.objects.create(name="To Json",can_run_when_blocked=False,command='{"to_json":{}}',description="Execute the to_json function of the printer")
#PredefinedCommand.objects.create(name="Get Camera Frame",can_run_when_blocked=True,command='{"get_camera_frame":{}}',description="Execute the get_camera_frame function of the printer")
#PredefinedCommand.objects.create(name="Get Camera Image",can_run_when_blocked=True,command='{"get_camera_image":{}}',description="Execute the get_camera_image function of the printer")
#PredefinedCommand.objects.create(name="Get Current State",can_run_when_blocked=True,command='{"get_current_state":{}}',description="Execute the get_current_state function of the printer")
#PredefinedCommand.objects.create(name="Get Skipped Objects",can_run_when_blocked=True,command='{"get_skipped_objects":{}}',description="Execute the get_skipped_objects function of the printer")

EOF

export DJANGO_SUPERUSER_PASSWORD="hc"
python manage.py createsuperuser --noinput --username hc --email hc@hc.local


python manage.py makemigrations
python manage.py migrate
python manage.py compilemessages
python manage.py collectstatic
