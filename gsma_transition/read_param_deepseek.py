import argparse
import logging
import re
import platform
from pathlib import Path
from typing import Dict, List, Optional, Pattern

# Constants
DEFAULT_SEVERITY = "CRITICAL"
CONFIG_FILES = {
    "log": "zbx_logMonitor.conf",
    "process": "zbx_processMonitor.conf",
    "network": "zbx_networkMonitor.conf",
    "eventlog": "zbx_eventLogMonitor.conf",
    "customscript": "zbx_customScriptMonitor.conf",
    "url": "zbx_urlMonitor.conf",
}
SEVERITY_MAP = {
    "W": "WARNING",
    "M": "WARNING",
    "C": "CRITICAL",
    "F": "FATAL",
}

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def check_os() -> str:
    """Determine the current operating system type.

    Returns:
        str: One of 'LINUX', 'WINDOWS', or 'UNIX' (uppercase).
    """
    return platform.system().upper()


def check_dir() -> Path:
    """Ensure Zabbix scripts directory exists based on OS.

    Returns:
        Path: Path to the Zabbix scripts directory.
    """
    os_type = check_os()
    zabbix_dir = Path("/etc/zabbix/scripts" if os_type != "WINDOWS" else "C:\\zabbix\\scripts")
    zabbix_dir.mkdir(parents=True, exist_ok=True)
    return zabbix_dir


def read_param_files(directory_path: str) -> Optional[Dict[str, List[str]]]:
    """Read and parse all .param files in the specified directory.

    Args:
        directory_path: Path to the directory containing .param files.

    Returns:
        Dictionary with filenames (without .param) as keys and file contents as values.
        Returns None if directory doesn't exist or has no .param files.
    """
    dir_path = Path(directory_path)
    if not dir_path.is_dir():
        logger.error(f"Directory does not exist: {dir_path}")
        return None

    param_files = list(dir_path.glob("*.param"))
    if not param_files:
        logger.warning(f"No .param files found in: {dir_path}")
        return None

    key_name_pattern: Pattern[str] = re.compile(r"^[Kk]\d{2}_")
    file_contents_dict: Dict[str, List[str]] = {}

    for file_path in param_files:
        try:
            key_name = key_name_pattern.sub("", file_path.stem)  # Remove prefix from filename
            with open(file_path, "r") as file:
                contents = [
                    line.strip()
                    for line in file
                    if line.strip() and not line.startswith("#")
                ]
                if contents:
                    file_contents_dict[key_name] = contents
        except IOError as e:
            logger.error(f"Error reading {file_path}: {e}")

    logger.info(f"Processed {len(file_contents_dict)} .param files")
    return file_contents_dict


def append_to_zabbix_config_file(
    config_file: str, contents_list: List[str], scripts_dir: Optional[Path] = None
) -> None:
    """Write lines to a Zabbix configuration file.

    Args:
        config_file: Target configuration filename (e.g., zbx_logMonitor.conf).
        contents_list: List of strings to write to the file.
        scripts_dir: Optional pre-determined scripts directory.
    """
    scripts_dir = scripts_dir or check_dir()
    file_path = scripts_dir / config_file

    try:
        with open(file_path, "a") as f:
            f.write("\n".join(contents_list) + "\n")
        logger.debug(f"Appended {len(contents_list)} lines to {file_path}")
    except IOError as e:
        logger.error(f"Failed to write to {file_path}: {e}")


def process_log_monitor_params(params_dict: Dict[str, List[str]], scripts_dir: Path) -> None:
    """Process LogMonitor and LogMonitor_detail parameters."""
    log_contents = params_dict.get("LogMonitor.param")
    detail_contents = params_dict.get("LogMonitor_detail.param")

    if not log_contents or not detail_contents:
        logger.warning("Missing LogMonitor or LogMonitor_detail.param files")
        return

    # Build file alias to path mapping
    files_dict = {}
    for line in log_contents:
        try:
            alias, path = line.split(";")[:2]
            files_dict[alias] = path
        except ValueError:
            logger.warning(f"Skipping malformed LogMonitor line: {line}")

    # Process detail lines
    output_lines = []
    for line in detail_contents:
        try:
            tag, alias, keyword, severity = line.split(";")[:4]
            file_path = files_dict.get(alias)
            if not file_path:
                logger.warning(f"Unknown file alias '{alias}' in line: {line}")
                continue

            dir_path, file_name = Path(file_path).parent, Path(file_path).name
            output_lines.append(";".join([tag, str(dir_path), file_name, keyword, severity]))
        except ValueError:
            logger.warning(f"Skipping malformed LogMonitor_detail line: {line}")

    if output_lines:
        append_to_zabbix_config_file(CONFIG_FILES["log"], output_lines, scripts_dir)


def process_process_params(params_dict: Dict[str, List[str]], scripts_dir: Path) -> None:
    """Process process monitoring parameters."""
    process_contents = params_dict.get("process.param")
    if not process_contents:
        logger.warning("Missing process.param file")
        return

    output_lines = []
    for line in process_contents:
        try:
            elements = line.split(";")
            if len(elements) < 8:
                logger.warning(f"Skipping incomplete process line: {line}")
                continue

            tag, name, user, count, severity = elements[0], elements[1], elements[2], elements[3], elements[7]
            mapped_severity = SEVERITY_MAP.get(severity, "UNKNOWN")
            output_lines.append(";".join([f"{tag}_{name}", name, user, count, mapped_severity]))
        except Exception as e:
            logger.error(f"Error processing line '{line}': {e}")

    if output_lines:
        append_to_zabbix_config_file(CONFIG_FILES["process"], output_lines, scripts_dir)


def process_network_port_params(params_dict: Dict[str, List[str]], scripts_dir: Path) -> None:
    """Process network port monitoring parameters."""
    os_type = check_os()
    param_file = "PortCheck.param" if os_type == "WINDOWS" else "networkport.param"
    network_contents = params_dict.get(param_file)

    if not network_contents:
        logger.warning(f"Missing {param_file} file")
        return

    output_lines = []
    for line in network_contents:
        try:
            elements = line.split(";")
            if os_type == "WINDOWS":
                if len(elements) < 3:
                    logger.warning(f"Skipping incomplete Windows port line: {line}")
                    continue
                tag, hostname, port = elements[0], elements[1], elements[2]
            else:
                if len(elements) < 4:
                    logger.warning(f"Skipping incomplete Unix port line: {line}")
                    continue
                tag, hostname, port = f"{elements[0]}_{elements[1]}", elements[2], elements[3]

            output_lines.append(";".join([tag, hostname, port, DEFAULT_SEVERITY]))
        except Exception as e:
            logger.error(f"Error processing line '{line}': {e}")

    if output_lines:
        append_to_zabbix_config_file(CONFIG_FILES["network"], output_lines, scripts_dir)


def process_event_log_params(params_dict: Dict[str, List[str]], scripts_dir: Path) -> None:
    """Process Windows event log monitoring parameters."""
    eventlog_contents = params_dict.get("EventLog.param")
    if not eventlog_contents:
        logger.warning("Missing EventLog.param file")
        return

    output_lines = []
    for line in eventlog_contents:
        try:
            elements = line.split(";")
            if len(elements) < 7:
                logger.warning(f"Skipping incomplete event log line: {line}")
                continue

            tag = elements[0]
            logfile = elements[1].replace("=", "")
            level = elements[2]
            source = elements[3].replace("=", "")
            event_id = elements[4].replace("=", "")
            severity = elements[6]

            output_lines.append(";".join([tag, logfile, "", level, source, event_id, severity]))
        except Exception as e:
            logger.error(f"Error processing line '{line}': {e}")

    if output_lines:
        append_to_zabbix_config_file(CONFIG_FILES["eventlog"], output_lines, scripts_dir)


def process_custom_script_params(params_dict: Dict[str, List[str]], scripts_dir: Path) -> None:
    """Process custom script monitoring parameters."""
    script_contents = params_dict.get("CustomScript.param")
    if not script_contents:
        logger.warning("Missing CustomScript.param file")
        return

    output_lines = []
    for line in script_contents:
        try:
            tag, script_path = line.split(";")[:2]
            output_lines.append(";".join([tag, script_path, DEFAULT_SEVERITY]))
        except ValueError:
            logger.warning(f"Skipping malformed custom script line: {line}")

    if output_lines:
        append_to_zabbix_config_file(CONFIG_FILES["customscript"], output_lines, scripts_dir)


def process_url_params(params_dict: Dict[str, List[str]], scripts_dir: Path) -> None:
    """Process URL monitoring parameters."""
    url_contents = params_dict.get("URLMonitor.param")
    if not url_contents:
        logger.warning("Missing URLMonitor.param file")
        return

    output_lines = []
    for line in url_contents:
        try:
            elements = line.split(";")
            if len(elements) < 5:
                logger.warning(f"Skipping incomplete URL line: {line}")
                continue

            tag, url, servername, severity = elements[0], elements[1], elements[3], elements[4]
            output_lines.append(";".join([tag, url, servername, severity]))
        except Exception as e:
            logger.error(f"Error processing line '{line}': {e}")

    if output_lines:
        append_to_zabbix_config_file(CONFIG_FILES["url"], output_lines, scripts_dir)


def convert_gsma_param(directory_path: str) -> None:
    """Main function to process all GSMA parameter files."""
    scripts_dir = check_dir()
    params_dict = read_param_files(directory_path)
    if not params_dict:
        return

    # Process each parameter type
    if all(key in params_dict for key in ["LogMonitor.param", "LogMonitor_detail.param"]):
        process_log_monitor_params(params_dict, scripts_dir)

    if "process.param" in params_dict:
        process_process_params(params_dict, scripts_dir)

    if "networkport.param" in params_dict or "PortCheck.param" in params_dict:
        process_network_port_params(params_dict, scripts_dir)

    if "EventLog.param" in params_dict:
        process_event_log_params(params_dict, scripts_dir)

    if "CustomScript.param" in params_dict:
        process_custom_script_params(params_dict, scripts_dir)

    if "URLMonitor.param" in params_dict:
        process_url_params(params_dict, scripts_dir)


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Process GSMA parameters and save to Zabbix configuration."
    )
    parser.add_argument(
        "directory_path", help="Path to the directory containing .param files"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    convert_gsma_param(args.directory_path)
