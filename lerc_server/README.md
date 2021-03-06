# Live Endpoint Response Client Server


## Install

Start with a fresh Ubuntu 18 server install.

#1. Get the stuff

    cd /opt && sudo -E git clone https://github.com/IntegralDefense/lerc.git

#2. Create lerc user::

    sudo adduser lerc

#3. Give the lerc user sudo::

    sudo adduser lerc sudo

#4. Give lerc full access to `/opt/lerc`::

    cd /opt && sudo chown -R lerc:lerc lerc

#5. Become the lerc user::

    sudo su lerc

#6. Run the install script::

    cd /opt/lerc/lerc_server && installer/source_install

#7. Chose to either change the default LERC Client group/company name or use the 'default' name::

    Do you wish specify the default client group/company name? The default is 'default'.
    1) Yes
    2) No

#8. Either supply a password for the MySQL DB or let the install script generate one::

    Generate random password for LERC DB user or supply your own?
    1) Generate
    2) Supply

#9. Decide how you want to run the LERC server::

    Running the LERC Server with one interface or two? Choose one if you don't know what you want.
     -- One Interface: Both the LERC clients and analysts (control API) will access this server on the same interface.
     -- Two Interfaces: LERC Clients and analysts (control API) will access their features via different interfaces.
    Choose which interface configuration you want:
    1) One
    2) Two

After that completes your LERC server should be running and ready. As part of the installation, LERC Client and LERC Control certificates were generated and placed in the following locations.

Client:

    /opt/lerc/lerc_server/ssl/client/

Control:

    /opt/lerc/lerc_server/ssl/admin/

The client and control certs are generated by the server install script.
