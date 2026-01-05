"""Provides filtering logic for server targets."""

load("@bazel_skylib//lib:paths.bzl", "paths")

def filter_server_builtin_modules(x):
    if paths.basename(x) in [
        "virtio_balloon.ko",
        "virtio_blk.ko",
        "virtio_console.ko",
        "virtio_pci.ko",
        "virtio_pci_legacy_dev.ko",
        "virtio_pci_modern_dev.ko",
        "vmw_vsock_virtio_transport.ko",
        "zram.ko",
        "zsmalloc.ko",
    ]:
        return None
    return paths.basename(x)
