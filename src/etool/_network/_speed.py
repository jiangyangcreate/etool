"""Cross-platform speed benchmarks (no GPU / no CUDA)."""

from __future__ import annotations

import tempfile
import time
import os


class ManagerSpeed:
    results: dict = {}

    @classmethod
    def network(cls) -> str:
        """Test network speed (requires optional speedtest-cli)."""
        try:
            import speedtest  # type: ignore[import-untyped]
        except ImportError:
            msg = "speedtest not installed; pip install speedtest-cli"
            cls.results["network"] = None
            return msg

        try:
            st = speedtest.Speedtest(secure=True, source_address=None)
            st.get_best_server()

            download_speed = st.download() / 1_000_000
            upload_speed = st.upload() / 1_000_000
            ping = st.results.ping

            cls.results["network"] = {
                "download_speed": f"{download_speed:.2f} Mbps",
                "upload_speed": f"{upload_speed:.2f} Mbps",
                "ping": f"{ping:.2f} ms",
            }
            info = (
                f"\n network test result:\n"
                f"download speed: {cls.results['network']['download_speed']}\n"
                f"upload speed: {cls.results['network']['upload_speed']}\n"
                f"ping: {cls.results['network']['ping']}\n"
            )
            print(info)
            return info
        except Exception as e:
            cls.results["network"] = None
            out = f"network test failed: {e}"
            print(out)
            return out

    @classmethod
    def disk(cls, file_size_mb: int = 100) -> str:
        """Test disk read and write speed (stdlib + temp file)."""
        try:
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            file_path = temp_file.name

            data = os.urandom(1024 * 1024)
            start_time = time.time()
            for _ in range(file_size_mb):
                temp_file.write(data)
            temp_file.close()

            write_time = time.time() - start_time
            write_speed = file_size_mb / write_time

            start_time = time.time()
            with open(file_path, "rb") as f:
                while f.read(1024 * 1024):
                    pass
            read_time = time.time() - start_time
            read_speed = file_size_mb / read_time

            os.unlink(file_path)

            cls.results["disk"] = {
                "read_speed": f"{read_speed:.2f} MB/s",
                "write_speed": f"{write_speed:.2f} MB/s",
            }
            info = (
                f"\n disk test result:\n"
                f"read speed: {cls.results['disk']['read_speed']}\n"
                f"write speed: {cls.results['disk']['write_speed']}\n"
            )
            print(info)
            return info
        except Exception as e:
            cls.results["disk"] = None
            out = f"disk test failed: {e}"
            print(out)
            return out

    @classmethod
    def memory(cls, size_mb: int = 1000) -> str:
        """Memory read/write throughput using stdlib bytes (no NumPy)."""
        try:
            chunk = 1024 * 1024
            n = max(1, size_mb)
            start = time.time()
            buf = bytearray()
            for _ in range(n):
                buf += os.urandom(chunk)
            write_time = time.time() - start
            write_speed = (n * chunk / (1024 * 1024)) / write_time

            start = time.time()
            s = 0
            for i in range(0, len(buf), chunk):
                s += sum(buf[i : i + chunk])
            read_time = time.time() - start
            read_speed = (n * chunk / (1024 * 1024)) / read_time

            info = (
                f"\n memory test result:\n"
                f"read speed: {read_speed:.2f} MB/s\n"
                f"write speed: {write_speed:.2f} MB/s"
            )
            print(info)
            return info
        except Exception as e:
            return f"memory test failed: {e}"
