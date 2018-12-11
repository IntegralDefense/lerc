
import os
import time
import subprocess
import shlex
import pprint
import logging

import lerc_api

logger = logging.getLogger("lerc_control."+__name__)

# Get the working lerc_control directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_directory(hostname, dir_path, profile='default'):

    config = lerc_api.load_config(required_keys=['7za_path', '7za_dir_cmd'])
    section = profile + "_collect"
    _7za_path = config[section]['7za_path']
    _7za_cmd = config[section]['7za_dir_cmd']
    default_client_dir = config['default']['client_working_dir']

    if not os.path.exists(_7za_path):
        if _7za_path[0] == '/':
            _7za_path = BASE_DIR + _7za_path
        else:
            _7za_path = BASE_DIR + '/' + _7za_path

    if not os.path.exists(_7za_path):
        logger.error("'{}' does not exist".format(_7za_path))
        return False

    ls = lerc_api.lerc_session()
    client = ls.check_host(host=hostname)
    if not client:
        logger.info("No LERC with '{}' for hostname".format(hostname))
        return False

    commands = []
    cmd = ls.Download(_7za_path)
    logger.info("Issued CID={} to download 7za.exe.".format(cmd['command_id']))
    commands.append(cmd)

    cmd = ls.Run(_7za_cmd.format(hostname+'_dirOfInterest' , dir_path))
    logger.info("Issued CID={} to run 7za on '{}'".format(cmd['command_id'], dir_path))
    commands.append(cmd)

    outputfile = default_client_dir + '{}_dirOfInterest.7z'.format(hostname)
    upCmd = ls.Upload(outputfile)
    logger.info("Issued CID={} to upload {}_dirOfInterest.7z".format(upCmd['command_id'], hostname))
    logger.info("Waiting for the upload command to reach completion ... ")
    commands.append(ls.wait_for_command(upCmd))

    cmd = ls.Run('Del "{}" && Del 7za.exe'.format(outputfile))
    logger.info("Issued CID={} to to delete '{}' and 7za.exe".format(cmd['command_id'], hostname))
    commands.append(cmd)

    logger.info("Getting result from the control server..".format(hostname))
    if ls.get_results(cid=upCmd['command_id'], file_path='{}_dirOfInterest.7z'.format(hostname)):
        logger.info("Wrote {}_dirOfInterest.7z".format(hostname))
    return commands


def full_collection(hostname, profile='default'):

    config = lerc_api.load_config(profile, required_keys=['client_working_dir'])
    client_workdir = config[profile]['client_working_dir']

    required_keys = ['lr_path', 'extract_cmd', 'collect_cmd', 'output_dir', 'streamline_path']
    collect_profile = profile+"_collect"
    config = lerc_api.load_config(collect_profile, required_keys=required_keys)

    lr_path = config[collect_profile]['lr_path']
    extract_cmd = config[collect_profile]['extract_cmd']
    collect_cmd = config[collect_profile]['collect_cmd']
    output_dir = config[collect_profile]['output_dir']
    streamline_path = config[collect_profile]['streamline_path']

    ls = lerc_api.lerc_session(host=hostname)
    commands = []

    logger.info("Starting full Live Response collection on {}.".format(hostname))

    # for contriving the output filename
    local_date_str_cmd = ls.Run('date /t')
    # Delete any existing LR artifacts
    ls.Run("DEL /S /F /Q lr && rmdir /S /Q lr")
    # download the package
    lr_download = ls.Download(lr_path)
    logger.info("Issued CID={} for client to download {}.".format(lr_download['command_id'], lr_path))
    # extract the package
    result = ls.Run(extract_cmd)
    logger.info("Issued CID={} to extract lr.exe on the host.".format(result['command_id']))
    # run the collection
    collect_command = ls.Run(collect_cmd)
    logger.info("Issued CID={} to run {}.".format(collect_command['command_id'], collect_cmd))
    # finish contriving the output filename
    output_filename = None
    local_date_str_cmd = ls.check_command(local_date_str_cmd['command_id'])
    while True:
        if local_date_str_cmd['status'] == 'COMPLETE':
            dateStr = ls.get_results(cid=local_date_str_cmd['command_id'], return_content=True).decode('utf-8')
            logger.debug("Got date string of '{}'".format(dateStr))
            # Mon 11/19/2018 -> 20181119      
            dateStr = dateStr.split(' ')[1].split('/')
            dateStr =  dateStr[2]+dateStr[0]+dateStr[1]
            # hostname.upper() because streamline.py expects uppercase
            output_filename = hostname.upper() + "." + dateStr + ".7z"
            break
        # wait five seconds before asking the server again
        time.sleep(5)
        local_date_str_cmd = ls.check_command(local_date_str_cmd['command_id'])
    # collect the output file
    upload_command = ls.Upload(client_workdir + output_dir + output_filename)
    logger.info("Issued CID={} to upload output at: '{}'".format(upload_command['command_id'], client_workdir + output_dir + output_filename))
    # Stream back collect.bat output as it comes in
    logger.info("Streaming collect.bat output ... ")
    position = 0
    while True:
        collect_command = ls.check_command(collect_command['command_id'])
        if collect_command['status'] == 'STARTED':
            if collect_command['filesize'] > 0:
                results = ls.get_results(cid=collect_command['command_id'], return_content=True, position=position)
                if len(results) > 0:
                    position += len(results)
                    print(results.decode('utf-8'))
            time.sleep(1)
        elif collect_command['status'] == 'COMPLETE':
            if position < collect_command['filesize']:
                results = ls.get_results(cid=collect_command['command_id'], return_content=True, position=position)
                if len(results) > 0:
                    position += len(results)
                    print(results.decode('utf-8'))
            elif position >= collect_command['filesize']:
                break
        elif collect_command['status'] == 'UNKNOWN' or collect_command['status'] == 'ERROR':
            logger.error("Collect command went to {} state : {}".format(collect_command['status'], pprint.pprint(collect_command)))
            return False
        time.sleep(5)
    logger.info("Waiting for '{}' upload to complete.".format(output_filename))
    upload_command = ls.wait_for_command(upload_command)
    #commands.append(upload_command)
    if upload_command['status'] == 'COMPLETE':
        logger.info("Upload command complete. Telling lerc to delete the output file on the client")
        commands.append(ls.Run('DEL /S /F /Q "{}"'.format(client_workdir + output_dir + output_filename)))

    # finally, stream the collection from the server to the cwd
    logger.info("Streaming {} from server..".format(output_filename))
    ls.get_results(cid=upload_command['command_id'], file_path=output_filename)
    # Call steamline on the 7z lr package
    logger.info("[+] Starting streamline on {}".format(output_filename))
    args = shlex.split(streamline_path + " " + output_filename)
    try:
        subprocess.Popen(args).wait()
        logger.info("[+] Streamline complete")
    except Exception as e:
        logger.error("Exception with Streamline: {}".format(e))

    return True
