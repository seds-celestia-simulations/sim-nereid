import time as CPUTime


class Profiler:
    def __init__(self):
        self.timings = {}
        self.start_time = None
        self.frame_counter = 0

    def start(self):
        self.start_time = CPUTime.perf_counter()

    def stop(self, name):
        elapsed = (CPUTime.perf_counter() - self.start_time) * 1000
        self.timings[name] = (
            0.95 * self.timings.get(name, elapsed)
            + 0.05 * elapsed
        )

    def display(self):
        self.frame_counter += 1

        if self.frame_counter % 10 == 0:
            return

        total = sum(self.timings.values())

        print("\n------ Frame Profile ------")
        for name, t in sorted(self.timings.items()):
            pct = 100 * t / total if total else 0
            print(f"{name:<20} {t:7.3f} ms ({pct:5.1f}%)")

        print(f"\nTotal : {total:.3f} ms")
        print(f"Frame : {total:.2f} ms")
        print(f"FPS   : {1000/total:.1f}")