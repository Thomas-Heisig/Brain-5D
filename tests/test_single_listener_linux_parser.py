"""Unit tests for the Linux /proc/net/tcp parser used by single listener discovery.

These tests use deterministic fixture text and do NOT require a Linux host.
They validate the hex parsing, state filtering, and port matching logic.
"""

# pyright: reportPrivateUsage=false

from __future__ import annotations

import platform as _platform

import pytest as _pytest

from tests.test_single_listener import (
    _parse_proc_net_tcp,
    _resolve_inode_to_pid,
)

# =========================================================================
# Fixtures: synthetic /proc/net/tcp content
# =========================================================================

PROC_NET_TCP_SAMPLE = """\
  sl  local_address rem_address   st tx_queue rx_queue tr tm->when retrnsmt   uid  timeout inode
   0: 0100007F:1F90 00000000:0000 0A 00000000:00000000 00:00000000 00000000     0        0 12345 1 0000000000000000 100 0 0 10 0
   1: 0100007F:2222 00000000:0000 0A 00000000:00000000 00:00000000 00000000     0        0 12346 1 0000000000000000 100 0 0 10 0
   2: 00000000:0050 00000000:0000 0A 00000000:00000000 00:00000000 00000000     0        0 12347 1 0000000000000000 100 0 0 10 0
"""

PROC_NET_TCP6_SAMPLE = """\
  sl  local_address                         remote_address                        st tx_queue rx_queue tr tm->when retrnsmt   uid  timeout inode
   0: 00000000000000000000000001000000:1F90 00000000000000000000000000000000:0000 0A 00000000:00000000 00:00000000 00000000     0        0 22345 1 0000000000000000 100 0 0 10 0
"""


# =========================================================================
# Test parse_proc_net_tcp
# =========================================================================


def test_parse_proc_net_tcp_finds_port_8080() -> None:
    """Port 8080 (0x1F90) in LISTEN state (0A) should be found."""
    inode_map = _parse_proc_net_tcp(8080, tcp_text=PROC_NET_TCP_SAMPLE)
    assert 12345 in inode_map
    assert len(inode_map[12345]) >= 1


def test_parse_proc_net_tcp_skips_wrong_port() -> None:
    """Port 8081 should not match any entry when only 8080 and 8738 are present."""
    inode_map = _parse_proc_net_tcp(8081, tcp_text=PROC_NET_TCP_SAMPLE)
    assert inode_map == {}


def test_parse_proc_net_tcp_mixed_ipv4_ipv6() -> None:
    """IPv6 loopback listener on the same port should also be discovered."""
    inode_map = _parse_proc_net_tcp(
        8080,
        tcp_text=PROC_NET_TCP_SAMPLE,
        tcp6_text=PROC_NET_TCP6_SAMPLE,
    )
    found_inodes = list(inode_map.keys())
    assert 12345 in found_inodes
    assert 22345 in found_inodes


def test_parse_proc_net_tcp_returns_empty_for_unknown_port() -> None:
    """Port 9999 should return empty dict."""
    inode_map = _parse_proc_net_tcp(9999, tcp_text=PROC_NET_TCP_SAMPLE)
    assert inode_map == {}


def test_parse_proc_net_tcp_empty_input() -> None:
    """Empty /proc/net/tcp content should produce empty result."""
    inode_map = _parse_proc_net_tcp(8080, tcp_text="")
    assert inode_map == {}


def test_parse_proc_net_tcp_port_80() -> None:
    """Port 80 (0x0050) in the sample should be found."""
    inode_map = _parse_proc_net_tcp(80, tcp_text=PROC_NET_TCP_SAMPLE)
    assert 12347 in inode_map


def test_parse_proc_net_tcp_hex_conversion() -> None:
    """Verify hex-to-int conversion for port numbers."""
    inode_map_8080 = _parse_proc_net_tcp(8080, tcp_text=PROC_NET_TCP_SAMPLE)
    inode_map_8738 = _parse_proc_net_tcp(8738, tcp_text=PROC_NET_TCP_SAMPLE)
    inode_map_80 = _parse_proc_net_tcp(80, tcp_text=PROC_NET_TCP_SAMPLE)
    assert 12345 in inode_map_8080
    assert 12346 in inode_map_8738
    assert 12347 in inode_map_80


def test_parse_proc_net_tcp_only_tcp6() -> None:
    """When only tcp6 is provided, IPv6 entries are still found."""
    inode_map = _parse_proc_net_tcp(8080, tcp6_text=PROC_NET_TCP6_SAMPLE)
    assert 22345 in inode_map


# =========================================================================
# Test resolve_inode_to_pid (basic contract — Linux only)
# =========================================================================


def _linux_only():
    """Skip test if not on Linux (no /proc filesystem)."""
    if _platform.system() != "Linux":
        _pytest.skip("/proc filesystem not available on this platform")


def test_resolve_inode_to_pid_returns_none_for_nonexistent_inode() -> None:
    """An inode that no process owns should return None."""
    _linux_only()
    pid = _resolve_inode_to_pid(999999999)
    assert pid is None


def test_resolve_inode_to_pid_with_brain_pid_hint() -> None:
    """Providing a brain_pid hint should not crash (PID likely doesn't exist)."""
    _linux_only()
    pid = _resolve_inode_to_pid(12345, brain_pid=999999)
    assert pid is None or isinstance(pid, int)


def test_resolve_inode_to_pid_negative_inode() -> None:
    """Negative inode should return None."""
    _linux_only()
    pid = _resolve_inode_to_pid(-1)
    assert pid is None
