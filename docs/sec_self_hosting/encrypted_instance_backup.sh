#!/bin/bash
#
# Create an encrypted database backup on /data/encrypted_db_dumps.
# You have to import a private key with `gpg --import dcor_public.key`
# and trust it with `gpg --edit-key 8FD98B2183B2C228` (command 'trust').
# Then also make sure that the key id in the example below is correct.
#
# Put this script in /root/scripts, make it executable and add the
# following cron job:
#
# # create encrypted database backups every day
# 2 0 * * * root /root/scripts/encrypted_instance_backup.sh > /dev/null
#
source /usr/lib/ckan/default/bin/activate
export CKAN_INI=/etc/ckan/default/ckan.ini
dcor encrypted-instance-backup --key-id 8FD98B2183B2C228
