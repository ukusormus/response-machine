"""Configuration management for the server.

This module handles loading and validating configuration from both environment variables
and command line arguments. It provides a single source of truth for all server settings.
"""

import os
import argparse
import logging
from dataclasses import dataclass

CONFIG_METADATA = {
    "port": {
        "env_var": "PORT",
        "type": int,
        "default": 8888,
        "cli_args": ("-p", "--port"),
        "help": "Port to listen on",
    },
    "host": {
        "env_var": "SERVER_HOST",
        "type": str,
        "default": "",
        "cli_args": ("--host",),
        "help": "Host to bind to. Empty string = all interfaces",
    },
    "tls_cert_path": {
        "env_var": "TLS_CERT_PATH",
        "type": str,
        "default": None,
        "cli_args": ("--tls-cert-path",),
        "help": "Path to TLS certificate (or combined private key and certificate) file. Required for HTTPS",
    },
    "tls_key_path": {
        "env_var": "TLS_KEY_PATH",
        "type": str,
        "default": None,
        "cli_args": ("--tls-key-path",),
        "help": "Path to TLS private key file",
    },
    "request_timeout": {
        "env_var": "REQUEST_TIMEOUT_SEC",
        "type": int,
        "default": 7,
        "cli_args": ("--request-timeout",),
        "help": "Request timeout in seconds",
    },
    "request_max_size": {
        "env_var": "REQUEST_MAX_SIZE_MB",
        "type": int,
        "default": 5,
        "cli_args": ("--request-max-size",),
        "help": "Maximum request size in MB",
    },
    "debug": {
        "env_var": "DEBUG",
        "type": bool,
        "default": False,
        "cli_args": ("-v", "--verbose"),
        "help": "Enable debug mode",
    },
    "user_gen_response_prefix": {
        "env_var": "USER_GEN_RESPONSE_PREFIX",
        "type": str,
        "default": "/data/",
        "cli_args": ("--user-gen-response-prefix",),
        "help": "Path prefix for user generated responses",
    },
}


def _parse_bool(val: str) -> bool:
    """Parse a boolean value from various input types."""
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.lower() in ("true", "1", "yes")
    return bool(val)


TYPE_PARSERS = {
    bool: _parse_bool,
    bytes: lambda x: x if isinstance(x, bytes) else str(x).encode(),
    str: str,
    int: int,
}


@dataclass(frozen=True)
class ServerConfig:
    port: int
    host: str
    tls_cert_path: str
    tls_key_path: str | None
    request_timeout: int
    request_max_size: int
    debug: bool
    user_gen_response_prefix: bytes


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="HTTP response machine 🤖")

    for field_name, metadata in CONFIG_METADATA.items():
        if not metadata["cli_args"]:
            continue

        type_parser = TYPE_PARSERS[metadata["type"]]
        env_value = os.getenv(metadata["env_var"])
        default_value = (
            type_parser(env_value) if env_value is not None else metadata["default"]
        )

        default_display = (
            repr(metadata["default"]) if metadata["default"] != "" else "''"
        )
        if metadata["type"] == bool:
            parser.add_argument(
                *metadata["cli_args"],
                action="store_true",
                default=default_value,
                help=f"{metadata['help']} (default: {default_display})",
            )
        else:
            parser.add_argument(
                *metadata["cli_args"],
                type=type_parser,
                default=default_value,
                help=f"{metadata['help']} (default: {default_display})",
            )

    return parser.parse_args()


def load_config() -> ServerConfig:
    """Load and validate configuration from environment and command line arguments."""
    args = parse_args()
    args_dict = vars(args)

    config_dict = {}
    for field_name, metadata in CONFIG_METADATA.items():
        # Try to get value from CLI args first
        cli_arg_name = (
            metadata["cli_args"][-1].lstrip("-").replace("-", "_")
            if metadata["cli_args"]
            else None
        )
        if cli_arg_name and cli_arg_name in args_dict:
            value = args_dict[cli_arg_name]
        else:
            # Fall back to env var
            env_value = os.getenv(metadata["env_var"])
            value = (
                TYPE_PARSERS[metadata["type"]](env_value)
                if env_value is not None
                else metadata["default"]
            )

        config_dict[field_name] = value

    if "request_max_size" in config_dict:
        config_dict["request_max_size"] *= 1024 * 1024

    if "user_gen_response_prefix" in config_dict:
        config_dict["user_gen_response_prefix"] = config_dict["user_gen_response_prefix"].encode("utf-8")


    return ServerConfig(**config_dict)
