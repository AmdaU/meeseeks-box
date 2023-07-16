import threading
from time import sleep
from colorama import Fore, Style
from typing import Iterable
from fancy_print import delete_line

_animation_lines = []

_animation_lock = threading.Lock()
_kill_animation = threading.Event()

def _animate():
    # Prints the animation line (and deletes them when necessary)
    last_line_amount = 0
    frame_counter = 0
    while True:
        _animation_lock.acquire()
        lines_copy = _animation_lines.copy()
        _animation_lock.release()
        # if there are less line then before, delete the extra before printing
        diff = len(lines_copy) - last_line_amount
        if diff < 0:
            delete_line(diff)
        # remember current amount of lines for next time
        last_line_amount = len(lines_copy)
        for line in lines_copy:
            animation = line.get("animation")
            animation_frame = animation[frame_counter % len(animation)]
            color = line["color"]
            print(color + animation_frame + Style.RESET_ALL + " " + line["text"])
        if _kill_animation.is_set():
            break
        sleep(0.1)
        delete_line(len(lines_copy))
        frame_counter +=1

animation_thread = threading.Thread(target=_animate)

def loading_animation_dec(text: str,
                          animation: Iterable = "⣾⣽⣻⢿⡿⣟⣯⣷",
                          color: str = Fore.BLUE,
                          text_format:Iterable | None = None,
                          trace: str | None = None,
                          trace_color: str = Fore.GREEN,
                          trace_animation: Iterable = "⣿",
                          trace_format:Iterable | None = None,
                          trace_failed: str = "Failed",
                          trace_color_failed: str = Fore.RED,
                          trace_animation_failed: Iterable = None,
                          trace_format_failed: Iterable | None = None):
    """
    Make a loading animation while `task` runs.

    Add a line to the console with the format 'animation + text'. Can also
    leave a 'trace' when the task is done running (instead of disappearing)

    text: text to be displayed next to the animation
    animation: Itarable containing all successive 'frames' of the animation
    color: ANSI escape code to set the color of the animation
    text_format: `text` can list of arguments that will be used to format the
        text of the animation. The element of that list will be passed in eval
        as to potentially grab local variable such as the arguments passed to
        `task`.
        Ex:
            @loading_animation_dec('Exectuing task with args: {}', text_format = ['args'])
            def random_task(foo, bar):
                pass

        will print the arguments passed to 'task'
    trace_*: same thing as the regular versions but for the 'trace' that will be
        left once the task is done
    """
    if trace_animation_failed is None:
        trace_animation_failed = trace_animation
    def decorator(task):
        def wrapper(*args, **kwargs):
            global animation_thread
            # formating the text
            if text_format:
                values = []
                for i in text_format:
                    values.append(eval(i))

                loading_text = text.format(*values)
            else:
                loading_text = text
            # formatting the trace text
            if trace_format and trace:
                values = []
                for i in text_format:
                    values.append(eval(i))
                trace_text = trace.format(*values)
            else:
                trace_text = trace

            # Make sure the kill animation flag is not set and starts the
            # animation thread if necessary
            if not animation_thread.is_alive():
                    _kill_animation.clear()
                    animation_thread.start()

            # Adds an 'animation line' relevent to the current task
            _animation_lock.acquire()
            anim_id = len(_animation_lines) + 1
            line = {
                "text":loading_text,
                "id": anim_id,
                "color":color,
                "done": False,
                "animation": animation,
                "thread_id": threading.current_thread().ident
            }
            _animation_lines.append(line)
            _animation_lines.sort(key=lambda e: e["thread_id"])
            _animation_lock.release()

            # actually runs the taks
            Failed = False
            Ex = None
            result = None
            try:
                result = task(*args, **kwargs)
            except Exception as e:
                Failed=True
                Ex = e

            if Failed:
                if trace_format_failed:
                    values = []
                    for i in trace_format_failed:
                        values.append(eval(i))

                    trace_text_failed = trace_failed.format(*values)
                else:
                    trace_text_failed = trace_failed


            # Either remove the animation line or replaces it with the trace
            _animation_lock.acquire()
            index = _animation_lines.index(line)
            if trace_failed and Failed:
                _animation_lines[index] = {
                    "text":trace_text_failed,
                    "id": anim_id,
                    "color":trace_color_failed,
                    "done": True,
                    "animation": trace_animation_failed,
                    "thread_id": threading.current_thread().ident
                }
            elif trace and not Failed:
                _animation_lines[index] = {
                    "text":trace_text,
                    "id": anim_id,
                    "color":trace_color,
                    "done": True,
                    "animation": trace_animation,
                    "thread_id": threading.current_thread().ident
                }

            else:
                _animation_lines.remove(line)

            # Check if all animated task are done
            remaning_animations = not all([line.get('done') for line in _animation_lines])
            _animation_lock.release()

            if not remaning_animations:
                _kill_animation.set()
                animation_thread.join()
                animation_thread = threading.Thread(target=_animate)

                _animation_lock.acquire()
                for line in _animation_lines[::-1]:
                    _animation_lines.remove(line)
                _animation_lock.release()

            # Except(Ex)
            return result
        return wrapper
    return decorator
