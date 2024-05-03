==========================
Operations and maintenance
==========================

.. _sec_sh_access_token:

Creating an encrypted access token
==================================
Encrypted access tokens are used to safely transfer the SSL certificate
and the user's API Key from the server to the user. This is especially
important in scenarios where self-signed SSL certificates are used
(medical branding) and where users are not allowed to register on their
own to prevent man-in-the-middle attacks.

An encrypted access token is an encrypted zip file with the suffix
".dcor-access" that contains the server's SSL certificate "server.cert"
and the user's API key "api_key.txt". DCOR-Aid can use such an access token
to automatically setup the server connection.

.. note::

    To create good passwords, you can use this command::

      dd if=/dev/urandom bs=1M count=10 status=none | md5sum | awk '{ print $1 }'

Steps to create an access token:

1. create a CKAN user::

     # set-up the CKAN environment
     source /usr/lib/ckan/default/bin/activate
     export CKAN_INI=/etc/ckan/default/ckan.ini
     # create a user (use a good password)
     ckan user add your_username
     # obtain the API key (if this does not work, you have to login
     # as that user and create an api key)
     ckan user token add user_name token_name
     # write the API key to a text file
     echo eyJ0eXAiOiJKV1QiLC...y5WqA5pCE > api_key.txt
     # copy the public SSL certificate to the current directory
     cp /etc/ssl/certs/fqdn.cert ./server.cert
     # creat the encrypted access token (use a good encryption passoword)
     zip -e your_username.dcor-access api_key.txt server.cert
     # cleanup
     rm api_key.txt server.cert

You should send the file `your_username.dcor-access` to your user. Please
send the encryption password of the access token via a different channel.
Especially in the context of hospitals (i.e. data protection), this is
critical.


.. _sec_sh_encrypted_backup:

Creating an encrypted database backup
=====================================
The CKAN database may contain sensitive information, such as email
addresses, which means that any backup should be encrypted. The
following script should be self-explanatory:

.. literalinclude:: encrypted_database_backup.sh
   :language: bash
