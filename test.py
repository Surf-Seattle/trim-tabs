def get_differences(srt):
    run_times = sorted(list(set(srt.values())))
    run_times_adjusted = []
    while run_times:
        run_times_adjusted.append(run_times.pop(0))
        run_times = [rt_ - run_times_adjusted[-1] for rt_ in run_times]
    return run_times_adjusted


def grouped_runtimes(surface_runtimes):
    run_blocks = []
    for runtime_difference in get_differences(surface_runtimes):
        run_blocks.append(
            (
                runtime_difference,
                [
                    surface
                    for surface, surface_runtime in surface_runtimes.items()
                    if surface_runtime >= runtime_difference
                ]
            )
        )
        surface_runtimes = {
            surface: surface_runtime-runtime_difference
            for surface, surface_runtime in surface_runtimes.items()
        }
    turn_off_after = []
    for i, run_block in enumerate(run_blocks):
        try:
            turn_off_after.append(
                (
                    run_block[0],
                    set(run_block[1]) - set(run_blocks[i+1][1])
                )
            )
        except Exception:
            turn_off_after.append(run_block)
    return turn_off_after

print(grouped_runtimes({'PORT': 3, 'CENTER': 5, 'STARBOARD': 7}))