===================
Server Installation
===================

#. Start with a clean Ubuntu 18 LTS Server install

#. Git the lerc files in `/opt/`::

    cd /opt && sudo -E git clone https://github.com/IntegralDefense/lerc.git

#. Create lerc user::

    sudo adduser lerc

#. Give the lerc user sudo::

    sudo adduser lerc sudo

#. Give lerc full access to `/opt/lerc`::

    cd /opt && sudo chown -R lerc:lerc lerc

#. Become the lerc user::

    sudo su lerc

#. Run the install script::

    cd /opt/lerc/lerc_server && installer/source_install

#. Chose to either change the default LERC Client group/company name or use the 'default' name::

    Do you wish specify the default client group/company name? The default is 'default'.
    1) Yes
    2) No 

#. Either supply a password for the MySQL DB or let the install script generate one::

    Generate random password for LERC DB user or supply your own?
    1) Generate
    2) Supply

#. Decide how you want to run the LERC server::

    Running the LERC Server with one interface or two? Choose one if you don't know what you want.
     -- One Interface: Both the LERC clients and analysts (control API) will access this server on the same interface.
     -- Two Interfaces: LERC Clients and analysts (control API) will access their features via different interfaces.
    Choose which interface configuration you want:
    1) One
    2) Two

After that completes your LERC server should be running and ready. As part of the installation, LERC Client and LERC Control certificates were generated and placed in the following locations.

Client::

    /opt/lerc/lerc_server/ssl/client/

Control::

    /opt/lerc/lerc_server/ssl/admin/

These certificate files, and the `/opt/lerc/lerc_server/ssl/ca-chain.cert.pem` will be needed to configure the LERC Control and LERC Clients.

As an additional security measure, you can safely remove the `lerc` user from the sudoers file after installation.

===============
LERClient Setup
===============

If you want to build your own client version, feel free. Otherwise, there is a LERC.zip file included in the project repo that contains everything you need to start. 

Download the LERC.zip file and extract it. Then, copy the client certificats that were generated by the server installation into that same directory. Next, edit the config.txt file so that the 'serverurls' variable reflects your LERC server. For example::

    serverurls: https://3.214.24.217/

Run lerc.exe and `tail -f /opt/lerc/lerc_server/logs/server.log` to see the client fetch.

